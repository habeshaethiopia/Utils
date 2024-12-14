import pandas as pd

def remove_duplicates_from_csv(file_path: str) -> None:
    """
    Remove duplicate rows from a CSV file.

    Args:
        file_path (str): The path to the CSV file.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Remove duplicates
        df_cleaned = df.drop_duplicates()

        # Write the cleaned data back to the CSV file
        df_cleaned.to_csv(file_path, index=False)

        print(f"Duplicates removed. Cleaned data written to {file_path}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
remove_duplicates_from_csv('output.csv')