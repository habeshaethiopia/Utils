import requests
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API Configuration
API_URL = "https://aweascua18.fema.net/api/v2/scans/scan-summary-list?searchText=&startedOnStartDate=&startedOnEndDate=&scanStatusType=&publishStatusType=&orderBy=&orderByDirection=&offset=0&limit=100"
HEADERS = {
    "accept": "application/json",
    "Authorization": "FortifyToken xxxxx"
}

# Database Configuration
SERVER = r"AWEASC2A2\SQLEXPRESS"
DB = "Tenable_SC"
DRIVER = "ODBC Driver 18 for SQL Server"
TABLE_NAME = "scan_summaries"

# Datetime fields to convert
DATETIME_FIELDS = [
    "startedDateTime",
    "createdDateTime",
    "scanStatsUpdatedDateTime",
    "scanStatusDateTime",
    "publishStatusDateTime",
    "purgeDateTime"
]

class DatabaseManager:
    """Handles database connections and operations."""
    
    def __init__(self, server: str, db: str, driver: str):
        # self.connection_string = f"mssql+pyodbc://{server}/{db}?trusted_connection=yes&driver={driver}"
        self.connection_string = f"sqlite:///{db}.db"
        self.engine = None
        
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
            with self.engine.connect() as connection:
                logger.info("Database connection successful")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Database connection failed: {e}")
            return False
    
    def create_table(self) -> None:
        """Create scan_summaries table if it doesn't exist."""
        metadata = MetaData()
        
        scan_summaries = Table(
            TABLE_NAME, metadata,
            Column('id', Integer, primary_key=True),
            Column('scanType', Integer),
            Column('scanTypeDescription', NVARCHAR(100)),
            Column('submitForAudit', Boolean),
            Column('name', NVARCHAR(255)),
            Column('url', NVARCHAR(500)),
            Column('hasSiteAuthentication', Boolean),
            Column('hasNetworkAuthentication', Boolean),
            Column('hasAPIAuthCredentials', Boolean),
            Column('startedDateTime', DateTime),
            Column('createdDateTime', DateTime),
            Column('duration', Integer),
            Column('requestCount', Integer),
            Column('failedRequestCount', Integer),
            Column('macroPlaybackCount', Integer),
            Column('kilobytesSent', Integer),
            Column('kilobytesReceived', Integer),
            Column('criticalCount', Integer),
            Column('highCount', Integer),
            Column('mediumCount', Integer),
            Column('lowCount', Integer),
            Column('scanStatusType', Integer),
            Column('scanStatusTypeDescription', NVARCHAR(100)),
            Column('scanStatusReasonType', Integer),
            Column('scanStatusReasonTypeDescription', NVARCHAR(100)),
            Column('publishStatusType', Integer),
            Column('publishStatusTypeDescription', NVARCHAR(100)),
            Column('publishStatusReasonType', Integer),
            Column('publishStatusReasonTypeDescription', NVARCHAR(100)),
            Column('applicationId', Integer),
            Column('applicationName', NVARCHAR(255)),
            Column('applicationVersionId', Integer),
            Column('applicationVersionName', NVARCHAR(255)),
            Column('scannerId', Integer),
            Column('scannerName', NVARCHAR(100)),
            Column('scannerStatusType', Integer),
            Column('scannerStatusTypeDescription', NVARCHAR(100)),
            Column('scannerIsEnabled', Boolean),
            Column('scannerPoolId', Integer),
            Column('scannerPoolName', NVARCHAR(100)),
            Column('webInspectScanId', UNIQUEIDENTIFIER),
            Column('scanStatsUpdatedDateTime', DateTime),
            Column('scanStatusDateTime', DateTime),
            Column('publishStatusDateTime', DateTime),
            Column('scanScheduleId', Integer, nullable=True),
            Column('scanScheduleName', NVARCHAR(255)),
            Column('useAssignedScannerOnly', Boolean),
            Column('policyId', UNIQUEIDENTIFIER),
            Column('policyName', NVARCHAR(100)),
            Column('hasScanResults', Boolean),
            Column('hasScanLogs', Boolean),
            Column('hasSiteTree', Boolean),
            Column('hasFPR', Boolean),
            Column('webInspectSettingsXmlStatusType', Integer),
            Column('webInspectSettingsXmlStatusTypeDescription', NVARCHAR(100)),
            Column('apiDefinitionType', NVARCHAR(100), nullable=True),
            Column('apiDefinitionTypeDescription', NVARCHAR(255)),
            Column('scanPriority', Integer),
            Column('activeAlertsCount', Integer),
            Column('unacknowledgedAlertsCount', Integer),
            Column('useScannerScaling', Boolean),
            Column('purgeDateTime', DateTime),
            Column('scanFindingsStatusType', Integer),
            Column('scanFindingsStatusTypeDescription', NVARCHAR(100)),
            Column('hasSpaEvents', Boolean),
            Column('enableSASTCorrelation', Boolean),
            Column('isImported', Boolean),
            Column('hasDASTServiceLogs', Boolean),
            Column('fortifyConnectClientId', UNIQUEIDENTIFIER, nullable=True),
            Column('fortifyConnectClientName', NVARCHAR(255)),
            Column('fortifyConnectConnectionId', UNIQUEIDENTIFIER, nullable=True)
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
        """Save DataFrame to scan_summaries table."""
        try:
            with self.engine.connect() as conn:
                with conn.begin():
                    # Use pandas to_sql for efficient bulk insert
                    df.to_sql(TABLE_NAME, conn, if_exists='append', index=False)
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
    
    def __init__(self, url: str, headers: Dict[str, str]):
        self.url = url
        self.headers = headers
    
    def fetch_data(self) -> List[Dict]:
        """Fetch data from the API."""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            items = data.get('items', [])
            logger.info(f"Fetched {len(items)} items from API")
            return items
        except requests.RequestException as e:
            logger.error(f"Error fetching API data: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            raise

class DataProcessor:
    """Handles data transformation and preparation."""
    
    @staticmethod
    def convert_datetime(dt_str: Optional[str]) -> Optional[str]:
        """Convert ISO 8601 datetime to MM/DD/YYYY HH:MM:SS format."""
        if not dt_str:
            return None
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%m/%d/%Y %H:%M:%S")
        except ValueError as e:
            logger.warning(f"Invalid datetime format: {dt_str}, error: {e}")
            return None
    
    @staticmethod
    def prepare_dataframe(items: List[Dict], datetime_fields: List[str]) -> pd.DataFrame:
        """Prepare DataFrame with converted datetimes and proper types."""
        # Create DataFrame
        df = pd.DataFrame(items)
        
        # Convert datetime fields
        for field in datetime_fields:
            if field in df.columns:
                df[field] = df[field].apply(DataProcessor.convert_datetime)
        
        logger.info(f"Prepared DataFrame with {len(df)} records")
        return df

def main():
    """Main execution function."""
    try:
        # Initialize components
        db_manager = DatabaseManager(SERVER, DB, DRIVER)
        api_fetcher = APIDataFetcher(API_URL, HEADERS)
        
        with db_manager:
            # Test connection
            if not db_manager.test_connection():
                return
            
            # Create table
            db_manager.create_table()
            
            # Fetch API data
            items = api_fetcher.fetch_data()
            
            if not items:
                logger.info("No items to process")
                return
            
            # Process data
            df = DataProcessor.prepare_dataframe(items, DATETIME_FIELDS)
            
            # Save to database
            count = db_manager.save_dataframe(df)
            
            logger.info(f"Successfully processed and saved {count} records")
            
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    main()
    
            