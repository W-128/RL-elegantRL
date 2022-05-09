import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from elegantrl.envs.request_env_no_sim_get_data_from_request_record import RequestEnvNoSim
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

# request=[request_id, arrive_time, rtl, remaining_time]
# success_request_list[request_id, arrive_time, rtl, wait_time]
REQUEST_ID_INDEX = 0
ARRIVE_TIME_INDEX = 1
RTL_INDEX = 2
REMAINING_TIME_INDEX = 3
WAIT_TIME_INDEX = 3
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
