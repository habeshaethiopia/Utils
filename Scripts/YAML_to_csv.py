import streamlit as st
import pandas as pd
import yaml
from io import StringIO

def yaml_to_dataframe(yaml_content):
    """Convert YAML content to a Pandas DataFrame."""
    try:
        data = yaml.safe_load(yaml_content)
        if isinstance(data, dict):
            data = [data]  # Wrap dictionary in a list to create a DataFrame
        return pd.DataFrame(data)
    except yaml.YAMLError as e:
        st.error(f"Error loading YAML: {e}")
        return pd.DataFrame()

# Streamlit UI
st.title("YAML to CSV Converter")

st.write("Upload your YAML file and download the converted CSV.")

uploaded_file = st.file_uploader("Choose a YAML file", type=["yaml", "yml"])

if uploaded_file is not None:
    # Read the uploaded YAML file
    yaml_content = uploaded_file.read().decode("utf-8")

    # Convert YAML to DataFrame
    df = yaml_to_dataframe(yaml_content)

    if not df.empty:
        st.write("Preview of the converted DataFrame:")
        st.dataframe(df)

        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="converted_file.csv",
            mime="text/csv",
        )
    else:
        st.error("The uploaded YAML file could not be converted to a valid DataFrame.")

