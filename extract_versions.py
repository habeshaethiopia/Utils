import requests
import json
import urllib3
import csv
from datetime import datetime
from collections import defaultdict

# API Configuration
headers = {"accept": "application/json", "Authorization": "FortifyToken token"}

# Request parameters
params = {
    "start": 0,
    "limit": 200,
    "fulltextsearch": "false",
    "includeInactive": "false",
    "myAssignedIssues": "false",
}

# Suppress SSL verification warnings
urllib3.disable_warnings()

# Step 1: Get Applications
#! check the Url is it applications or projects
applications_url = 'https://domain/api/v2/applications'
applications_response = requests.get(applications_url, headers=headers, params=params, verify=False)

if applications_response.status_code != 200:
    print(f"Error: Applications request failed with status code {applications_response.status_code}")
    exit()

applications_data = applications_response.json()

# Step 2: Get Versions for each Application
all_versions = []

for app in applications_data["data"]:
    project_id = app["id"]
    versions_url = f"domain/ssc/api/v1/projects/{project_id}/versions"
    
    print(f"Fetching versions for application: {app['name']} (ID: {project_id})")
    
    versions_response = requests.get(versions_url, headers=headers, params=params, verify=False)
    
    if versions_response.status_code == 200:
        versions_data = versions_response.json()
        all_versions.extend(versions_data["data"])
    else:
        print(f"Error fetching versions for project {project_id}: {versions_response.status_code}")

# Define the fields for versions CSV
version_fields = [
    "Project Name",
    "Project ID",
    "Version ID",
    "Version Name",
    "Created By",
    "Creation Date",
    "Server Version",
    "Mode",
    "Issue Template ID",
    "Issue Template Name",
    "Last FPR Upload Date",
    "Analysis Results Exist",
    "Audit Enabled",
    "Analysis Upload Enabled",
    "Metric Evaluation Date",
    "Delta Period",
    "Issue Count Delta",
    "Percent Audited Delta",
    "Critical Priority Issue Count Delta",
    "Master Attr Guid",
    "Project Created By",
    "Project Creation Date"
]

# Create CSV file with all version data
output_file = "all_project_versions.csv"
with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=version_fields)
    writer.writeheader()

    # Write data for all versions
    for version in all_versions:
        row = {
            "Project Name": version["project"]["name"],
            "Project ID": version["project"]["id"],
            "Version ID": version["id"],
            "Version Name": version["name"],
            "Created By": version["createdBy"],
            "Creation Date": version["creationDate"],
            "Server Version": version["serverVersion"],
            "Mode": version["mode"],
            "Issue Template ID": version["issueTemplateId"],
            "Issue Template Name": version["issueTemplateName"],
            "Last FPR Upload Date": version["currentState"]["lastFprUploadDate"],
            "Analysis Results Exist": version["currentState"]["analysisResultsExist"],
            "Audit Enabled": version["currentState"]["auditEnabled"],
            "Analysis Upload Enabled": version["currentState"]["analysisUploadEnabled"],
            "Metric Evaluation Date": version["currentState"]["metricEvaluationDate"],
            "Delta Period": version["currentState"]["deltaPeriod"],
            "Issue Count Delta": version["currentState"]["issueCountDelta"],
            "Percent Audited Delta": version["currentState"]["percentAuditedDelta"],
            "Critical Priority Issue Count Delta": version["currentState"]["criticalPriorityIssueCountDelta"],
            "Master Attr Guid": version["masterAttrGuid"],
            "Project Created By": version["project"]["createdBy"],
            "Project Creation Date": version["project"]["creationDate"]
        }
        writer.writerow(row)

print(f"All project versions have been saved to {output_file}")
print(f"Total versions found: {len(all_versions)}") 