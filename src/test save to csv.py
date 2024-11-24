import json
from extract_versions_latest import write_to_csv, map_fields  # Adjust the import based on your file structure

def main():
    # Load the JSON data from the files
    with open('/home/adane/Repository/Utils/src/issues.json') as issues_file:
        issues_data = json.load(issues_file)

    with open('/home/adane/Repository/Utils/src/version.json') as version_file:
        version_data = json.load(version_file)

    with open('/home/adane/Repository/Utils/Scripts/res.json') as res_file:
        res_data = json.load(res_file)

    # Prepare the data for CSV writing
    items = []
    

    for issue in issues_data:
        # Find the corresponding version and application data
        project_version_id = issue['projectVersionId']
        version_info = next((v for v in version_data if v['id'] == project_version_id), None)

        # Use res.json as the application data source
        application_info = next((app for app in res_data['items'] if app['id'] == version_info['project']['id']), None) if version_info else None

        if version_info and application_info:
            # Call the map_fields function
            mapped_data = map_fields(issue, version_info, application_info)
            items.append(mapped_data)

    # Call the write_to_csv function
    filename = 'output.csv'
    fieldnames = mapped_data.keys()
    result = write_to_csv(items, fieldnames, filename)
    json.dump(items, open('output.json', 'w'), indent=4)

    # Print the result
    print(f"CSV writing successful: {result}")

if __name__ == '__main__':
    main()
