import time
import datetime
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from test_env import Env
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


class Buffer:
    BUFFER_INSTANCE = None
    env = None
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)

    def __init__(self) -> None:
        self.env = Env()
        t = Thread(target=self.consume)
        t.start()

    @staticmethod
    def get_instance():
        if Buffer.BUFFER_INSTANCE is None:
            Buffer.lock.acquire()
            if Buffer.BUFFER_INSTANCE is None:
                Buffer.BUFFER_INSTANCE = Buffer()
            Buffer.lock.release()
        return Buffer.BUFFER_INSTANCE

    def produce(self, task_id, rtl, event):
        self.env.produce_task(task_id, rtl, event)

    def consume(self):
        state = self.env.get_state()
        while True:
            action = self.actor_predict(state)
            next_state = self.env_step(action)
            state = next_state

    def actor_predict(self, state):
        if state != 0:
            return 1
        return 0

    def env_step(self, action):
        return self.boss_thread_pool.submit(self.env.step, action).result()


# print("主线程，生产任务, task_id:1, rtl=1" +
#       datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# Buffer.get_instance().produce('1', '1')
# time.sleep(1)
# print("主线程，生产任务, task_id:2, rtl=2" +
#       datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# Buffer.get_instance().produce('2', '2')
# print("主线程，生产任务, task_id:3, rtl=3" +
#       datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
# Buffer.get_instance().produce('3', '3')
# time.sleep(1)
# time.sleep(1)
