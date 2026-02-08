from price_comparison.notify import send_notification
from pathlib import Path
from loguru import logger


def notify_on_error(msg):
    try:
        text = (
                f"{msg.record['name']}\n"
                f"{msg.record['level'].name}\n"
                f"{msg.record['message']}"
            )
        send_notification(text)
    except Exception:
        pass


def setup_logger(name: str):
    """
    Configure Loguru logger:
    - write logs to file
    - send notifications on ERROR and above
    """
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"{name}.log"

    # Remove default handlers to avoid duplicate logs
    logger.remove()

    # File logging (everything)
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:DD-MM-YYYY HH:mm:ss} | {level:<8} | {file}:{line} - {message}",
    )

    # Notifications (ERROR and above only)
    logger.add(
        notify_on_error,
        level="ERROR",
    )

    return logger
