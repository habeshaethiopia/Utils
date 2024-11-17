import unittest
from unittest.mock import patch, mock_open
import json
import os
import requests

# Import the functions to be tested from extract_versions.py
from src.extract_versions import (
    fetch_applications,
    fetch_versions,
    fetch_issues,
    fetch_issues_concurrently,
    process_versions,
    process_issues,
    write_to_csv,
    flatten_dict,
    validate_schema,
    get_date_range
)


class TestExtractVersions(unittest.TestCase):
    """Unit tests for extract_versions.py"""

    # Sample JSON responses as Python dictionaries
    APPLICATIONS_RESPONSE = {
        "data": [
            {
                "id": 10028,
                "project": {
                    "id": 20,
                    "name": "SPARTA-ET",
                    "description": None,
                    "creationDate": "2023-10-30T19:33:56.165+00:00",
                    "createdBy": "ctorres",
                    "issueTemplateId": "Prioritized-HighRisk-Project-Template"
                },
                "name": "07",
                "description": "",
                "createdBy": "ctorres",
                "creationDate": "2023-10-30T19:33:56.166+00:00",
                "committed": True,
                "issueTemplateId": "Prioritized-HighRisk-Project-Template",
                "issueTemplateName": "Prioritized High Risk Issue Template",
                "active": True,
                "_href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028"
            },
            {
                "id": 10723,
                "project": {
                    "id": 20,
                    "name": "SPARTA-ET",
                    "description": None,
                    "creationDate": "2023-10-30T19:33:56.165+00:00",
                    "createdBy": "ctorres",
                    "issueTemplateId": "Prioritized-HighRisk-Project-Template"
                },
                "name": "07-Aug",
                "description": "",
                "createdBy": "phillips.humphrey@associates.fema.dhs.gov",
                "creationDate": "2024-10-23T19:20:20.177+00:00",
                "committed": True,
                "issueTemplateId": "Prioritized-HighRisk-Project-Template",
                "issueTemplateName": "Prioritized High Risk Issue Template",
                "active": True,
                "_href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10723"
            }
            # Add more application entries as needed
        ]
    }

    VERSIONS_RESPONSE = {
        "data": [
            {
                "projectVersionId": 10028,
                "lastScanId": 22,
                "id": 56077,
                "projectVersionName": "07",
                "projectName": "SPARTA-ET",
                "revision": 0,
                "folderId": 260,
                "folderGuid": "5b50bb77-071d-08ed-fdba-1213fa90ac5a",
                "issueInstanceId": "495D5C0A8FDFB27D3C1AD470BC9BF65D",
                "issueName": "Key Management: Empty Encryption Key",
                "primaryLocation": "ContainerItemView.js",
                "lineNumber": 460,
                "fullFileName": "app-ui/src/go/components/modules/requestDetails/v3/items/shared/ContainerItemView.js",
                "analyzer": "Structural",
                "kingdom": "Security Features",
                "friority": "High",
                "enginePriority": "High",
                "reviewed": None,
                "bugURL": None,
                "externalBugId": None,
                "hidden": False,
                "removed": False,
                "suppressed": False,
                "_href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues/56077"
            },
            {
                "projectVersionId": 10028,
                "lastScanId": 22,
                "id": 56197,
                "projectVersionName": None,
                "projectName": None,
                "revision": 0,
                "folderId": 260,
                "folderGuid": "5b50bb77-071d-08ed-fdba-1213fa90ac5a",
                "issueInstanceId": "47282DCFF94197DE8124E75D534354B9",
                "issueName": "Key Management: Hardcoded Encryption Key",
                "primaryLocation": "CostShare.js",
                "lineNumber": 152,
                "fullFileName": "app-ui/src/go/components/dynamic/modules/costShare/v1/CostShare.js",
                "analyzer": "Structural",
                "kingdom": "Security Features",
                "friority": "High",
                "enginePriority": "High",
                "reviewed": None,
                "bugURL": None,
                "externalBugId": None,
                "primaryTag": None,
                "hasAttachments": False,
                "hasCorrelatedIssues": False,
                "correlatedIssueIdsAsSource": [],
                "correlatedIssueIdsAsTarget": [],
                "hasComments": False,
                "scanStatus": "NEW",
                "foundDate": "2023-07-25T10:41:33.000+00:00",
                "removedDate": None,
                "engineType": "SCA",
                "displayEngineType": "SCA",
                "engineCategory": "STATIC",
                "primaryRuleGuid": "54B5A093-BF90-402E-B411-CD186B9B29C6",
                "impact": 3.0,
                "likelihood": 2.4,
                "severity": 3.0,
                "confidence": 5.0,
                "audited": False,
                "issueStatus": "Unreviewed",
                "primaryTagValueAutoApplied": False,
                "hidden": False,
                "removed": False,
                "suppressed": False,
                "_href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues/56223"
            }
            # Add more version entries as needed
        ],
        "count": 2522,
        "responseCode": 200,
        "links": {
            "next": {
                "href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues?limit=20&limit=5000&orderby=friority&filterset=a243b195-0a59-3f8b-1403-d55b7a7d78e6&sh&fulltextsearch=false&includeInactive=false&myAssignedIssues=false&start=20"
            },
            "last": {
                "href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues?limit=20&limit=5000&orderby=friority&filterset=a243b195-0a59-3f8b-1403-d55b7a7d78e6&sh&fulltextsearch=false&includeInactive=false&myAssignedIssues=false&start=2502"
            },
            "first": {
                "href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues?limit=20&limit=5000&orderby=friority&filterset=a243b195-0a59-3f8b-1403-d55b7a7d78e6&sh&fulltextsearch=false&includeInactive=false&myAssignedIssues=false&start=0"
            }
        }
    }

    ISSUES_RESPONSE = {
        "data": [
            {
                "projectVersionId": 10028,
                "lastScanId": 22,
                "id": 56077,
                "projectVersionName": "07",
                "projectName": "SPARTA-ET",
                "revision": 0,
                "folderId": 260,
                "folderGuid": "5b50bb77-071d-08ed-fdba-1213fa90ac5a",
                "issueInstanceId": "495D5C0A8FDFB27D3C1AD470BC9BF65D",
                "issueName": "Key Management: Empty Encryption Key",
                "primaryLocation": "ContainerItemView.js",
                "lineNumber": 460,
                "fullFileName": "app-ui/src/go/components/modules/requestDetails/v3/items/shared/ContainerItemView.js",
                "analyzer": "Structural",
                "kingdom": "Security Features",
                "friority": "High",
                "enginePriority": "High",
                "reviewed": None,
                "bugURL": None,
                "externalBugId": None,
                "hidden": False,
                "removed": False,
                "suppressed": False,
                "_href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues/56077"
            },
            {
                "projectVersionId": 10028,
                "lastScanId": 22,
                "id": 56223,
                "projectVersionName": None,
                "projectName": None,
                "revision": 0,
                "folderId": 260,
                "folderGuid": "5b50bb77-071d-08ed-fdba-1213fa90ac5a",
                "issueInstanceId": "47282DCFF94197DE8124E75D534354B9",
                "issueName": "Key Management: Hardcoded Encryption Key",
                "primaryLocation": "CostShare.js",
                "lineNumber": 152,
                "fullFileName": "app-ui/src/go/components/dynamic/modules/costShare/v1/CostShare.js",
                "analyzer": "Structural",
                "kingdom": "Security Features",
                "friority": "High",
                "enginePriority": "High",
                "reviewed": None,
                "bugURL": None,
                "externalBugId": None,
                "primaryTag": None,
                "hasAttachments": False,
                "hasCorrelatedIssues": False,
                "correlatedIssueIdsAsSource": [],
                "correlatedIssueIdsAsTarget": [],
                "hasComments": False,
                "scanStatus": "NEW",
                "foundDate": "2023-07-25T10:41:33.000+00:00",
                "removedDate": None,
                "engineType": "SCA",
                "displayEngineType": "SCA",
                "engineCategory": "STATIC",
                "primaryRuleGuid": "54B5A093-BF90-402E-B411-CD186B9B29C6",
                "impact": 3.0,
                "likelihood": 2.4,
                "severity": 3.0,
                "confidence": 5.0,
                "audited": False,
                "issueStatus": "Unreviewed",
                "primaryTagValueAutoApplied": False,
                "hidden": False,
                "removed": False,
                "suppressed": False,
                "_href": "https://ssc.fema.net/ssc/api/v1/projectVersions/10028/issues/56223"
            }
            # Add more issue entries as needed
        ]
    }

    ISSUES_RESPONSE_PARTIAL = {
        "data": [
            # Partial data for pagination simulation
        ]
    }

    def test_flatten_dict(self):
        """Test the flatten_dict utility function."""

        nested_dict = {
            "id": 1,
            "name": "Test",
            "project": {
                "id": 100,
                "name": "ProjectX"
            },
            "tags": ["security", "high"],
            "details": {
                "created_at": "2023-10-30T19:33:56.165+00:00",
                "updated_at": "2023-10-31T19:33:56.165+00:00"
            }
        }

        expected_flat = {
            "id": 1,
            "name": "Test",
            "project_id": 100,
            "project_name": "ProjectX",
            "tags": "security, high",
            "details_created_at": "2023-10-30T19:33:56.165+00:00",
            "details_updated_at": "2023-10-31T19:33:56.165+00:00"
        }

        flat = flatten_dict(nested_dict)
        self.assertEqual(flat, expected_flat)

    @patch('src.extract_versions.validate_schema')
    @patch('src.extract_versions.write_to_csv')
    @patch('src.extract_versions.os.path.isfile')
    def test_write_to_csv_new_file(self, mock_isfile, mock_write_to_csv, mock_validate_schema):
        """Test writing to a new CSV file (file does not exist)."""

        items = [
            {"id": 1, "name": "Test Application"},
            {"id": 2, "name": "Another Application"}
        ]
        fieldnames = ["id", "name"]
        filename = "new_applications.csv"

        mock_isfile.return_value = False
        mock_validate_schema.return_value = True
        mock_write_to_csv.return_value = True

        result = write_to_csv(items, fieldnames, filename)

        self.assertTrue(result)
        mock_isfile.assert_called_with(filename)
        mock_validate_schema.assert_called_with(fieldnames, filename)
        mock_write_to_csv.assert_called_with(items, fieldnames, filename)

    @patch('src.extract_versions.validate_schema')
    @patch('src.extract_versions.write_to_csv')
    @patch('src.extract_versions.os.path.isfile')
    def test_write_to_csv_existing_file(self, mock_isfile, mock_write_to_csv, mock_validate_schema):
        """Test writing to an existing CSV file (file exists)."""

        items = [
            {"id": 3, "name": "New Application"},
            {"id": 4, "name": "Additional Application"}
        ]
        fieldnames = ["id", "name"]
        filename = "existing_applications.csv"

        mock_isfile.return_value = True
        mock_validate_schema.return_value = True
        mock_write_to_csv.return_value = True

        result = write_to_csv(items, fieldnames, filename)

        self.assertTrue(result)
        mock_isfile.assert_called_with(filename)
        mock_validate_schema.assert_called_with(fieldnames, filename)
        mock_write_to_csv.assert_called_with(items, fieldnames, filename)

    @patch('src.extract_versions.requests.get')
    def test_fetch_api_data_success(self, mock_get):
        """Test fetch_api_data with a successful API response."""

        endpoint_key = "applications"
        mock_response = mock_get.return_value
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.APPLICATIONS_RESPONSE

        result = fetch_api_data(endpoint_key)

        mock_get.assert_called_once()
        self.assertEqual(result, self.APPLICATIONS_RESPONSE)

    @patch('src.extract_versions.requests.get')
    def test_fetch_api_data_failure(self, mock_get):
        """Test fetch_api_data with a failed API response."""

        endpoint_key = "applications"
        mock_response = mock_get.return_value
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error fetching data")

        result = fetch_api_data(endpoint_key)

        mock_get.assert_called_once()
        self.assertEqual(result, {})

    @patch('src.extract_versions.fetch_api_data')
    def test_fetch_applications(self, mock_fetch_api_data):
        """Test fetching applications within a date range."""

        start_date, end_date = "2023-10-23T19:20:20.177+00:00", "2023-10-30T19:20:20.177+00:00"
        mock_fetch_api_data.return_value = self.APPLICATIONS_RESPONSE

        with patch('src.extract_versions.flatten_dict', side_effect=lambda x: x):
            with patch('src.extract_versions.write_to_csv', return_value=True):
                applications = fetch_applications(start_date, end_date)

        mock_fetch_api_data.assert_called_once_with(
            "applications",
            params_override={
                "startDate": start_date,
                "endDate": end_date
            }
        )
        self.assertEqual(applications, self.APPLICATIONS_RESPONSE["data"])

    @patch('src.extract_versions.fetch_api_data')
    def test_fetch_versions(self, mock_fetch_api_data):
        """Test fetching versions for a given project ID."""

        project_id = "20"
        mock_fetch_api_data.side_effect = [self.VERSIONS_RESPONSE, {}]  # Simulate end of pagination

        with patch('src.extract_versions.flatten_dict', side_effect=lambda x: x):
            with patch('src.extract_versions.write_to_csv', return_value=True):
                versions = fetch_versions(project_id)

        # Should have fetched only once due to count=2522 and limit=200, but simulated end
        self.assertEqual(versions, self.VERSIONS_RESPONSE["data"])

    @patch('src.extract_versions.fetch_api_data')
    def test_fetch_issues(self, mock_fetch_api_data):
        """Test fetching issues for a given version ID."""

        version_id = "10028"
        mock_fetch_api_data.side_effect = [self.ISSUES_RESPONSE, {}]  # Simulate end of pagination

        with patch('src.extract_versions.flatten_dict', side_effect=lambda x: x):
            with patch('src.extract_versions.write_to_csv', return_value=True):
                issues = fetch_issues(version_id)

        self.assertEqual(issues, self.ISSUES_RESPONSE["data"])

    @patch('src.extract_versions.fetch_issues')
    def test_fetch_issues_concurrently(self, mock_fetch_issues):
        """Test fetching issues concurrently for multiple version IDs."""

        version_ids = [56077, 56223, 56240, 56250]
        mock_fetch_issues.side_effect = [
            self.ISSUES_RESPONSE["data"],
            self.ISSUES_RESPONSE["data"],
            self.ISSUES_RESPONSE["data"],
            self.ISSUES_RESPONSE["data"]
        ]

        with patch('src.extract_versions.flatten_dict', side_effect=lambda x: x):
            with patch('src.extract_versions.write_to_csv', return_value=True):
                all_issues = fetch_issues_concurrently(version_ids, max_workers=2)

        self.assertEqual(len(all_issues), len(self.ISSUES_RESPONSE["data"]) * len(version_ids))
        self.assertTrue(all(isinstance(issue, dict) for issue in all_issues))

    @patch('src.extract_versions.fetch_versions')
    def test_process_versions(self, mock_fetch_versions):
        """Test processing versions for all applications."""

        applications = self.APPLICATIONS_RESPONSE["data"]
        mock_fetch_versions.side_effect = [
            self.VERSIONS_RESPONSE["data"],
            self.VERSIONS_RESPONSE["data"]
        ]

        with patch('src.extract_versions.flatten_dict', side_effect=lambda x: x):
            with patch('src.extract_versions.write_to_csv', return_value=True):
                all_versions = process_versions(applications)

        expected_length = len(self.VERSIONS_RESPONSE["data"]) * len(applications)
        self.assertEqual(len(all_versions), expected_length)

    @patch('src.extract_versions.fetch_issues_concurrently')
    def test_process_issues(self, mock_fetch_issues_concurrently):
        """Test processing issues for all versions."""

        versions = self.VERSIONS_RESPONSE["data"]
        mock_fetch_issues_concurrently.return_value = self.ISSUES_RESPONSE["data"]

        all_issues = process_issues(versions)

        mock_fetch_issues_concurrently.assert_called_once_with(
            [version.get("id") for version in versions if version.get("id")]
        )
        self.assertEqual(all_issues, self.ISSUES_RESPONSE["data"])

    def test_validate_schema_matching(self):
        """Test schema validation when schemas match."""

        fieldnames = ["id", "name"]
        filename = "existing_applications.csv"

        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data="id,name\r\n")):
                is_valid = validate_schema(fieldnames, filename)
                self.assertTrue(is_valid)

    def test_validate_schema_mismatch(self):
        """Test schema validation when schemas do not match."""

        fieldnames = ["id", "name"]
        filename = "existing_applications.csv"

        with patch("os.path.isfile", return_value=True):
            with patch("builtins.open", mock_open(read_data="name,id\r\n")):
                with patch("builtins.print") as mock_print:
                    is_valid = validate_schema(fieldnames, filename)
                    self.assertFalse(is_valid)
                    mock_print.assert_called_with(
                        "Schema mismatch in existing_applications.csv. Expected ['id', 'name'], got ['name', 'id']."
                    )

    def test_validate_schema_file_not_exist(self):
        """Test schema validation when the file does not exist."""

        fieldnames = ["id", "name"]
        filename = "non_existent.csv"

        with patch("os.path.isfile", return_value=False):
            is_valid = validate_schema(fieldnames, filename)
            self.assertTrue(is_valid)  # Should return True as there's no file to validate against

    def test_get_date_range(self):
        """Test calculating the date range for the past 7 days."""

        start_date, end_date = get_date_range()
        end_datetime = datetime.fromisoformat(end_date)
        start_datetime = datetime.fromisoformat(start_date)

        expected_end = datetime.now()
        expected_start = expected_end - timedelta(days=7)

        # Allow slight differences due to execution time
        self.assertAlmostEqual(start_datetime.timestamp(), expected_start.timestamp(), delta=5)
        self.assertAlmostEqual(end_datetime.timestamp(), expected_end.timestamp(), delta=5)


if __name__ == '__main__':
    unittest.main() 