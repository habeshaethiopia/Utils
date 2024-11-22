import pytest
import requests
from src.extract_versions_latest import fetch_api_data, API_CONFIG

def test_fetch_api_data_success(requests_mock):
    """Test successful API data fetch"""
    # Mock data
    expected_response = {
        "items": [
            {"id": 1, "name": "Test App"}
        ]
    }
    
    # Mock the API request
    requests_mock.get(
        API_CONFIG["applications"]["url"],
        json=expected_response
    )
    
    # Execute
    result = fetch_api_data("applications")
    
    # Assert
    assert result == expected_response
    assert requests_mock.called
    assert requests_mock.call_count == 1

def test_fetch_api_data_with_params(requests_mock):
    """Test API data fetch with parameter overrides"""
    # Mock data
    expected_response = {"data": [{"id": 1}]}
    project_id = "123"
    
    # Mock the API request
    requests_mock.get(
        API_CONFIG["versions"]["url"].format(project_id=project_id),
        json=expected_response
    )
    
    # Execute
    params_override = {"start": 0, "limit": 10}
    result = fetch_api_data("versions", project_id=project_id, params_override=params_override)
    
    # Assert
    assert result == expected_response
    assert requests_mock.called
    assert requests_mock.last_request.qs.get('start') == ['0']
    assert requests_mock.last_request.qs.get('limit') == ['10']

def test_fetch_api_data_invalid_endpoint():
    """Test handling of invalid endpoint key"""
    result = fetch_api_data("invalid_endpoint")
    assert result == {}

def test_fetch_api_data_request_exception(requests_mock):
    """Test handling of request exception"""
    # Mock a failed request
    requests_mock.get(
        API_CONFIG["applications"]["url"],
        status_code=500
    )
    
    # Execute
    result = fetch_api_data("applications")
    
    # Assert
    assert result == {}
    assert requests_mock.called

def test_fetch_api_data_connection_error(requests_mock):
    """Test handling of connection error"""
    # Mock a connection error
    requests_mock.get(
        API_CONFIG["applications"]["url"],
        exc=requests.exceptions.ConnectionError
    )
    
    # Execute
    result = fetch_api_data("applications")
    
    # Assert
    assert result == {}
    assert requests_mock.called 