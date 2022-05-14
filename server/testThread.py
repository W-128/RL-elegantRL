import time
import datetime
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


class NewThread(Thread):

    def __init__(self):
        Thread.__init__(self)  # 必须步骤

    def run(self):  # 入口是名字为run的方法
        print("开始做一个任务啦")
        time.sleep(1)  # 用time.sleep模拟任务耗时
        print("这个任务结束啦")

    def get_result(self):
        threading.Thread.join(self)  # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None


def task():
    print('env中生产任务 ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def exe_task(event):
    time.sleep(2)
    executor = ThreadPoolExecutor(1)
    executor.submit(task).result()
    event.set()


# if __name__ == '__main__':
#     print("这里是主线程 " + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
#     event = threading.Event()
#     exe_task(event)
#     event.wait()
#     print("主线程结束了" + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

time1 = datetime.datetime.now().timestamp()
time.sleep(0.9)
time2 = datetime.datetime.now().timestamp()
time2 += 1
print(time2 - time1)
