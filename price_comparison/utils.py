from price_comparison.logger_config import setup_logger
import os

logger = setup_logger('utils')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAST_UPDATE_FILE = os.path.join(BASE_DIR, 'lastupdate.txt')

def last_update():
    try:
        with open(LAST_UPDATE_FILE, 'r') as f:
            return f.read().strip()

    except FileNotFoundError:
        logger.error('File not found.')
        return 'Unknown'
