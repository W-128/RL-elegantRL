import sys
import os
import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import queue

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath)

from bucket import Bucket
import logging
from my_common.utils import get_logger


class RequestEnvNoSimForServer:
    logger = get_logger('RequestEnvNoSimForServer', logging.INFO)

    def __init__(self, task_num, action_is_probability):
        self.unserved_time_up_bound=20
        self.current_time = datetime.datetime.now().replace(microsecond=0)
        self.state_record = []
        if task_num == 2:
            self.task_num = 2
            # 引擎能承受的单位时间最大并发量
            self.threshold = 90
        if task_num == 1:
            self.task_num = 1
            # 引擎能承受的单位时间最大并发量
            self.threshold = 45
        self.N = 20
        self.state_dim = self.N + 1
        self.action_dim = self.state_dim
        # key=expire_time
        # value= expire_time=key的bucket
        self.bucket_dic = {}
        self.action_is_probability = action_is_probability
        self.worker_thread_pool = ThreadPoolExecutor(max_workers=60)
        self.violate_request_queue = queue.Queue()

    # 全局时钟向前一步
    def advance_clock(self):
        current_time = datetime.datetime.now()
        if current_time >= self.current_time + timedelta(seconds=1):
            self.current_time = current_time.replace(microsecond=0)
        RequestEnvNoSimForServer.logger.debug('全局时钟现在的时间是: ' + str(self.current_time))

    def action_probability_to_number(self, probability_action):
        # number_action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        number_action = [0] * len(probability_action)
        for index in range(len(probability_action)):
            number_action[index] = int(round(probability_action[index] * self.state_record[index], 0))
        if number_action[0] < self.state_record[0]:
            number_action[0] = min(self.threshold, self.state_record[0])
        return number_action

    def do_action(self, action):
        if self.action_is_probability:
            action = self.action_probability_to_number(action)

        for remaining_time in range(self.action_dim):
            # 提交任务
            for j in range(action[remaining_time]):
                req = self.bucket_dic[self.current_time + timedelta(seconds=remaining_time)].get_a_request()
                submit_time_ms = datetime.datetime.now().timestamp()
                req.set_submit_time(submit_time_ms)
                self.worker_thread_pool.submit(req.run)
                req.event.set()

        # 提交量不足阈值时提交已经违约的
        if np.sum(action) < self.threshold:
            remain_submit_times = self.threshold - np.sum(action)
            while (remain_submit_times != 0):
                if self.violate_request_queue.qsize() == 0:
                    break
                else:
                    req = self.violate_request_queue.get()
                    submit_time_ms = datetime.datetime.now().timestamp()
                    if submit_time_ms - req.start_time <= self.unserved_time_up_bound:
                        req.set_submit_time(submit_time_ms)
                        self.worker_thread_pool.submit(req.run)
                        remain_submit_times -= 1
                    else:
                        req.is_success = False
                    req.event.set()

        del_expire_time_list = []
        for expire_time in self.bucket_dic:
            if expire_time <= self.current_time:
                while self.bucket_dic[expire_time].get_q_size() != 0:
                    req = self.bucket_dic[expire_time].get_a_request()
                    self.violate_request_queue.put(req)
                del_expire_time_list.append(expire_time)
        for del_expire_time in del_expire_time_list:
            bucket = self.bucket_dic.pop(del_expire_time)
            del bucket

    def produce(self, req):
        expire_time = self.current_time + timedelta(seconds=req.rtl)
        if expire_time in self.bucket_dic:
            self.bucket_dic[expire_time].add_request(req)
        else:
            self.bucket_dic[expire_time] = Bucket(expire_time)
            self.bucket_dic[expire_time].add_request(req)

    def get_state(self):
        state = []
        for index in range(self.state_dim):
            if (self.current_time + timedelta(seconds=index)) in self.bucket_dic:
                state.append(self.bucket_dic[self.current_time + timedelta(seconds=index)].get_q_size())
            else:
                state.append(0)
        self.state_record = state
        return state

    def get_state_for_RL(self):
        state = []
        for index in range(self.state_dim):
            if (self.current_time + timedelta(seconds=index)) in self.bucket_dic:
                state.append(self.bucket_dic[self.current_time + timedelta(seconds=index)].get_q_size())
            else:
                state.append(0)
        self.state_record = state
        return np.asarray(state, dtype=np.float32) / self.threshold
