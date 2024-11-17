# Extract Versions and Security Issues

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Output](#output)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Overview

`extract_versions.py` is a Python script designed to interact with specific APIs to fetch and process data related to applications, their versions, and associated security issues. The script performs the following tasks:

1. **Fetch Applications**: Retrieves a list of applications within a specified date range.
2. **Fetch Versions**: For each application, fetches all associated versions, handling pagination as needed.
3. **Fetch Security Issues**: For each version, retrieves all related security issues concurrently to optimize performance.
4. **Data Storage**: Stores the fetched data in structured CSV files for further analysis or reporting.

## Features

- **Modular Design**: Organized functions for fetching applications, versions, and issues.
- **Concurrency**: Utilizes multi-threading to fetch security issues for multiple versions simultaneously, improving efficiency.
- **Data Flattening**: Transforms nested JSON responses into flat dictionaries suitable for CSV storage.
- **Error Handling**: Comprehensive error management to ensure robustness during API interactions.
- **Configurable**: Easily adjustable API endpoints, headers, and parameters to suit different environments.

## Prerequisites

- **Python 3.7 or higher**
- **Required Python Packages**:
  - `requests`
  - `urllib3`

## Configuration

Before running the script, you need to configure API tokens and endpoints:

1. **Update API Tokens**:

   Open `src/extract_versions.py` and locate the **Global Variables for API Tokens** section. Replace the placeholder strings with your actual API tokens.

   ```python
   APPLICATIONS_API_TOKEN = 'your_applications_api_token_here'
   VERSIONS_API_TOKEN = 'your_versions_api_token_here'
   ISSUES_API_TOKEN = 'your_issues_api_token_here'
   ```

2. **Verify API Endpoints**:

   Ensure that the URLs in the `API_CONFIG` dictionary match your API endpoints. Update the domain and paths if necessary.

   ```python
   API_CONFIG = {
       "applications": {
           "url": "https://your-domain/api/v2/applications",
           ...
       },
       "versions": {
           "url": "https://your-domain/ssc/api/v1/projects/{project_id}/versions",
           ...
       },
       "issues": {
           "url": "https://your-domain/ssc/api/v1/projectVersions/{version_id}/issues",
           ...
       }
   }
   ```

## Usage

Navigate to the project directory and execute the script:
