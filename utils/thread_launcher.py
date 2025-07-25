import threading
import logging
import time

def thread_wrapper(target_func, name="Unnamed"):
    def wrapped():
        while True:
            try:
                target_func()
            except Exception as e:
                logging.error(f"🔥 {name} thread crashed: {e}")
                time.sleep(10)
    thread = threading.Thread(target=wrapped, name=name, daemon=True)
    thread.start()
    logging.info(f"🧵 Thread launched: {name}")

THREAD_STATUS = {}

def thread_wrapper(target_func, name="Unnamed"):
    def wrapped():
        retries = 0
        started = time.time()
        while True:
            try:
                THREAD_STATUS[name] = {
                    "retries": retries,
                    "uptime": time.time() - started,
                    "active": True
                }
                target_func()
            except Exception as e:
                retries += 1
                THREAD_STATUS[name] = {
                    "retries": retries,
                    "uptime": time.time() - started,
                    "active": False,
                    "last_error": str(e)
                }
                logging.error(f"🔥 {name} thread crashed (retry #{retries}): {e}")
                time.sleep(10)

    thread = threading.Thread(target=wrapped, name=name, daemon=True)
    thread.start()
    logging.info(f"🧵 Thread launched: {name}")
