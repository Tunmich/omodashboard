# core/threading_helper.py
import threading
import time
import logging


class SafeThread:
    def __init__(self, name, target, interval=1.0, daemon=True):
        self.name = name
        self.target = target
        self.interval = interval
        self.thread = threading.Thread(target=self.run, name=name, daemon=daemon)
        self._stop_event = threading.Event()
        self.logger = logging.getLogger(name)

    def run(self):
        self.logger.info(f"Thread {self.name} started.")
        while not self._stop_event.is_set():
            try:
                self.target()
            except Exception as e:
                self.logger.exception(f"Error in thread {self.name}: {e}")
            time.sleep(self.interval)
        self.logger.info(f"Thread {self.name} stopped.")

    def start(self):
        self._stop_event.clear()
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self.run, name=self.name, daemon=True)
            self.thread.start()

    def stop(self):
        self.logger.info(f"Stopping thread {self.name}...")
        self._stop_event.set()
        self.thread.join()

    def is_alive(self):
        return self.thread.is_alive()
