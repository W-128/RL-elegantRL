import time
import datetime
import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSimForServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from baseline.agent import EDF
from my_log import get_logger
import logging


class BufferEDF:
    BUFFER_INSTANCE = None
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)
    worker_thread_pool = ThreadPoolExecutor(max_workers=50)
    logger = get_logger('buffer_edf', logging.INFO)

    def __init__(self) -> None:
        self.env = RequestEnvNoSimForServer(action_is_probability=False)
        self.agent = EDF(self.env.action_dim)
        t = Thread(target=self.consume)
        t.start()

    @staticmethod
    def get_instance():
        if BufferEDF.BUFFER_INSTANCE is None:
            BufferEDF.lock.acquire()
            if BufferEDF.BUFFER_INSTANCE is None:
                BufferEDF.BUFFER_INSTANCE = BufferEDF()
            BufferEDF.lock.release()
        return BufferEDF.BUFFER_INSTANCE

    def produce(self, req):
        self.env.produce(req)

    def consume(self):
        while True:
            # 获取环境值
            # t1 = datetime.datetime.now().timestamp()
            state = self.env.get_state()
            self.logger.debug('state' + str(state))
            # actor得到action
            action = self.agent.predict(state, self.env.threshold)
            self.logger.debug('action' + str(action))
            self.env.do_action(action)
            # t2 = datetime.datetime.now().timestamp()
            # print('一次交互的用时：' + str(t2 - t1) + 's')
            time.sleep(1)
