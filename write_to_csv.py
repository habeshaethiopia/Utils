import os
import csv
def write_to_csv(items, fieldnames, filename):
    """
    Write data to a CSV file. If the file exists, append rows without writing headers.
    If the file does not exist, create it and write headers.

    Args:
        items (list): List of dictionaries containing the data.
        fieldnames (list): List of field names for the CSV.
        filename (str): The name of the CSV file.

    Returns:
        bool: True if writing was successful, False otherwise.
    """
    try:
        # Ensure the directory exists
        folder = os.path.dirname(filename)
        if folder:  # Only create directory if folder is specified
            os.makedirs(folder, exist_ok=True)

        # Check if the file already exists
        file_exists = os.path.isfile(filename)

        # Write to the CSV file
        with open(filename, mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write header only if the file does not exist
            if not file_exists:
                writer.writeheader()

            # Write each item as a row
            for item in items:
                writer.writerow(item)

        print(f"Data successfully written to {filename}")
        return True
    except Exception as e:
        print(f"Failed to write data to {filename}: {e}")
        return False


