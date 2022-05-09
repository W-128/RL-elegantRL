import datetime
import time
from threading import Thread


class Env:
    task_num = 0

    def step(self, submit_task_num):
        self.task_num -= submit_task_num
        print('do action:提交' + str(submit_task_num) + '个任务，剩余' + \
              str(self.task_num) + '个任务' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(1)
        print('next state:现在有' + str(self.task_num) + '个任务' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return self.task_num

    def produce_task(self, task_id, rtl):
        print('提交任务：task_id=' + str(task_id) + ' rtl=' + str(rtl))
        self.task_num += 1

    def get_state(self):
        return self.task_num
