import requests
import json
import urllib3
import csv
from datetime import datetime, time
from collections import defaultdict

# Global variables and configuration
API_HEADERS = {"accept": "application/json", "Authorization": "FortifyToken xxxx"}

API_PARAMS = {
    "start": 0,
    "limit": 200,
    "fulltextsearch": "false",
    "includeInactive": "false",
    "myAssignedIssues": "false",
}

BASE_URL = "https://domain"
APPLICATIONS_API = f"{BASE_URL}/api/v2/applications"
VERSIONS_API = f"{BASE_URL}/ssc/api/v1/projects"
ISSUES_API = f"{BASE_URL}/ssc/api/v1/projectVersions"
OUTPUT_FILES = {
    "applications": "applications.csv",
    "versions": "all_project_versions.csv",
    "issues": "security_issues.csv",  # New output file
}

VERSION_FIELDS = [
    "Project Name",
    "Project ID",
    "Version ID",
    "Version Name",
    "Version Description",
    "Project Version Status",
    "Server Version Status",
    "Issue Template ID",
    "Issue Template Name",
    "Development Phase",
    "Development Strategy",
    "Business Risk Rating",
    "Business Criticality",
    "Repository URL",
    "Repository Type",
    "Issue Status",
    "Analysis Status",
    "Current Analysis Date",
    "Published Status",
    "Project Owner",
    "Project Owner First Name",
    "Project Owner Last Name",
    "Project Owner Email",
    "Application Name",
    "Application ID",
    "Application Type",
    "Application Business Unit",
    "Application Tags",
    "Project Created By",
    "Project Creation Date",
]

# Suppress SSL verification warnings
urllib3.disable_warnings()


def fetch_api_data(url, params=None):
    """Generic function to fetch data from API with error handling"""
    try:
        response = requests.get(url, headers=API_HEADERS, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response: {e}")
        return None


def write_to_csv(data, fieldnames, filename):
    """Generic function to write data to CSV with error handling"""
    try:
        with open(filename, mode="w", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully written to {filename}")
        return True
    except IOError as e:
        print(f"Failed to write to CSV file {filename}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while writing to CSV: {e}")
        return False


def get_applications():
    """Fetch and save applications data"""
    response_data = fetch_api_data(APPLICATIONS_API)
    if not response_data:
        return []

    items = response_data.get("items", [])
    if not items:
        print("No applications found")
        return []

    if write_to_csv(items, items[0].keys(), OUTPUT_FILES["applications"]):
        return items
    return []


def fetch_issues(project_version_id):
    """Fetch security issues for a specific project version"""
    issues_url = f"{ISSUES_API}/{project_version_id}/issues"
    all_issues = []
    start = 0
    limit = 100  # Increased limit for faster fetching

    while True:
        params = {**API_PARAMS, "start": start, "limit": limit, "orderby": "friority"}

        print(
            f"Fetching issues for project version {project_version_id} (start: {start})"
        )
        response_data = fetch_api_data(issues_url, params)

        if not response_data or "data" not in response_data:
            print(
                f"No data found for project version {project_version_id} at start {start}"
            )
            break

        issues = response_data["data"]
        if not issues:
            break

        # Get fields from first issue if we haven't set them yet
        if not hasattr(fetch_issues, "fields") and issues:
            fetch_issues.fields = list(issues[0].keys())
            print(f"Fields detected: {fetch_issues.fields}")

        all_issues.extend(issues)

        # Check if we've reached the end
        if len(issues) < limit:
            break
        time.sleep(0.1)
        start += limit

    return all_issues


def format_issue_data(issue):
    """Format issue data for CSV output with all fields from response"""
    return {key: issue.get(key, "") for key in fetch_issues.fields}


def process_issues(versions):
    """Process and save security issues data for all versions"""
    all_issues = []
    total_versions = len(versions)

    for index, version in enumerate(versions, 1):
        version_id = version.get("id")
        if not version_id:
            continue

        print(
            f"Processing version {index}/{total_versions}: {version.get('name')} (ID: {version_id})"
        )
        version_issues = fetch_issues(version_id)
        all_issues.extend(version_issues)

    if all_issues:
        formatted_issues = [format_issue_data(issue) for issue in all_issues]
        # Use the dynamically detected fields for CSV headers
        write_to_csv(formatted_issues, fetch_issues.fields, OUTPUT_FILES["issues"])
        print(f"Total issues found and saved: {len(all_issues)}")
    else:
        print("No issues found")

    return all_issues


def process_versions(applications):
    """Process and save versions data for all applications"""
    all_versions = []

    for app in applications:
        project_id = app["id"]
        versions_url = f"{VERSIONS_API}/{project_id}/versions"
        print(f"Fetching versions for application: {app['name']} (ID: {project_id})")

        versions_data = fetch_api_data(versions_url, API_PARAMS)
        if versions_data:
            all_versions.extend(versions_data["data"])

    if all_versions:
        formatted_versions = [format_version_data(version) for version in all_versions]
        write_to_csv(formatted_versions, VERSION_FIELDS, OUTPUT_FILES["versions"])
        print(f"Total versions found: {len(all_versions)}")

    return all_versions


def format_version_data(version):
    """Format version data for CSV output"""
    return {
        "Project Name": version["project"]["name"],
        "Project ID": version["project"]["id"],
        "Version ID": version["id"],
        "Version Name": version["name"],
        "Version Description": version.get("description", ""),
        "Project Version Status": version.get("status", ""),
        "Server Version Status": version.get("serverVersion", ""),
        "Issue Template ID": version.get("issueTemplateId", ""),
        "Issue Template Name": version.get("issueTemplateName", ""),
        "Development Phase": version.get("phase", ""),
        "Development Strategy": version.get("strategy", ""),
        "Business Risk Rating": version.get("businessRiskRating", ""),
        "Business Criticality": version.get("businessCriticality", ""),
        "Repository URL": version.get("sourceControl", {}).get("url", ""),
        "Repository Type": version.get("sourceControl", {}).get("type", ""),
        "Issue Status": version.get("issueStatus", ""),
        "Analysis Status": version.get("analysisStatus", ""),
        "Current Analysis Date": version.get("currentAnalysisDate", ""),
        "Published Status": version.get("publishedStatus", ""),
        "Project Owner": version["project"].get("owner", ""),
        "Project Owner First Name": version["project"].get("ownerFirstName", ""),
        "Project Owner Last Name": version["project"].get("ownerLastName", ""),
        "Project Owner Email": version["project"].get("ownerEmail", ""),
        "Application Name": version.get("application", {}).get("name", ""),
        "Application ID": version.get("application", {}).get("id", ""),
        "Application Type": version.get("application", {}).get("type", ""),
        "Application Business Unit": version.get("application", {}).get(
            "businessUnit", ""
        ),
        "Application Tags": ", ".join(version.get("application", {}).get("tags", [])),
        "Project Created By": version["project"].get("createdBy", ""),
        "Project Creation Date": version["project"].get("creationDate", ""),
    }


def main():
    """Main execution function"""
    # Suppress SSL warnings
    urllib3.disable_warnings()
    
    try:
        # Get applications
        applications = get_applications()
        if not applications:
            print("Failed to fetch applications. Exiting.")
            return
        
        # Process versions
        versions = process_versions(applications)
        if not versions:
            print("Failed to fetch versions. Exiting.")
            return
            
        # Process issues
        process_issues(versions)
        
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()