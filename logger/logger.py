import logging
import os
from datetime import datetime, timezone

LOGS_DIR = os.path.join('.', 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)


def setup_logger(log_file="app.log"):
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


utc_now = datetime.now(timezone.utc)
current_date = utc_now.strftime("%Y-%m-%d")
log_file_name = os.path.join(LOGS_DIR, f'app_{current_date}.log')
logger = setup_logger(log_file_name)
