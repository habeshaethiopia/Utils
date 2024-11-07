import subprocess
import json
import csv

# Define the PowerShell command
powershell_command = """
$headers = @{ 
    "accept" = "application/json"; 
    "Authorization" = "FortifyToken xxxx" 
}

# Bypass SSL/TLS certificate validation
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }

$response = Invoke-WebRequest -Uri 'domain/api/v2/applications' -Headers $headers -Method GET
$response.Content
"""

def process():
    try:
        # Execute the PowerShell command
        result = subprocess.run(
            ["powershell", "-Command", powershell_command],
            capture_output=True,
            text=True,
            check=True,
        )

        # Check if the command was successful
        if result.returncode == 0:
            # print("Status Code:", result.returncode)
            # print("STDOUT:", result.stdout)  # Print the raw JSON response
            
            # Parse the JSON response
            if result.stdout.strip():  # Ensure stdout is not empty
                response_json = json.loads(result.stdout)

                # Extract items from the response
                items = response_json.get("items", [])

                # Specify the CSV file name
                csv_file_name = "applications.csv"

                with open(csv_file_name, mode="w", newline="") as csv_file:
                    fieldnames = items[0].keys() if len(items) > 0 else []  # Get keys from the first item as fieldnames
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()  # Write the header
                    for item in items:
                        writer.writerow(item)  # Write each item's data

                print(f"Data has been written to {csv_file_name}")
            else:
                print("No output from PowerShell command.")
        else:
            print(f"Failed to execute command: {result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from the command output.")
if __name__=="__main__":
    process()