
import os
import pandas as pd
from charset_normalizer import detect

def remove_duplicates_from_csv(file_path: str, unique_column: str) -> None:
    """
    Remove duplicate rows from a CSV file based on a unique column, handling any encoding type.

    Args:
        file_path (str): The path to the CSV file.
        unique_column (str): The column to use for filtering unique rows.
    """
    try:
        # Check if file is writable
        if not os.access(file_path, os.W_OK):
            raise PermissionError(f"Write permission denied for file: {file_path}")

        # Detect file encoding
        with open(file_path, 'rb') as file:
            encoding = detect(file.read())['encoding']
            print(f"Detected encoding: {encoding}")

        # Read CSV file with detected encoding
        df = pd.read_csv(file_path, encoding=encoding, on_bad_lines='skip', low_memory=False)

        # Validate column existence
        if unique_column not in df.columns:
            raise ValueError(f"Column '{unique_column}' does not exist in the CSV file.")

        # Remove duplicates and write back
        df_cleaned = df.drop_duplicates(subset=unique_column, keep='last')
        df_cleaned.to_csv(file_path, index=False, encoding=encoding)
        print(f"Duplicates removed based on '{unique_column}'. Cleaned data written to {file_path}.")
    except PermissionError as perm_error:
        print(f"Permission error: {perm_error}")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    remove_duplicates_from_csv('output.csv', unique_column='vulnUUID')
