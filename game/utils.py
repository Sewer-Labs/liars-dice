def clear_log_file():
    """Function to clear the log file."""
    with open('gamelogs.txt', 'w'):
        pass  # Opening the file in write mode ('w') clears its contents
