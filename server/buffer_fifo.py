import time
import datetime
import sys
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSimForServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from my_common.utils import get_logger
import queue
from request import Request

class BufferFIFO:
    BUFFER_FIFO_INSTANCE = None
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)
    queue = queue.Queue()
    request_threshold = 45
    worker_thread_pool = ThreadPoolExecutor(max_workers=50)

    def __init__(self) -> None:
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(func=self.advance_clock, trigger='interval', seconds=1)
        t=Thread(target=self.scheduler.start)
        t.start()

    @staticmethod
    def get_instance():
        if BufferFIFO.BUFFER_FIFO_INSTANCE is None:
            BufferFIFO.lock.acquire()
            if BufferFIFO.BUFFER_FIFO_INSTANCE is None:
                BufferFIFO.BUFFER_FIFO_INSTANCE = BufferFIFO()
            BufferFIFO.lock.release()
        return BufferFIFO.BUFFER_FIFO_INSTANCE

    def produce(self, req):
        self.queue.put(req)

    def advance_clock(self):
        remain_submit_times = self.request_threshold
        while (remain_submit_times > 0):
            if self.queue.qsize != 0:
                req = self.queue.get()
                submit_time_ms = datetime.datetime.now().timestamp()
                req.set_submit_time(submit_time_ms)
                self.worker_thread_pool.submit(req.run)
                remain_submit_times = remain_submit_times - 1
                req.event.set()
            else:
                break

