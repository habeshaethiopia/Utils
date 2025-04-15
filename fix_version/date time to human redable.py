from datetime import datetime

data = {
    "id": 950,
    "startedDateTime": "2025-04-10T15:36:27.8027568",
    "createdDateTime": "2025-04-10T15:36:13.1449573",
    "scanStatsUpdatedDateTime": "2025-04-10T15:41:05.7890637",
    "scanStatusDateTime": "2025-04-10T15:41:35.4517685",
    "publishStatusDateTime": "2025-04-10T16:14:08.3608918",
    "purgeDateTime": None,
}


# Function to convert datetime strings to "Apr 10 2025 03:36 PM"
def convert_datetime_fields(obj):
    for key, value in obj.items():
        if isinstance(value, str) and "T" in value and ":" in value:
            try:
                dt = datetime.fromisoformat(value)
                obj[key] = dt.strftime("%b %d %Y %I:%M %p")
            except ValueError:
                pass
    return obj


# Convert the datetime fields
converted_data = convert_datetime_fields(data)
print(converted_data)
# Output the converted data
'''
{
    "id": 950,
    "startedDateTime": "Apr 10 2025 03:36 PM",
    "createdDateTime": "Apr 10 2025 03:36 PM",
    "scanStatsUpdatedDateTime": "Apr 10 2025 03:41 PM",
    "scanStatusDateTime": "Apr 10 2025 03:41 PM",
    "publishStatusDateTime": "Apr 10 2025 04:14 PM",
    "purgeDateTime": None,
}
'''