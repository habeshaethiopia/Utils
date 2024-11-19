import streamlit as st
import requests
import pandas as pd
import os
from io import BytesIO
import time

st.set_page_config(page_title="API Workflow Manager", layout="wide")

# Custom CSS to improve the look
st.markdown("""
<style>
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .stButton>button {
        width: 100%;
    }
    .stProgress>div>div>div>div {
        background-color: #4CAF50;
    }
    .css-1v0mbdj.ebxwdo61 {
        width: 100%;
    }
    .api-config {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Global API Configuration
# -----------------------------
API_CONFIG = {
    "applications": {
        "url": "https://domain/api/v2/applications",
        "headers": {"Accept": "application/json", "Authorization": ""},
        "params": {"startDate": None, "endDate": None},
        "output_file": "applications.csv",
    },
    "versions": {
        "url": "https://domain/ssc/api/v1/projects/{project_id}/versions",
        "headers": {"Accept": "application/json", "Authorization": ""},
        "params": {"start": 0, "limit": 200},
        "output_file": "all_project_versions.csv",
    },
    "issues": {
        "url": "https://domain/ssc/api/v1/projectVersions/{version_id}/issues",
        "headers": {"Accept": "application/json", "Authorization": ""},
        "params": {"limit": 5000, "orderby": "friority", "start": 0},
        "output_file": "security_issues.csv",
    },
}

# -----------------------------
# Utility Functions
# -----------------------------
def fetch_api_data(api_key, dependency_data=None):
    config = API_CONFIG[api_key]
    url = config["url"]
    headers = config["headers"]
    params = config["params"]

    if dependency_data:
        url = url.format(**dependency_data)

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API Error ({api_key}): {str(e)}")
        return None

def save_to_csv(data, output_file):
    if data:
        pd.DataFrame(data).to_csv(output_file, index=False)
        st.success(f"Saved {output_file}")

def load_csv(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

# -----------------------------
# Streamlit App UI
# -----------------------------
# st.set_page_config(page_title="API Workflow Manager", layout="wide")

st.title("Dependent API Workflow Manager")

# Configuration Section
st.header("API Configuration")

config_tabs = st.tabs([api_key.capitalize() for api_key in API_CONFIG.keys()])

for tab, (api_key, config) in zip(config_tabs, API_CONFIG.items()):
    with tab:
        st.markdown(f"<div class='api-config'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            config["url"] = st.text_input(
                f"Base URL",
                value=config["url"],
                key=f"{api_key}_url",
            )
        
        with col2:
            config["headers"]["Authorization"] = st.text_input(
                f"API Token",
                value=config["headers"]["Authorization"],
                type="password",
                key=f"{api_key}_auth",
            )
        
        st.markdown("**Parameters**")
        param_cols = st.columns(len(config["params"]))
        for (param_key, param_value), col in zip(config["params"].items(), param_cols):
            with col:
                if "date" in param_key.lower():
                    print(param_key)
                    date_value = st.date_input(
                        param_key.capitalize(),
                        value=None,  # Default to None/today
                        key=f"{api_key}_{param_key}",
                    )
                    # Convert to ISO format string
                    print(date_value)
                    config["params"][param_key] = date_value.isoformat()
                    print(config["params"][param_key])
                else:
                    config["params"][param_key] = st.text_input(
                        param_key.capitalize(),
                        value=param_value if param_value else "",
                        key=f"{api_key}_{param_key}",
                    )
        
        st.markdown("</div>", unsafe_allow_html=True)

# Execution Section
st.header("Execute API Workflow")

if st.button("Run Workflow", key="run_workflow"):
    with st.spinner("Processing API requests..."):
        # Step 1: Fetch Applications
        st.subheader("Step 1: Fetching Applications")
        progress_bar = st.progress(0)
        app_data = fetch_api_data("applications")
        save_to_csv(app_data, API_CONFIG["applications"]["output_file"])
        project_ids = [app["id"] for app in app_data] if app_data else []
        progress_bar.progress(33)

        # Step 2: Fetch Versions
        if project_ids:
            st.subheader("Step 2: Fetching Versions")
            all_versions = []
            for i, project_id in enumerate(project_ids):
                version_data = fetch_api_data("versions", {"project_id": project_id})
                if version_data:
                    all_versions.extend(version_data)
                progress_bar.progress(33 + (i + 1) / len(project_ids) * 33)
            save_to_csv(all_versions, API_CONFIG["versions"]["output_file"])
            version_ids = [version["id"] for version in all_versions]
        else:
            version_ids = []
            st.warning("No project IDs found. Skipping version fetching.")

        # Step 3: Fetch Issues
        if version_ids:
            st.subheader("Step 3: Fetching Issues")
            all_issues = []
            for i, version_id in enumerate(version_ids):
                issues_data = fetch_api_data("issues", {"version_id": version_id})
                if issues_data:
                    all_issues.extend(issues_data)
                progress_bar.progress(66 + (i + 1) / len(version_ids) * 34)
            save_to_csv(all_issues, API_CONFIG["issues"]["output_file"])
        else:
            st.warning("No version IDs found. Skipping issue fetching.")

        progress_bar.progress(100)
        st.success("Workflow completed successfully!")

# Section: CSV Management
st.header("CSV File Management")

csv_tabs = st.tabs([api_key.capitalize() for api_key in API_CONFIG.keys()])

for tab, (api_key, config) in zip(csv_tabs, API_CONFIG.items()):
    with tab:
        file_path = config["output_file"]
        csv_data = load_csv(file_path)
        if csv_data is not None:
            st.subheader(f"Preview: {file_path}")
            st.dataframe(csv_data.head())
            st.download_button(
                label=f"Download {file_path}",
                data=BytesIO(csv_data.to_csv(index=False).encode("utf-8")),
                file_name=file_path,
                mime="text/csv",
            )
        else:
            st.info(f"No data available for {file_path}. Run the workflow to generate data.")

# Add a footer
st.markdown("---")
st.markdown("Created with ❤️ using Streamlit")