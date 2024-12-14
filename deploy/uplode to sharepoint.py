import os
import csv
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext

def upload_csv_to_sharepoint(items, fieldnames, filename, site_url, folder_path, username, password):
    """
    Write a CSV file, upload it to a SharePoint site, and create the folder path if it doesn't exist.

    Args:
        items (list): List of dictionaries containing the data.
        fieldnames (list): List of field names for the CSV.
        filename (str): The name of the local CSV file to be created.
        site_url (str): The URL of the SharePoint site.
        folder_path (str): The folder path in the SharePoint document library.
        username (str): The username for SharePoint authentication.
        password (str): The password for SharePoint authentication.

    Returns:
        bool: True if upload was successful, False otherwise.
    """
    try:
        # Ensure local directories exist
        local_folder = os.path.dirname(filename)
        if local_folder:
            os.makedirs(local_folder, exist_ok=True)

        # Write the CSV file locally
        with open(filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(items)
        
        print(f"Local CSV file {filename} created successfully.")

        # Authenticate with SharePoint
        auth_context = AuthenticationContext(site_url)
        if not auth_context.acquire_token_for_user(username, password):
            raise Exception(f"Failed to authenticate: {auth_context.get_last_error()}")

        ctx = ClientContext(site_url, auth_context)

        # Ensure the folder path exists, create if necessary
        folder_path = folder_path.strip("/")
        folder_levels = [f for f in folder_path.split("/") if f]
        print(f"Folder levels: {folder_levels}")

        current_path = ""
        for i, folder in enumerate(folder_levels):
            if i == 0:
                current_path = f"/{folder}"
            else:
                current_path = f"{current_path}/{folder}"
            print(f"Processing folder: {current_path}")
            try:
                existing_folder = ctx.web.get_folder_by_server_relative_url(current_path)
                ctx.load(existing_folder)
                ctx.execute_query()
                print(f"Folder exists: {current_path}")
            except Exception as e:
                print(f"Folder not found: {current_path}. Creating...")
                if i > 0:
                    parent_folder_path = "/".join(folder_levels[:i])
                    parent_folder = ctx.web.get_folder_by_server_relative_url(f"/{parent_folder_path}")
                    ctx.load(parent_folder)
                    ctx.execute_query()
                    parent_folder.add_folder(folder).execute_query()
                    print(f"Folder created: {current_path}")
                else:
                    print(f"Cannot create library: {current_path}. Please ensure the library exists.")
                    return False

        # Upload the file to the SharePoint folder
        with open(filename, "rb") as file:
            target_folder = ctx.web.get_folder_by_server_relative_url(folder_path)
            target_folder.upload_file(os.path.basename(filename), file.read())
            ctx.execute_query()
            print(f"File {filename} uploaded to SharePoint at {folder_path}.")
        
        return True
    except Exception as e:
        print(f"Error uploading CSV to SharePoint: {e}")
        return False

# Example usage
items = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30}
]
fieldnames = ["name", "age"]
filename = "data/output2.csv"
site_url = "https://yoursharepointsite.sharepoint.com/sites/yoursite"
folder_path = "Shared Documents/YourFolder"
username = "your_username@yourdomain.com"
password = "your_password"
upload_csv_to_sharepoint(items, fieldnames, filename, site_url, folder_path, username, password)