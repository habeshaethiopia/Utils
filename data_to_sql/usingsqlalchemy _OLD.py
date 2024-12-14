import pandas as pd
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    Boolean,
    Date,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import VARCHAR
import chardet
DATABASE_URL = "mysql+pymysql://root:1942@localhost:3306/example"
# Database configuration
server = r"AWEASC2A2\SQLEXPRESS"
db = "Tenable_SC"
driver = "ODBC+Driver+18+for+SQL+Server"

# Create the connection string
connection_string = f"mssql+pyodbc://{server}/{db}?trusted_connection=yes&driver={driver}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful.")
except Exception as e:
    print(f"Connection failed: {e}")

# Session factory
Session = sessionmaker(bind=engine)


def create_table_from_csv(csv_file_path, table_name):
    """
    Creates a table dynamically from a CSV file and inserts data into the table.
    If the table already exists, it only inserts the data.

    :param csv_file_path: Path to the CSV file
    :param table_name: Name of the table to create or insert into
    """
    # Read CSV into a Pandas DataFrame
    try:
        # Detect encoding
        with open(csv_file_path, "rb") as f:
            result = chardet.detect(f.read())
            detected_encoding = result["encoding"]
            print(f"Detected Encoding: {detected_encoding}")

        # Read CSV with correct encoding
        df = pd.read_csv(csv_file_path, encoding=detected_encoding)
        print("CSV read successfully!")
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    # Establish connection and metadata
    metadata = MetaData()

    # Define a table dynamically based on the CSV columns
    table_columns = []
    for column in df.columns:
        # Infer column types based on the DataFrame
        if pd.api.types.is_integer_dtype(df[column]):
            col_type = Integer
        elif pd.api.types.is_bool_dtype(df[column]):
            col_type = Boolean
        elif pd.api.types.is_datetime64_any_dtype(df[column]):
            col_type = Date
        else:
            # Default to String with max length 255
            col_type = String
        table_columns.append(Column(column, col_type, nullable=False))

    # Create the table object
    table = Table(table_name, metadata, *table_columns, extend_existing=True)


    # Insert data into the table
    try:
        # Create the table if it doesn't exist
        metadata.create_all(engine)
        with engine.connect() as connection:
            # Insert rows
            df.to_sql(table_name, con=connection, if_exists="append", index=False, method="multi")
            print(f"Data successfully inserted into the table '{table_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage
if __name__ == "__main__":
    # Path to the CSV file
    csv_file_path = "/home/adane/Repository/AIM3_week0/notebooks/data/benin-malanville.csv"

    # Name of the table to create or update
    table_name = "example_table"

    # Create table and insert data
    create_table_from_csv(csv_file_path, table_name)
