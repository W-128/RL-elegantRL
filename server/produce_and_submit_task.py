import time
import schedule
import datetime
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from test import Env
from threading import Thread

env = None
start_env = False


def produce(task_id, rtl):
    global env
    global start_env
    if env is None:
        env = Env()
        start_env = True
    env.produce_task(task_id, rtl)


# def consume_job():
# env step 给出state
# actor决策提交哪些任务

# def submit_task():
#     schedule.every(1).seconds.do(produce_job)
#     while True:
#         schedule.run_pending()

# def submit_request_continuously():
#     schedule.every(1).seconds.do(produce_job)
#
#     class ScheduleThread(threading.Thread):
#         @classmethod
#         def run(cls):
#             while True:
#                 schedule.run_pending()
#
#     continuous_thread = ScheduleThread()
#     continuous_thread.start()

def env_step(action):
    t1 = Thread(target=env.step, args=action)
    t1.start()


# if __name__ == '__main__':
#     print("这里是主线程" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     env = Env()
#     t1 = Thread(target=env.step)
#     t1.start()
#     env.add_i()
#     print("主线程让i+1 " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     env.add_i()
#     print("主线程让i+1 " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     time.sleep(1)

def actor_predict(state):
    return 1


if start_env:
    state = env.get_state()
    while True:
        action = actor_predict(state)
        next_state = env_step(action)
        state = next_state
