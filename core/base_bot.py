# core/base_bot.py
import logging
import threading
import time


class BaseBot:
    def __init__(self, name: str):
        self.name = name
        self.thread = None
        self._stop_event = threading.Event()
        self.logger = logging.getLogger(self.name)

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self.logger.info(f"Starting {self.name}...")
            self._stop_event.clear()
            self.thread = threading.Thread(target=self.run, name=self.name, daemon=True)
            self.thread.start()
        else:
            self.logger.warning(f"{self.name} is already running.")

    def stop(self):
        self.logger.info(f"Stopping {self.name}...")
        self._stop_event.set()
        if self.thread:
            self.thread.join()

    def is_running(self):
        return self.thread is not None and self.thread.is_alive()

    def run(self):
        raise NotImplementedError("You must implement the run() method in your subclass.")

    def should_stop(self):
        return self._stop_event.is_set()