import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from elegantrl.envs.request_env_no_sim import RequestEnvNoSim
from agent import RandomChoose, EDF, EDFSubmitThreshold, fifo
from train_test import test, test_fifo
import datetime
import torch
from my_common.utils import make_dir
import numpy as np
from my_common.get_data import get_arrive_time_request_dic

curr_path = os.path.dirname(os.path.abspath(__file__))  # 当前文件所在绝对路径
curr_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")  # 获取当前时间
env_name = 'request_env_no_sim'  # 环境名称
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 检测GPU

# request=[request_id, arrive_time, rtl, task_id, remaining_time]
# success_request_list[request_id, arrive_time, rtl, task_id, wait_time]
REQUEST_ID_INDEX = 0
ARRIVE_TIME_INDEX = 1
RTL_INDEX = 2
TASK_ID_INDEX = 3
REMAINING_TIME_INDEX = 4
WAIT_TIME_INDEX = 4
# t=1000ms
TIME_UNIT = 1
TIME_UNIT_IN_ON_SECOND = int(1 / TIME_UNIT)


class RandomChooseConfig:
    '''训练相关参数'''

    def __init__(self):
        self.algo_name = 'random_choose'  # 算法名称
        self.env_name = env_name  # 环境名称
        self.result_path = curr_path + "/outputs/" + self.env_name + \
                           '/' + self.algo_name + '/results/'  # 保存结果的路径
        self.save = True  # 是否保存图片


class EDFSubmitThresholdConfig:
    '''训练相关参数'''

    def __init__(self):
        self.algo_name = 'edf_submit_threshold'  # 算法名称
        self.env_name = env_name  # 环境名称
        self.result_path = curr_path + "/outputs/" + self.env_name + \
                           '/' + self.algo_name + '/results/'  # 保存结果的路径
        self.save = True  # 是否保存图片


class EDFConfig:
    '''训练相关参数'''

    def __init__(self):
        self.algo_name = 'edf'  # 算法名称
        self.env_name = env_name  # 环境名称
        self.result_path = curr_path + "/outputs/" + self.env_name + \
                           '/' + self.algo_name + '/results/'  # 保存结果的路径
        self.save = True  # 是否保存图片


class FIFOConfig:
    '''训练相关参数'''

    def __init__(self):
        self.algo_name = 'fifo'  # 算法名称
        self.env_name = env_name  # 环境名称
        self.result_path = curr_path + "/outputs/" + self.env_name + \
                           '/' + self.algo_name + '/results/'  # 保存结果的路径
        self.save = True  # 是否保存图片


env = RequestEnvNoSim()

THRESHOLD = env.threshold

env.action_is_probability = False

# random_choose_cfg = RandomChooseConfig()
# make_dir(random_choose_cfg.result_path)  # 创建模型路径的文件夹
# agent = RandomChoose(env.action_dim)
# success_request, waiting_time_index, rtl_index = test(random_choose_cfg, env,agent)
# # plot_waiting_time_and_require_time(success_request, waiting_time_index,
# #                                    rtl_index, random_choose_cfg)

print("==========================================================")
edf_config = EDFConfig()
make_dir(edf_config.result_path)  # 创建模型路径的文件夹
agent = EDF(env.action_dim)
success_request, waiting_time_index, rtl_index = test(edf_config, env, agent)
# plot_waiting_time_and_require_time(success_request, waiting_time_index,
#                                    rtl_index, edf_config)

print("==========================================================")
edf_submit_threshold_config = EDFSubmitThresholdConfig()
make_dir(edf_submit_threshold_config.result_path)  # 创建模型路径的文件夹
agent = EDFSubmitThreshold(env.action_dim)
success_request, waiting_time_index, rtl_index = test(edf_submit_threshold_config, env, agent)
# plot_waiting_time_and_require_time(success_request, waiting_time_index,
#                                    rtl_index, edf_submit_threshold_config)

print("==========================================================")
fifo_config = FIFOConfig()
make_dir(fifo_config.result_path)  # 创建模型路径的文件夹
agent = fifo(env.action_dim)
success_request, waiting_time_index, rtl_index = test_fifo(fifo_config, env, agent)


# FIFO
class FIFO:

    def __init__(self):
        self.new_arrive_request_in_dic, self.arriveTime_request_dic = get_arrive_time_request_dic(
            ARRIVE_TIME_INDEX)
        self.t = 0
        self.threshold = THRESHOLD
        self.active_request_list = []
        self.get_new_arrive_request()
        self.success_request_list = []
        self.fail_request_list = []

    def get_new_arrive_request(self):
        if self.t in self.arriveTime_request_dic:
            for request_in_dic in self.arriveTime_request_dic[self.t]:
                # request_in_dic的形式为[request_id, arrive_time, rtl]
                # request [request_id, arrive_time, rtl, remaining_time]
                # request_in_dic 转为request
                # 刚加进缓冲时 remaining_time=rtl
                request = list(request_in_dic)
                request.append(request_in_dic[RTL_INDEX])
                self.active_request_list.append(request)

    def submit_request(self):
        remaining_num = THRESHOLD
        self.active_request_list = sorted(self.active_request_list, key=lambda i: i[ARRIVE_TIME_INDEX])
        while remaining_num != 0 and len(self.active_request_list) != 0:
            success_request = list(self.active_request_list[0])
            del self.active_request_list[0]
            success_request[WAIT_TIME_INDEX] = self.t - success_request[ARRIVE_TIME_INDEX]
            self.success_request_list.append(success_request)
            remaining_num = remaining_num - 1

    def step(self):
        self.submit_request()
        self.t = self.t + 1
        for request in self.active_request_list:
            request[REMAINING_TIME_INDEX] = request[REMAINING_TIME_INDEX] - 1
        for request in self.active_request_list[:]:
            if request[REMAINING_TIME_INDEX] < 0:
                self.fail_request_list.append(list(request))
                self.active_request_list.remove(request)

        # time.sleep(FRESH_TIME)
        self.get_new_arrive_request()
        episode_done = False
        if self.t > np.max(list(self.arriveTime_request_dic.keys())
                           ) and self.active_request_list.__len__() == 0:
            episode_done = True
        if episode_done:
            print('环境正确性：' + str(self.is_correct()))
            print('成功率：{:.1f}%'.format(self.get_success_rate() * 100))
            print('超供率：{:.1f}%'.format(self.get_more_provision_rate() * 100))
            print('超供程度：{:.1f}%'.format(self.get_more_provision_sum() * 100))
            print('每秒提交量方差：{:.1f}'.format(self.get_submit_request_num_per_second_variance()))

        return episode_done

    def get_success_rate(self):
        all_request_num = len(self.new_arrive_request_in_dic)
        return len(self.success_request_list) / float(all_request_num)

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

    def get_more_provision(self):
        more_provision_list = []
        for success_request in self.success_request_list:
            more_provision_list.append(
                (success_request[RTL_INDEX] - success_request[WAIT_TIME_INDEX])
                / success_request[RTL_INDEX])
        return np.sum(more_provision_list)

    def get_more_provision_rate(self):
        more_provision_request_num = 0
        for success_request in self.success_request_list:
            if success_request[RTL_INDEX] > success_request[WAIT_TIME_INDEX]:
                more_provision_request_num += 1
        return float(more_provision_request_num) / len(self.new_arrive_request_in_dic)

    def get_more_provision_sum(self):
        more_provision_list = []
        for success_request in self.success_request_list:
            more_provision_list.append(float(success_request[RTL_INDEX] -
                                             success_request[WAIT_TIME_INDEX]) / success_request[RTL_INDEX])
        return np.mean(more_provision_list)

    def get_submit_request_num_per_second_variance(self):
        submit_request_num_per_second_list = [0] * self.t
        for success_request in self.success_request_list:
            submit_request_num_per_second_list[
                success_request[ARRIVE_TIME_INDEX] +
                success_request[WAIT_TIME_INDEX]] += 1
        more_than_threshold_times = 0
        for submit_request_num_per_second in submit_request_num_per_second_list:
            if submit_request_num_per_second > THRESHOLD:
                more_than_threshold_times += 1
        return np.var(submit_request_num_per_second_list)

# print("====================================================")
# fifo = FIFO()
# done = False
# while done != True:
#     done = fifo.step()
