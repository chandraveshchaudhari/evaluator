def now_timestamp():
    """Get the current timestamp as a formatted string."""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

