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
from request_env_no_sim_for_server import RequestEnvNoSimForServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from baseline.agent import EDFSubmitThreshold
from my_common.utils import get_logger


class BufferEDFThreshold:
    # 流程的任务数
    task_num = 1
    BUFFER_INSTANCE = None
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)
    logger = get_logger('buffer_edf_threshold', logging.INFO)

    def __init__(self) -> None:
        self.env = RequestEnvNoSimForServer(BufferEDFThreshold.task_num, action_is_probability=False)
        self.agent = EDFSubmitThreshold(self.env.action_dim)
        self.worker_thread_pool = ThreadPoolExecutor(max_workers=10)
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(func=self.advance_clock, trigger='interval', seconds=1)
        t=Thread(target=self.scheduler.start)
        t.start()

    @staticmethod
    def get_instance():
        if BufferEDFThreshold.BUFFER_INSTANCE is None:
            BufferEDFThreshold.lock.acquire()
            if BufferEDFThreshold.BUFFER_INSTANCE is None:
                BufferEDFThreshold.BUFFER_INSTANCE = BufferEDFThreshold()
            BufferEDFThreshold.lock.release()
        return BufferEDFThreshold.BUFFER_INSTANCE

    def produce(self, req):
        self.env.produce(req)

    def advance_clock(self):
        self.env.advance_clock()
        self.worker_thread_pool.submit(self.consume)

    def consume(self):
        state = self.env.get_state()
        self.logger.debug('state' + str(state))
        # actor得到action
        action = self.agent.predict(state, self.env.threshold)
        self.logger.debug('action' + str(action))
        self.env.do_action(action)
