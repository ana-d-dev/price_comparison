from dotenv import load_dotenv
import requests
import os



load_dotenv()
NOTIFIER = os.getenv("NOTIFIER")


def send_notification(message: str) -> None:
    """
    Send a notification via ntfy.
    """
    if not NOTIFIER:
        return  # no topic configured

    try:
        requests.post(
            f"https://ntfy.sh/{NOTIFIER}",
            data=message.encode(),
            timeout=5,
        )
    except requests.RequestException:
        pass
