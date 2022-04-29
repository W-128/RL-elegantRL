import sys
import os
import datetime
import numpy as np
import pandas as pd
import time
import csv

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath + '/my_common')

from my_common.get_data import get_arrive_time_request_dic
import math
import torch.nn as nn
import torch

# t=1000ms
TIME_UNIT = 1
TIME_UNIT_IN_ON_SECOND = int(1 / TIME_UNIT)
THRESHOLD = int(60 / TIME_UNIT_IN_ON_SECOND)
# 实时用的话，这个地方无法事先写好，只能每秒来append
# 现在先 直接从文件读取

# request=[request_id, arrive_time, rtl, remaining_time]
# success_request_list[request_id, arrive_time, rtl, wait_time]
REQUEST_ID_INDEX = 0
ARRIVE_TIME_INDEX = 1
RTL_INDEX = 2
REMAINING_TIME_INDEX = 3
WAIT_TIME_INDEX = 3

FRESH_TIME = 1

# t t的长度为TIME_UNIT
t = 0
curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  # 获取当前时间


def t_add_one():
    global t
    t = t + 1


def t_to_zero():
    global t
    t = 0


class RequestEnvNoSim:

    def __init__(self):
        # 奖励参数设置
        self.more_provision_penalty_scale = 0
        self.success_reward_scale = 1
        self.more_than_threshold_penalty_scale = -4
        self.fail_penalty_scale = -1
        self.beta = 1
        self.c = -1
        # action需要从概率到数量
        self.action_is_probability = True
        # 状态向量的维数=rtl的级别个数
        self.N = 5
        # state=(剩余时间为0的请求个数,...,剩余时间为5的请求个数)
        self.state_dim = self.N + 1
        # [剩余时间为0s的请求列表,剩余时间为1s...,剩余时间为5s的请求列表]
        # active_request_group_by_remaining_time_list是中间变量，随时间推移会有remainingTime的改变
        self.active_request_group_by_remaining_time_list = []
        for i in range(self.state_dim):
            self.active_request_group_by_remaining_time_list.append([])
        self.state_record = []
        # 动作空间维数 == 状态向量的维数
        # action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        self.action_dim = self.state_dim
        # [0,1,...,5]
        self.action_list = []
        for i in range(self.action_dim - 1):
            self.action_list.append(str(i))
        self.success_request_list = []
        self.fail_request_list = []
        self.episode = 0
        # 引擎能承受的单位时间最大并发量
        self.threshold = THRESHOLD
        self.call_get_reward_times = 0
        self.invalid_action_times = 0
        self.need_evaluate_env_correct = False
        # 测试阶段将该值置为true
        self.invalid_action_optim = False
        '''
        arriveTime_request_dic:
        key=arriveTime
        value=arriveTime为key的request_in_dic列表
        request_in_dic的形式为[request_id, arrive_time, rtl]
        '''
        self.new_arrive_request_in_dic, self.arriveTime_request_dic = get_arrive_time_request_dic(
            ARRIVE_TIME_INDEX)
        # self.end_request_result_path = curr_path + '/success_request_list/' + curr_time + '/'
        # make_dir(self.end_request_result_path)

    def action_probability_to_number(self, probability_action):
        # number_action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        number_action = [0] * len(probability_action)
        for index in range(len(probability_action)):
            number_action[index] = int(
                round(
                    probability_action[index] *
                    len(self.active_request_group_by_remaining_time_list[index]
                        ), 0))
        if self.invalid_action_optim:
            if index == 0:
                if number_action[0] < len(self.active_request_group_by_remaining_time_list[0]):
                    number_action[0] = min(self.threshold, len(self.active_request_group_by_remaining_time_list[0]))
        return number_action

    # 返回奖励值和下一个状态
    def step(self, action):
        if self.action_is_probability:
            action = self.action_probability_to_number(action)
        # debug
        # print('action: ' + str(action))
        # print('t:' + str(t))

        reward = self.get_reward(action)
        # 环境更新
        done = self.update_env(action)

        # 验证环境正确性
        if done and self.need_evaluate_env_correct:
            print('环境正确性:' + str(self.is_correct()))

        # debug
        # print('active_request_list:' + str(self.active_request_group_by_remaining_time_list))

        return self.state_record, reward, done, {}

    # 确保action合法
    def update_env(self, action):
        # submit request
        # action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        for remaining_time in range(self.action_dim):
            for j in range(int(action[remaining_time])):
                # time_stamp = time.time()
                submit_index = np.random.choice(
                    self.active_request_group_by_remaining_time_list[
                        remaining_time].__len__())
                end_request = list(
                    self.active_request_group_by_remaining_time_list[
                        remaining_time][submit_index])
                # 把提交的任务从active_request_list中删除
                del self.active_request_group_by_remaining_time_list[
                    remaining_time][submit_index]
                end_request[
                    WAIT_TIME_INDEX] = t - end_request[ARRIVE_TIME_INDEX]
                self.success_request_list.append(end_request)

        t_add_one()

        # remaining_time==0且还留在active_request_group_by_remaining_time_list中的请求此时失败
        for active_request in self.active_request_group_by_remaining_time_list[
            0]:
            self.fail_request_list.append(list(active_request))
        self.active_request_group_by_remaining_time_list[0] = []

        # active_request_group_by_remaining_time_list 剩余时间要推移
        for i in range(
                1, len(self.active_request_group_by_remaining_time_list)):
            for active_request in self.active_request_group_by_remaining_time_list[i]:
                active_request[REMAINING_TIME_INDEX] = active_request[REMAINING_TIME_INDEX] - 1
                self.active_request_group_by_remaining_time_list[i - 1].append(
                    list(active_request))
            self.active_request_group_by_remaining_time_list[i] = []

        episode_done = False
        # 与真实环境交互的话这里需要更改
        new_arrive_request_list = self.get_new_arrive_request_list()
        # 更新active_request 为active_request_{t+1}
        for i in range(len(self.active_request_group_by_remaining_time_list)):
            self.active_request_group_by_remaining_time_list[i] = self.active_request_group_by_remaining_time_list[i] + \
                                                                  new_arrive_request_list[i]
        # 状态更新
        self.active_request_group_by_remaining_time_list_to_state()
        # 判断是否结束
        remaining_request_is_done = True
        for i in range(0, len(self.state_record) - 1):
            if self.state_record[i] != 0:
                remaining_request_is_done = False
        if t > np.max(list(self.arriveTime_request_dic.keys())
                      ) and remaining_request_is_done:
            episode_done = True
        # time.sleep(FRESH_TIME)
        return episode_done

    def get_reward(self, action):
        # action[提交剩余时间为0的请求数量, 提交剩余时间为1的请求数量, 提交剩余时间为N的请求数量]
        self.call_get_reward_times += 1

        # 超阈值惩罚
        more_than_threshold_penalty = 0
        if sum(action) > self.threshold:
            more_than_threshold_penalty = (sum(action) - self.threshold) / float(self.threshold)

        # 超供惩罚
        more_provision_penalty = 0
        for index in range(1, self.action_dim - 1):
            more_provision_penalty -= action[index] * index
        more_provision_penalty = more_provision_penalty / (self.threshold *
                                                           self.state_dim)

        # 成功奖励
        success_reward = 0
        for index in range(len(action)):
            success_reward += ((self.success_reward_scale - index * 0.1) * min(
                action[index], self.threshold)) / float(self.threshold)
        # 失败数量
        fail_num = 0
        if action[0] < len(self.active_request_group_by_remaining_time_list[0]):
            fail_num = (len(self.active_request_group_by_remaining_time_list[0]) - action[0]) / float(self.threshold)

        return success_reward \
               + self.fail_penalty_scale * fail_num \
               + self.more_provision_penalty_scale * more_provision_penalty \
               + self.more_than_threshold_penalty_scale * more_than_threshold_penalty

    # request_list -> state
    def active_request_group_by_remaining_time_list_to_state(self):
        state = []
        for active_request_group_by_remaining_time in self.active_request_group_by_remaining_time_list:
            state.append(len(active_request_group_by_remaining_time))
        self.state_record = state

    def is_correct(self):
        all_request_id_list = []
        for request_in_dic in self.new_arrive_request_in_dic:
            all_request_id_list.append(request_in_dic[REQUEST_ID_INDEX])
        all_request_after_episode_list = []
        all_request_id_after_episode_list = []
        for request in self.fail_request_list:
            all_request_after_episode_list.append(request)
            all_request_id_after_episode_list.append(request[REQUEST_ID_INDEX])
        for request in self.success_request_list:
            all_request_after_episode_list.append(request)
            all_request_id_after_episode_list.append(request[REQUEST_ID_INDEX])
        all_request_id_list.sort()
        all_request_id_after_episode_list.sort()
        return all_request_id_after_episode_list == all_request_id_list

    def get_success_rate(self):
        all_request_num = len(self.new_arrive_request_in_dic)
        return self.success_request_list.__len__() / all_request_num

    # def save_success_request(self):
    #     # success_request_list[request_id, arrive_time, rtl, wait_time]
    #     headers = ['request_id', 'arrive_time', 'rtl', 'wait_time']
    #     with open(self.end_request_result_path + 'success_request_list' + str(self.episode) + '.csv', 'w', newline='')as f:
    #         f_csv = csv.writer(f)
    #         f_csv.writerow(headers)
    #         f_csv.writerows(self.success_request_list)

    # 现在用t来表示，真实环境中收集[t-1,t)到来的请求直接给出
    def get_new_arrive_request_list(self):
        now_new_arrive_request_list = []
        for i in range(self.state_dim):
            now_new_arrive_request_list.append([])
        if t in self.arriveTime_request_dic:
            for request_in_dic in self.arriveTime_request_dic[t]:
                # request_in_dic的形式为[request_id, arrive_time, rtl]
                # request [request_id, arrive_time, rtl, remaining_time]
                # request_in_dic 转为request
                request = list(request_in_dic)
                # 刚加进缓冲时 remaining_time=rtl
                request.append(request_in_dic[RTL_INDEX])
                now_new_arrive_request_list[request[REMAINING_TIME_INDEX] //
                                            TIME_UNIT_IN_ON_SECOND].append(
                    request)
        return now_new_arrive_request_list

    #   初始状态
    def reset(self):
        t_to_zero()
        self.call_get_reward_times = 0
        self.invalid_action_times = 0
        self.success_request_list = []
        self.fail_request_list = []
        self.active_request_group_by_remaining_time_list = self.get_new_arrive_request_list(
        )
        self.active_request_group_by_remaining_time_list_to_state()
        return self.state_record

    def get_active_request_sum(self):
        sum = 0
        for active_request in self.active_request_group_by_remaining_time_list:
            sum += active_request.__len__()
        return sum

    def get_more_provision_rate(self):
        more_provision_request_num = 0
        for success_request in self.success_request_list:
            if success_request[RTL_INDEX] > success_request[WAIT_TIME_INDEX]:
                more_provision_request_num += 1
        return float(more_provision_request_num) / len(self.new_arrive_request_in_dic)

    def get_more_provision_sum(self):
        more_provision_list = []
        for success_request in self.success_request_list:
            more_provision_list.append(
                float(success_request[RTL_INDEX] - success_request[WAIT_TIME_INDEX]) / success_request[RTL_INDEX])
        return np.mean(more_provision_list)

    def get_success_request(self):
        return self.success_request_list, WAIT_TIME_INDEX, RTL_INDEX

    def get_submit_request_num_per_second_variance(self):
        submit_request_num_per_second_list = [0] * t
        for success_request in self.success_request_list:
            submit_request_num_per_second_list[
                success_request[ARRIVE_TIME_INDEX] +
                success_request[WAIT_TIME_INDEX]] += 1
        more_than_threshold_times = 0
        for submit_request_num_per_second in submit_request_num_per_second_list:
            if submit_request_num_per_second > self.threshold:
                more_than_threshold_times += 1
        return np.var(submit_request_num_per_second_list)

    def get_more_than_threshold_rate(self):
        submit_request_num_per_second_list = [0] * t
        for success_request in self.success_request_list:
            submit_request_num_per_second_list[
                success_request[ARRIVE_TIME_INDEX] +
                success_request[WAIT_TIME_INDEX]] += 1
        more_than_threshold_times = 0
        for submit_request_num_per_second in submit_request_num_per_second_list:
            if submit_request_num_per_second > self.threshold:
                more_than_threshold_times += 1
        return float(more_than_threshold_times) / sum(submit_request_num_per_second_list)

    def print_wait_time_avg(self):
        success_request_rtl_dic = {}
        for success_request in self.success_request_list:
            if success_request[RTL_INDEX] in success_request_rtl_dic:
                success_request_rtl_dic[success_request[RTL_INDEX]].append(success_request)
            else:
                success_request_rtl_dic[success_request[RTL_INDEX]] = []
        for rtl in success_request_rtl_dic:
            wait_time_arr = np.array(np.array(success_request_rtl_dic[rtl])[:, WAIT_TIME_INDEX], dtype=int)
            wait_time_avg = np.average(wait_time_arr)
            print('rtl:' + str(rtl) + '等待时间平均值:{:.1f}'.format(wait_time_avg))

    def get_now_state(self):
        state = []
        for active_request_group_by_remaining_time in self.active_request_group_by_remaining_time_list:
            state.append(len(active_request_group_by_remaining_time))
        return state
