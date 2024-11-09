import json
import csv
import os
import subprocess
from fetch_time import write_to_csv
'''
def test_csv_generation():
    # Sample JSON response
    sample_json = {
        "items": [
            {
                "id": 67,
                "name": "ACE5",
                "scannerPoolId": 1,
                "scannerPoolName": "Default",
                "scannerPoolScannerScalingIsEnabled": False,
                "scanPriority": 5,
                "isDataRetentionEnabled": False,
                "dataRetentionDays": 180,
                "enableSASTCorrelation": True,
                "disableGlobalDomainRestrictions": False,
                "hasDomainRestrictions": False,
                "disableGlobalPrivateDataSettings": True,
                "hasPrivateDataSettings": False,
                "fortifyConnectClientId": None,
                "fortifyConnectClientName": "",
                "fortifyConnectClientModeType": None
            },
            {
                "id": 65,
                "name": "AdminIA",
                "scannerPoolId": 2,
                "scannerPoolName": "Custom",
                "scannerPoolScannerScalingIsEnabled": True,
                "scanPriority": 3,
                "isDataRetentionEnabled": True,
                "dataRetentionDays": 90,
                "enableSASTCorrelation": False,
                "disableGlobalDomainRestrictions": True,
                "hasDomainRestrictions": True,
                "disableGlobalPrivateDataSettings": False,
                "hasPrivateDataSettings": True,
                "fortifyConnectClientId": "12345",
                "fortifyConnectClientName": "AdminClient",
                "fortifyConnectClientModeType": "SAST"
            }
        ]
    }

    # Mock the subprocess.run to return the sample JSON response
    class MockCompletedProcess:
        def __init__(self, stdout, returncode=0):
            self.stdout = stdout
            self.returncode = returncode

    def mock_run(*args, **kwargs):
        return MockCompletedProcess(stdout=json.dumps(sample_json))

    # Apply the mock to subprocess.run
    subprocess.run = mock_run

    # Run the fetch script
    process()

    # Check if the CSV file is created
    csv_file_name = "applications_test.csv"
    assert os.path.exists(csv_file_name)

    # Read the CSV file and verify its content matches sample_json data
    with open(csv_file_name, mode="r", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["id"] == "67"
        assert rows[0]["name"] == "ACE5"
        assert rows[1]["id"] == "65"
        assert rows[1]["name"] == "AdminIA"

    # Clean up the generated CSV file
    os.remove(csv_file_name)


# Run the test
test_csv_generation()
'''
def test_write_to_csv():
    # Sample data from API response
    items = [
        {
            "id": 67,
            "name": "ACE5",
            "scannerPoolId": 1,
            "scannerPoolName": "Default",
            "scannerPoolScannerScalingIsEnabled": False,
            "scanPriority": 5,
            "isDataRetentionEnabled": False,
            "dataRetentionDays": 180,
            "enableSASTCorrelation": True,
            "disableGlobalDomainRestrictions": False,
            "hasDomainRestrictions": False,
            "disableGlobalPrivateDataSettings": True,
            "hasPrivateDataSettings": False,
            "fortifyConnectClientId": None,
            "fortifyConnectClientName": "",
            "fortifyConnectClientModeType": None
        },
        {
            "id": 65,
            "name": "AdminIA",
            "scannerPoolId": 2,
            "scannerPoolName": "Custom",
            "scannerPoolScannerScalingIsEnabled": True,
            "scanPriority": 3,
            "isDataRetentionEnabled": True,
            "dataRetentionDays": 90,
            "enableSASTCorrelation": False,
            "disableGlobalDomainRestrictions": True,
            "hasDomainRestrictions": True,
            "disableGlobalPrivateDataSettings": False,
            "hasPrivateDataSettings": True,
            "fortifyConnectClientId": "12345",
            "fortifyConnectClientName": "AdminClient",
            "fortifyConnectClientModeType": "SAST"
        }
    ]

    # Test file name
    test_csv_file = "test_output.csv"

    # Write to CSV
    write_to_csv(items)

    # Verify the CSV contents
    with open(test_csv_file, mode="r", newline="", encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)
        
        # Verify number of rows
        assert len(rows) == 2
        
        # Verify first row contents
        assert rows[0]["id"] == "67"
        assert rows[0]["name"] == "ACE5"
        assert rows[0]["scannerPoolName"] == "Default"
        assert rows[0]["fortifyConnectClientName"] == ""
        
        # Verify second row contents
        assert rows[1]["id"] == "65"
        assert rows[1]["name"] == "AdminIA"
        assert rows[1]["scannerPoolName"] == "Custom"
        assert rows[1]["fortifyConnectClientName"] == "AdminClient"

    # Clean up test file
    os.remove(test_csv_file)
if __name__ == "__main__":
    test_write_to_csv()
    print('All tests passed!')