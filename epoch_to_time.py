from datetime import datetime

def convert_epoch_to_human_readable(epoch_time, timezone=None):
    """
    Converts epoch time to a human-readable date and time format.
    
    Args:
        epoch_time (int or float): The epoch timestamp to convert.
        timezone (str, optional): A timezone name, like 'UTC' or 'Asia/Kolkata'. Defaults to None (local time).
    
    Returns:
        str: The human-readable date and time string.
    """
    try:
        if timezone is None:
            # Convert to local time if no timezone is provided
            dt = datetime.fromtimestamp(epoch_time)
        else:
            import pytz
            tz = pytz.timezone(timezone)
            dt = datetime.fromtimestamp(epoch_time, tz)
        
        # Format the datetime object to a human-readable string
        human_readable = dt.strftime("%Y-%m-%d %H:%M:%S")
        return human_readable
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    # Example usage
    epoch = input("Enter the epoch time (in seconds): ").strip()
    
    try:
        epoch_time = float(epoch)
        # Optional: Specify a timezone if needed
        timezone = input("Enter timezone (leave blank for local time): ").strip() or None
        
        result = convert_epoch_to_human_readable(epoch_time, timezone)
        print(f"Human-readable format: {result}")
    except ValueError:
        print("Invalid epoch time. Please enter a valid number.")
