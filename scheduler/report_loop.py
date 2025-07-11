import time
import schedule
import logging
from utils.logger_config import setup_logger
setup_logger()
from alerts.telegram_reporter import send_hourly_report

schedule.every().hour.at(":00").do(send_hourly_report)

print("📊 Auto-report loop active.")
while True:
    schedule.run_pending()
    time.sleep(60)