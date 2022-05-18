import time
import datetime
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from test_env import Env
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import queue
from request import Request
import logging


class BufferFIFO:
    BUFFER_FIFO_INSTANCE = None
    env = None
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)
    queue = queue.Queue()
    request_threshold = 45
    worker_thread_pool = ThreadPoolExecutor(max_workers=50)

    def __init__(self) -> None:
        self.env = Env()
        t = Thread(target=self.consume)
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

    def consume(self):
        while True:
            remain_submit_times = self.request_threshold
            while (remain_submit_times > 0):
                if self.queue.qsize != 0:
                    req = self.queue.get()
                    wait_time_ms = int((datetime.datetime.now().timestamp() - req.start_time) * 1000)
                    req.set_wait_time(wait_time_ms)
                    if wait_time_ms > req.rtl * 1000:
                        req.is_success = False
                    else:
                        self.worker_thread_pool.submit(req.run)
                        remain_submit_times = remain_submit_times - 1
                    req.event.set()
                else:
                    break
            time.sleep(1)
