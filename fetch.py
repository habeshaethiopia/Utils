import subprocess
import json
import csv

# Define the PowerShell command
powershell_command = """
$headers = @{ 
    "accept" = "application/json"; 
    "Authorization" = "FortifyToken xxxx" 
}

$response = Invoke-WebRequest -Uri 'domain/api/v2/applications' -Headers $headers -Method GET
$response.Content
"""

# Executethe Powershsell command
process = subprocess.run(
    ["powershell", "-Command", powershell_command], capture_output=True, text=True
)

# Check if the command was successful
if process.returncode == 0:
    print("Status Code:", process.returncode)

    # Parse the JSON response
    response_json = json.loads(process.stdout)
    
    # Extract items from the response 
    items = response_json.get("items", [])

    # Specify the CSV file name 
    csv_file_name = "applications.csv"

   
    with open(csv_file_name, mode="w", newline="") as csv_file:
        fieldnames = (
            items[0].keys() if items else []
        )  # Get the keys from the first item as fieldnames
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()  # Write the header
        for item in items:
            writer.writerow(item)  # Write each item's data

    print(f"Data has been written to {csv_file_name}")
else:
    print("Failed to execute command:", process.stderr)
