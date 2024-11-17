import json
import csv
import os
with open("test.json", mode="r") as file:
    response_json = json.load(file)
    csv_file_path = "./output.csv"
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Define headers based on expected structure
            headers = ["pluginID", "severity_id", "severity_name", "severity_description", "hasBeenMitigated", "acceptRisk"]
            writer.writerow(headers)
    if 200== 200:
        data = response_json
        results = data.get("response", {}).get("results", [])

        # Write each result to the CSV
        with open(csv_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            for item in results:
                # Flatten the nested severity dictionary for CSV compatibility
                row = [
                    item.get("pluginID"),
                    item.get("severity", {}).get("id"),
                    item.get("severity", {}).get("name"),
                    item.get("severity", {}).get("description"),
                    item.get("hasBeenMitigated"),
                    item.get("acceptRisk"),
                ]
                writer.writerow(row)
        
        # print(f"Batch {start_offset}-{end_offset} written to {csv_file_path}")

    # else:
        # print("Error:", response.status_code, response.text)
        # break

    # Move to the next batch
    # start_offset += batch_size