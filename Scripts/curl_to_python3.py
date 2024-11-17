import json
import csv
from datetime import datetime
from collections import defaultdict

# Read the JSON file
with open('res2.json', 'r') as f:
    data = json.load(f)
# Group versions by project
project_versions = defaultdict(list)
for version in data['data']:
    project_id = version['project']['id']
    project_versions[project_id].append(version)

# Find latest version for each project
latest_projects = {}
for project_id, versions in project_versions.items():
    latest_version = sorted(
        versions,
        key=lambda x: datetime.strptime(x['creationDate'], "%Y-%m-%dT%H:%M:%S.%f%z"),
        reverse=True
    )[0]
    latest_projects[project_id] = latest_version

# Define the fields we want to extract
fields = [
    'Project Name',
    'Project ID',
    'Version ID',
    'Version Name',
    'Created By',
    'Creation Date',
    'Server Version',
    'Mode'
]

# Create CSV file with the latest version data
output_file = 'latest_project_versions.csv'
with open(output_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    
    # Write data for each project's latest version
    for project_id, version in latest_projects.items():
        row = {
            'Project Name': version['project']['name'],
            'Project ID': version['project']['id'],
            'Version ID': version['id'],
            'Version Name': version['name'],
            'Created By': version['createdBy'],
            'Creation Date': version['creationDate'],
            'Server Version': version['serverVersion'],
            'Mode': version['mode']
        }
        writer.writerow(row)

print(f"Latest project versions have been saved to {output_file}")