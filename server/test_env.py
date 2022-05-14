import datetime
import imp
import time
from threading import Thread
import queue
from request import Request


class Env:
    queue = queue.Queue()

    def step(self, submit_task_num):
        for i in range(submit_task_num):
            request = self.queue.get()
            print('env中do action:提交任务, task_id=' + request.task_id + ' rtl=' + request.rtl + ' ' +
                  datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            request.event.set()
        time.sleep(1)
        print('env中next state:现在有' + str(self.queue.qsize()) + '个任务 ' +
              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return self.queue.qsize()

    def produce_task(self, task_id, rtl, event):
        print('env中生产任务：task_id=' + str(task_id) + ' rtl=' + str(rtl) + ' ' +
              datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        request = Request(task_id, rtl, event)
        self.queue.put(request)

    def get_state(self):
        return self.queue.qsize()
