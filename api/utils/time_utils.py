from datetime import datetime, timezone


def get_current_utc_datetime():
    """
    Returns the current datetime in UTC formatted as an ISO 8601 string.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
