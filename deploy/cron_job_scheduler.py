import schedule
import time
import subprocess
import logging
import configparser
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="cron_job.log",  # Log to a file
    filemode="a",  # Append to the log file
)
logger = logging.getLogger(__name__)

# Path to the config file
CONFIG_FILE = "config.ini"


def read_last_seen_epoch():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return int(config["LastSeen"]["last_seen_epoch"])


def write_last_seen_epoch(epoch):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config["LastSeen"]["last_seen_epoch"] = str(epoch)
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)


def run_fetch_data():
    try:
        logger.info("Starting run_fetch_data function.")
        current_epoch = int(datetime.now().timestamp())
        # Read the last seen epoch
        last_seen_epoch = read_last_seen_epoch()
        print(f"time stamp {str(last_seen_epoch)}-{str(current_epoch)}")
        logger.info(f"Last seen epoch: {last_seen_epoch}")

        # Run the script with the last seen epoch argument
        logger.info("Executing version_issue_processor.py")
        subprocess.run(["python", "version_issue_processor.py"], check=True)
        logger.info("excuting tenable.py with last seen epoch.")
        subprocess.run(
            ["python", "tenable.py", f"{str(last_seen_epoch)}-{str(current_epoch)}"],
            check=True,
        )

        logger.info("version_issue_processor.py executed successfully.")

        # Update the last seen epoch to the current time
        write_last_seen_epoch(current_epoch)
        logger.info(f"Updated last seen epoch to: {current_epoch}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing version_issue_processor.py: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        logger.info("Finished run_fetch_data function.")


# Schedule the job to run every day at 2 AM
# schedule.every().day.at("02:00").do(run_fetch_data)
# Run the job every 5 seconds for testing purposes
schedule.every(2).seconds.do(run_fetch_data)
schedule.every().second.do(run_fetch_data)
logger.info("Cron job scheduler started. Waiting for the scheduled time...")

# Keep the script running to execute scheduled tasks
while True:
    schedule.run_pending()
    time.sleep(1)
