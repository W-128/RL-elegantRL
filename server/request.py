import logging
import time
import datetime
from my_log import get_logger


class Request:
    logger = get_logger('request', logging.INFO)

    def __init__(self, start_time, task_id, rtl, event) -> None:
        self.start_time = start_time
        self.task_id = task_id
        self.rtl = rtl
        self.event = event
        self.is_success = True

    def set_wait_time(self, wait_time):
        self.wait_time = wait_time

    def run(self):
        time.sleep(0.9)
        end_time = datetime.datetime.now().timestamp()
        delta_ms = int((end_time - self.start_time) * 1000)
        # logger.info("rtllevel:" + str(self.rtl) + " request response time: " + str(delta_ms) + "ms")
        self.logger.info("rtllevel:" + str(self.rtl) + " wait time: " + str(self.wait_time) + "ms")
