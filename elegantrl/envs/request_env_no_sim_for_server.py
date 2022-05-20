import sys
import os
import datetime
from concurrent.futures import ThreadPoolExecutor
import queue

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath + '/my_common')


class RequestEnvNoSimForServer:

    def __init__(self, task_num, action_is_probability):
        if task_num == 2:
            self.task_num = 2
            # 引擎能承受的单位时间最大并发量
            self.threshold = 90
        if task_num == 1:
            self.task_num = 1
            # 引擎能承受的单位时间最大并发量
            self.threshold = 45
        self.threshold = 45
        self.N = 20
        self.state_dim = self.N + 1
        self.action_dim = self.state_dim
        self.active_request_group_by_remaining_time_list = []
        for i in range(self.state_dim):
            self.active_request_group_by_remaining_time_list.append(queue.Queue())
        self.action_is_probability = action_is_probability
        self.worker_thread_pool = ThreadPoolExecutor(max_workers=50)

    def action_probability_to_number(self, probability_action):
        # number_action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        number_action = [0] * len(probability_action)
        for index in range(len(probability_action)):
            number_action[index] = int(
                round(probability_action[index] * self.active_request_group_by_remaining_time_list[index].qsize(), 0))
        if number_action[0] < self.active_request_group_by_remaining_time_list[0].qsize():
            number_action[0] = min(self.threshold, self.active_request_group_by_remaining_time_list[0].qsize())
        return number_action

    def do_action(self, action):
        if self.action_is_probability:
            action = self.action_probability_to_number(action)
        now_time = datetime.datetime.now()
        for remaining_time in range(self.action_dim):
            # 提交任务
            for j in range(int(action[remaining_time])):
                req = self.active_request_group_by_remaining_time_list[remaining_time].get()
                wait_time_ms = int((now_time.timestamp() - req.start_time) * 1000)
                req.set_wait_time(wait_time_ms)
                self.worker_thread_pool.submit(req.run)
                req.event.set()

        while (self.active_request_group_by_remaining_time_list[0].qsize()) != 0:
            req = self.active_request_group_by_remaining_time_list[0].get()
            req.is_success = False
            req.event.set()

        # print('更新前state：' + str(self.get_state()))
        self.active_request_group_by_remaining_time_list = self.active_request_group_by_remaining_time_list[1:]
        self.active_request_group_by_remaining_time_list.append(queue.Queue())
        # print('更新后state：' + str(self.get_state()))

    def produce(self, req):
        self.active_request_group_by_remaining_time_list[req.rtl - 1].put(req)

    def get_state(self):
        state = []
        for active_request_group_by_remaining_time in self.active_request_group_by_remaining_time_list:
            state.append(active_request_group_by_remaining_time.qsize())
        return state
