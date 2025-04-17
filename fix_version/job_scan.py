import requests
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text 
import logging
import urllib3

urllib3.disable_warnings()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# API Configuration
API_URL = "https://example.com/api/v2/jobs"
HEADERS = {
    "accept": "application/json",
    "Authorization": "Bearer YOUR_API_TOKEN",
}

# Datetime fields to convert
DATETIME_FIELDS = [
    "jobQueuedTime",
    "jobStartedTime",
    "jobFinishedTime",
    "jobExpiryTime",
]

# Database Configuration
DB_CONFIG = {
    "server": r"AWEASC2A2\MSSQLSERVER02",
    "db": "Fortify_SSC",
    "driver": "ODBC+Driver+17+for+SQL+Server",
    "table_name": "JOB_SUMMARIES",
}
SERVER = DB_CONFIG["server"]
DB = DB_CONFIG["db"]
DRIVER = DB_CONFIG["driver"]
TABLE_NAME = DB_CONFIG["table_name"]


class DatabaseManager:
    """Handles database connections and operations."""

    def __init__(self, server: str, db: str, driver: str):
        self.connection_string = (
            f"mssql+pyodbc://{server}/{db}?trusted_connection=yes&driver={driver}"
        )
        self.engine = self.get_engine()

    def get_engine(self):
        """Create and return SQLAlchemy engine."""
        try:
            self.engine = create_engine(self.connection_string)
            return self.engine
        except SQLAlchemyError as e:
            logger.error(f"Failed to create engine: {e}")
            raise

    def test_connection(self) -> bool:
        """Test the database connection."""
        try:
            with self.engine.connect():
                logger.info("Database connection successful")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def create_table(self) -> None:
        """Create job_summaries table if it doesn't exist."""
        metadata = MetaData()
        Table(
            TABLE_NAME,
            metadata,
            Column("jobToken", String(36)),
            Column("scaBuildId", String(50)),
            Column("scaVersion", String(50)),
            Column("scaArgs", String(255)),
            Column("submitterUserName", String(100)),
            Column("submitterIpAddress", String(50)),
            Column("submitterEmail", String(255), nullable=True),
            Column("jobState", String(50)),
            Column("jobCancellable", Boolean),
            Column("jobQueuedTime", DateTime),
            Column("jobStartedTime", DateTime),
            Column("jobFinishedTime", DateTime),
            Column("jobExpiryTime", DateTime),
            Column("jobHasLog", Boolean),
            Column("jobHasFpr", Boolean),
            Column("queuedDuration", Integer),
            Column("scanDuration", Integer),
            Column("jobDuration", Integer),
            Column("priority", Integer),
            Column("pvId", Integer),
            Column("pvName", String(255)),
            Column("projectId", Integer),
            Column("projectName", String(255)),
            Column("cloudPoolUuid", String(36)),
            Column("cloudPoolName", String(255)),
            Column("cloudPoolDescription", String(500)),
            Column("cloudPoolChildOfGlobalPool", Boolean),
        )

        try:
            with self.engine.connect() as conn:
                if not self.engine.dialect.has_table(conn, TABLE_NAME):
                    metadata.create_all(self.engine)
                    logger.info(f"Created {TABLE_NAME} table")
                else:
                    logger.info(f"{TABLE_NAME} table already exists")
        except SQLAlchemyError as e:
            logger.error(f"Error creating table: {e}")
            raise

    def save_dataframe(self, df: pd.DataFrame) -> int:
        """Save DataFrame to job_summaries table."""
        try:
            # Get the table schema from the database for SQL Server
            with self.engine.connect() as conn:
                table_columns = conn.execute(
                    text(
                        f"""
                        SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '{TABLE_NAME}'
                    """
                    )
                ).fetchall()
                logger.info(f"Fetched table columns: {table_columns}")
                table_column_names = [col[0] for col in table_columns]

            # Filter the DataFrame to include only columns present in the table
            df = df[table_column_names]

            # Save the filtered DataFrame to the database
            with self.engine.connect() as conn:
                with conn.begin():
                    df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
                    logger.info(f"Inserted {len(df)} records into {TABLE_NAME}")
                    return len(df)
        except SQLAlchemyError as e:
            logger.error(f"Error inserting records: {e}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.engine:
            self.engine.dispose()
            logger.info("Database engine disposed")


class APIDataFetcher:
    """Handles API requests and data retrieval."""

    def __init__(self, url: str, headers: Dict[str, str], limit: int = 100):
        self.base_url = url.split("&offset=")[0] if "&offset=" in url else url
        self.headers = headers
        self.limit = limit
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def fetch_data(self) -> List[Dict]:
        """Fetch all data from the API."""
        all_items = []
        offset = 0

        while True:
            url = f"{self.base_url}&offset={offset}&limit={self.limit}"
            try:
                response = requests.get(url, headers=self.headers, verify=False)
                response.raise_for_status()
                data = response.json()
                items = data.get("data", [])
                total_items = data.get("totalItems", 0)

                logger.info(
                    f"Fetched {len(items)} items from offset {offset} (totalItems: {total_items})"
                )
                all_items.extend(items)

                if offset + len(items) >= total_items or not items:
                    logger.info(f"Completed fetching {len(all_items)} total items")
                    break

                offset += self.limit
            except requests.RequestException as e:
                logger.error(f"Error fetching API data at offset {offset}: {e}")
                raise
            except ValueError as e:
                logger.error(f"Error parsing JSON response at offset {offset}: {e}")
                raise

        return all_items


class DataProcessor:
    """Handles data transformation and preparation."""

    @staticmethod
    def convert_datetime(dt_str: Optional[str]) -> Optional[str]:
        """Convert ISO 8601 datetime to MM/DD/YYYY HH:MM:SS format."""
        if not dt_str:
            return None
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            return dt.strftime("%m/%d/%Y %H:%M:%S")
        except ValueError as e:
            logger.warning(f"Invalid datetime format: {dt_str}, error: {e}")
            return None

    @staticmethod
    def prepare_dataframe(
        items: List[Dict], datetime_fields: List[str]
    ) -> pd.DataFrame:
        """Prepare DataFrame with converted datetimes and proper types."""
        df = pd.DataFrame(items)
        for field in datetime_fields:
            if field in df.columns:
                df[field] = df[field].apply(DataProcessor.convert_datetime)
        if "cloudPool" in df.columns:
            # Correct the type check for elements in the cloudPool column
            df["cloudPoolUuid"] = df["cloudPool"].apply(
                lambda x: x.get("uuid") if isinstance(x, dict) else None
            )
            df["cloudPoolName"] = df["cloudPool"].apply(
                lambda x: x.get("name") if isinstance(x, dict) else None
            )
            df["cloudPoolDescription"] = df["cloudPool"].apply(
                lambda x: x.get("description") if isinstance(x, dict) else None
            )
            df["cloudPoolChildOfGlobalPool"] = df["cloudPool"].apply(
                lambda x: x.get("childOfGlobalPool") if isinstance(x, dict) else None
            )
            df.drop(columns=["cloudPool"], inplace=True)

        # Ensure all columns are of supported types
        for col in df.columns:
            df[col] = df[col].apply(
                lambda x: str(x) if isinstance(x, (dict, list)) else x
            )
        logger.info(f"Prepared DataFrame with {len(df)} records")
        return df


def main():
    """Main execution function."""
    try:
        db_manager = DatabaseManager(SERVER, DB, DRIVER)
        api_fetcher = APIDataFetcher(API_URL, HEADERS)

        with db_manager:
            if not db_manager.test_connection():
                return
            db_manager.create_table()
            items = api_fetcher.fetch_data()
            if not items:
                logger.info("No items to process")
                return
            df = DataProcessor.prepare_dataframe(items, DATETIME_FIELDS)
            count = db_manager.save_dataframe(df)
            logger.info(f"Successfully processed and saved {count} records")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
