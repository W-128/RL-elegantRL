import sys
import os
import datetime
import numpy as np
import math

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath + '/my_common')

from my_common.get_data import get_arrive_time_request_dic
from my_common.utils import generate_next_request

# t=1000ms
TIME_UNIT = 1
TIME_UNIT_IN_ON_SECOND = int(1 / TIME_UNIT)
THRESHOLD = int(90 / TIME_UNIT_IN_ON_SECOND)

# 处理中
# request={'request_id', 'arrive_time', 'rtl', 'task_id', 'remaining_time'}
# 处理完
# success/violate_request{'request_id', 'arrive_time', 'rtl', 'task_id', 'wait_time'}

FRESH_TIME = 1

curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  # 获取当前时间


class RequestEnvNoSim:

    def __init__(self, task_num):
        if task_num == 2:
            self.task_num = 2
            # 引擎能承受的单位时间最大并发量
            self.threshold = 90
        if task_num == 1:
            self.task_num = 1
            # 引擎能承受的单位时间最大并发量
            self.threshold = 45
            self.beta = 0.04
        # 奖励参数设置
        self.A = 1
        # self.more_than_threshold_penalty_scale = -9
        self.C = -1/float(self.threshold)
        # action需要从概率到数量
        self.action_is_probability = True
        # 状态向量的维数=rtl的级别个数
        self.N = 10
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
        # 超过unserved_time_up_bound 请求视作失败
        self.unserved_time_up_bound = 20
        # 存放已过期请求尚未执行的请求
        self.violate_request_unsubmit = []
        # 存放未违约请求
        self.success_request_list = []
        # 存放sla失败请求
        self.fail_request_list = []
        # 存放sla违约但未失败且已经执行的请求
        self.violate_request_list = []
        self.episode = 0
        self.call_get_reward_times = 0
        self.invalid_action_times = 0
        self.need_evaluate_env_correct = False
        # 测试阶段将该值置为true 将Qt全执行
        self.action_optim = False
        self.avoid_more_than_threshold = False
        self.t = 0
        self.next_request_num = 0
        self.success_request_dic_key_is_end_time = {}
        '''
        arriveTime_request_dic:
        key=arriveTime
        value=arriveTime为key的request_in_dic列表
        request_in_dic的形式为{'request_id', 'arrive_time', 'rtl', 'task_id'}
        '''
        # self.all_request
        self.all_request, self.arriveTime_request_dic = get_arrive_time_request_dic()
        self.all_request_num = len(self.all_request) * self.task_num
        # self.end_request_result_path = curr_path + '/success_request_list/' + curr_time + '/'
        # make_dir(self.end_request_result_path)

    # 概率->number_action
    def action_to_number_action(self, action):
        # number_action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        number_action = [0] * len(action)
        for index in range(len(action)):
            number_action[index] = min(math.ceil(action[index] * self.threshold),
                                       len(self.active_request_group_by_remaining_time_list[index]))

        if self.action_optim:
            if number_action[0] < len(self.active_request_group_by_remaining_time_list[0]):
                number_action[0] = min(self.threshold, len(self.active_request_group_by_remaining_time_list[0]))

        # 拒绝超供
        if np.sum(number_action) > self.threshold:
            need_reduce_number = np.sum(number_action) - self.threshold
            while need_reduce_number > 0:
                for index in range(len(number_action) - 1, -1, -1):
                    if number_action[index] > 0:
                        if number_action[index] > need_reduce_number:
                            number_action[index] = number_action[index] - need_reduce_number
                            need_reduce_number = 0
                            break
                        if number_action[index] < need_reduce_number:
                            need_reduce_number -= number_action[index]
                            number_action[index] = 0

        return number_action

    # 返回奖励值和下一个状态
    def step(self, action):
        if self.action_is_probability:
            num_action = self.action_to_number_action(action)
        else:
            num_action = action
        # 环境更新
        reward, done = self.update_env(num_action)

        # 验证环境正确性
        if done and self.need_evaluate_env_correct:
            print('环境正确性:' + str(self.is_correct()))

        # debug
        # print('active_request_list:' + str(self.active_request_group_by_remaining_time_list))

        return self.state_record, reward, done, {}

    def step_fifo(self, submit_request_id_list):
        # submit_request_id_list to action
        action = [0] * self.action_dim
        for index in range(len(self.active_request_group_by_remaining_time_list)):
            for active_request in self.active_request_group_by_remaining_time_list[index]:
                if active_request['request_id'] in submit_request_id_list:
                    action[index] += 1

        # 环境更新
        reward, done = self.update_env(action)

        # 验证环境正确性
        if done and self.need_evaluate_env_correct:
            print('环境正确性:' + str(self.is_correct()))

        # debug
        # print('active_request_list:' + str(self.active_request_group_by_remaining_time_list))

        return self.active_request_group_by_remaining_time_list, reward, done, {}

    # 确保action合法
    def update_env(self, num_action):
        # submit request
        # num_action=(从剩余时间为0的请求中提交的请求个数, 从剩余时间为1的请求中提交的请求个数,...,从剩余时间为5的请求中提交的请求个数)
        for remaining_time in range(self.action_dim):
            for j in range(int(num_action[remaining_time])):
                # time_stamp = time.time()
                success_request = self.active_request_group_by_remaining_time_list[remaining_time][0].copy()
                # 把提交的任务从active_request_list中删除
                del self.active_request_group_by_remaining_time_list[remaining_time][0]
                success_request['wait_time'] = self.t - success_request['arrive_time']
                self.success_request_list.append(success_request)
                if self.t in self.success_request_dic_key_is_end_time:
                    self.success_request_dic_key_is_end_time[self.t].append(success_request)
                else:
                    self.success_request_dic_key_is_end_time[self.t] = [success_request]
                # 下一个任务加入
                if self.task_num != 1:
                    next_request = generate_next_request(success_request, self.task_num)
                    if next_request != {}:
                        self.next_request_num += 1
                        if next_request['arrive_time'] not in self.arriveTime_request_dic:
                            self.arriveTime_request_dic[next_request['arrive_time']] = [next_request]
                        else:
                            self.arriveTime_request_dic[next_request['arrive_time']].append(next_request)
                        self.all_request.append(next_request)

        # 提交量不足阈值时提交已经违约的
        if np.sum(num_action) < self.threshold:
            remain_submit_times = self.threshold - np.sum(num_action)
            while (remain_submit_times != 0):
                if len(self.violate_request_unsubmit) == 0:
                    break
                else:
                    req = self.violate_request_unsubmit.pop(0)
                    if self.t - int(req['arrive_time']) <= self.unserved_time_up_bound:
                        req['wait_time'] = self.t - req['arrive_time']
                        # 加入sla违约请求列表
                        self.violate_request_list.append(req)
                        remain_submit_times -= 1
                    else:
                        self.fail_request_list.append(req)

        # 时间推移
        self.t += 1

        fail_penalty = 0
        if self.task_num == 1:
            fail_num = len(self.active_request_group_by_remaining_time_list[0])
            for active_request in self.active_request_group_by_remaining_time_list[0]:
                self.violate_request_unsubmit.append(active_request)
            fail_penalty = self.C * fail_num

        if self.task_num == 2:
            # 失败数量
            fail_task1_num = 0
            fail_task2_num = 0
            for active_request in self.active_request_group_by_remaining_time_list[0]:
                self.violate_request_unsubmit.append(active_request)
                if active_request['task_id'] == 'task1':
                    fail_task1_num += 1
                if active_request['task_id'] == 'task2':
                    fail_task2_num += 1
            fail_penalty = (fail_task1_num * self.C * 2 +
                            fail_task2_num * self.C)

        # remaining_time==0且还留在active_request_group_by_remaining_time_list中的请求此时失败
        self.active_request_group_by_remaining_time_list[0] = []

        # 超阈值惩罚
        # more_than_threshold_penalty = 0
        # if sum(num_action) > self.threshold:
        #     more_than_threshold_penalty = (sum(num_action) - self.threshold) / float(self.threshold)

        # 成功奖励
        success_reward = 0
        for index in range(len(num_action)):
            success_reward += (self.A - index * self.beta) * num_action[index]
        success_reward = success_reward / float(self.threshold)

        reward = success_reward + fail_penalty

        # active_request_group_by_remaining_time_list 剩余时间要推移
        for i in range(1, len(self.active_request_group_by_remaining_time_list)):
            for active_request in self.active_request_group_by_remaining_time_list[i]:
                active_request['remaining_time'] = active_request['remaining_time'] - 1
                self.active_request_group_by_remaining_time_list[i - 1].append(active_request.copy())
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
        if self.t > np.max(list(self.arriveTime_request_dic.keys())) and remaining_request_is_done:
            episode_done = True
        # time.sleep(FRESH_TIME)
        return reward, episode_done

    # request_list -> state
    def active_request_group_by_remaining_time_list_to_state(self):
        state = []
        for active_request_group_by_remaining_time in self.active_request_group_by_remaining_time_list:
            state.append(len(active_request_group_by_remaining_time))
        self.state_record = state

    def is_correct(self):
        all_request_id_list = []
        for request_in_dic in self.all_request:
            all_request_id_list.append(request_in_dic['request_id'])
        all_request_after_episode_list = []
        all_request_id_after_episode_list = []
        for request in self.fail_request_list:
            all_request_after_episode_list.append(request)
            all_request_id_after_episode_list.append(request['request_id'])
        for request in self.success_request_list:
            all_request_after_episode_list.append(request)
            all_request_id_after_episode_list.append(request['request_id'])
        for request in self.violate_request_list:
            all_request_after_episode_list.append(request)
            all_request_id_after_episode_list.append(request['request_id'])
        all_request_id_list.sort()
        all_request_id_after_episode_list.sort()
        return all_request_id_after_episode_list == all_request_id_list

    def get_success_rate(self):
        success_request_task_id_dic = {}
        for success_request_task in self.success_request_list:
            if success_request_task['task_id'] in success_request_task_id_dic:
                success_request_task_id_dic[success_request_task['task_id']].append(success_request_task)
            else:
                success_request_task_id_dic[success_request_task['task_id']] = [success_request_task]
        # for task_id in success_request_task_id_dic:
        #     print('task_id:' + task_id + '应有数量:' + str(self.all_request_num / 2))
        #     print('task_id:' + task_id + '成功数量：' + str(len(success_request_task_id_dic[task_id])))
        # print("self.next_request_num" + str(self.next_request_num))
        return self.success_request_list.__len__() / self.all_request_num

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
        if self.t in self.arriveTime_request_dic:
            for request_in_dic in self.arriveTime_request_dic[self.t]:
                # request_in_dic的形式为{'request_id', 'arrive_time', 'rtl', 'task_id'}
                # request=              {'request_id', 'arrive_time', 'rtl', 'task_id', 'remaining_time'}
                # request_in_dic 转为request
                request = request_in_dic.copy()
                # 刚加进缓冲时 remaining_time=rtl
                request['remaining_time'] = request_in_dic['rtl']
                now_new_arrive_request_list[request['remaining_time'] // TIME_UNIT_IN_ON_SECOND].append(request)
        return now_new_arrive_request_list

    #   初始状态
    def reset(self):
        self.t = 0
        self.call_get_reward_times = 0
        self.invalid_action_times = 0
        # 存放已过期请求
        self.violate_request_unsubmit = []
        # 存放未违约请求
        self.success_request_list = []
        # 存放sla失败请求
        self.fail_request_list = []
        # 存放sla违约但未失败请求
        self.violate_request_list = []
        self.all_request, self.arriveTime_request_dic = get_arrive_time_request_dic()
        self.active_request_group_by_remaining_time_list = self.get_new_arrive_request_list()
        self.active_request_group_by_remaining_time_list_to_state()
        self.next_request_num = 0
        self.success_request_dic_key_is_end_time = {}
        return self.state_record

    #   初始状态
    def reset_fifo(self):
        self.t = 0
        self.call_get_reward_times = 0
        self.invalid_action_times = 0
        # 存放已过期请求
        self.violate_request_unsubmit = []
        # 存放未违约请求
        self.success_request_list = []
        # 存放sla失败请求
        self.fail_request_list = []
        # 存放sla违约但未失败请求
        self.violate_request_list = []
        self.all_request, self.arriveTime_request_dic = get_arrive_time_request_dic()
        self.active_request_group_by_remaining_time_list = self.get_new_arrive_request_list()
        self.active_request_group_by_remaining_time_list_to_state()
        self.next_request_num = 0
        self.success_request_dic_key_is_end_time = {}
        return self.active_request_group_by_remaining_time_list

    def get_active_request_sum(self):
        sum = 0
        for active_request in self.active_request_group_by_remaining_time_list:
            sum += active_request.__len__()
        return sum

    def get_more_provision_rate(self):
        more_provision_request_num = 0
        for success_request in self.success_request_list:
            if success_request['rtl'] > success_request['wait_time']:
                more_provision_request_num += 1
        return float(more_provision_request_num) / self.all_request_num

    def get_more_provision_degree(self):
        more_provision_list = []
        for success_request in self.success_request_list:
            more_provision_list.append(
                float(success_request['rtl'] - success_request['wait_time']) / success_request['rtl'])
        # more_provision_list = more_provision_list + [0] * len(self.fail_request_list)
        return np.mean(more_provision_list)

    # 超供平均值
    def get_more_provision_mean(self):
        more_provision_list = []
        for success_request in self.success_request_list:
            more_provision_list.append(success_request['rtl'] - success_request['wait_time'])
        return np.mean(more_provision_list)

    def get_more_provision_sum(self):
        more_provision_list = []
        for success_request in self.success_request_list:
            more_provision_list.append(success_request['rtl'] - success_request['wait_time'])
        return float(np.sum(more_provision_list))

    def get_success_request(self):
        return self.success_request_list

    def get_success_request_dic_key_is_end_time_and_rtl_list(self):
        rtl_list = []
        for success_request in self.success_request_list:
            if success_request['rtl'] not in rtl_list:
                rtl_list.append(success_request['rtl'])
        return self.success_request_dic_key_is_end_time, rtl_list

    def get_submit_request_num_per_second_variance(self):
        submit_request_num_per_second_list = [0] * self.t
        for success_request in self.success_request_list:
            submit_request_num_per_second_list[success_request['arrive_time'] + success_request['wait_time']] += 1
        more_than_threshold_times = 0
        for submit_request_num_per_second in submit_request_num_per_second_list:
            if submit_request_num_per_second > self.threshold:
                more_than_threshold_times += 1
        return np.var(submit_request_num_per_second_list)

    def get_more_than_threshold_rate(self):
        submit_request_num_per_second_list = [0] * self.t
        for success_request in self.success_request_list:
            submit_request_num_per_second_list[success_request['arrive_time'] + success_request['wait_time']] += 1
        more_than_threshold_times = 0
        for submit_request_num_per_second in submit_request_num_per_second_list:
            if submit_request_num_per_second > self.threshold:
                more_than_threshold_times += 1
        return float(more_than_threshold_times) / sum(submit_request_num_per_second_list)

    def print_wait_time_avg(self):
        success_request_rtl_dic = {}
        for success_request in self.success_request_list:
            if success_request['rtl'] in success_request_rtl_dic:
                success_request_rtl_dic[success_request['rtl']].append(success_request)
            else:
                success_request_rtl_dic[success_request['rtl']] = []
                success_request_rtl_dic[success_request['rtl']].append(success_request)
        for rtl in success_request_rtl_dic:
            wait_time_list = []
            for success_request in success_request_rtl_dic[rtl]:
                wait_time_list.append(success_request['wait_time'])
            wait_time_arr = np.array(wait_time_list, dtype=int)
            wait_time_avg = np.average(wait_time_arr)
            print('rtl:' + str(rtl) + '等待时间平均值:{:.1f}'.format(wait_time_avg))

    def get_now_state(self):
        state = []
        for active_request_group_by_remaining_time in self.active_request_group_by_remaining_time_list:
            state.append(len(active_request_group_by_remaining_time))
        return state

    # def get_more_provision_area(self):

    def get_violation_rate(self):
        return len(self.violate_request_list) / self.all_request_num

    def get_fail_rate(self):
        return len(self.fail_request_list) / self.all_request_num

    def get_over_prov_rate(self):
        rt_area = 0
        for req in self.all_request:
            rt_area += req['rtl']
        return self.get_more_provision_sum() / rt_area
