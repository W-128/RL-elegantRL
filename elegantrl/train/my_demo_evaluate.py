import torch
import sys
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

from elegantrl.train.run import *
from elegantrl.agents import *
from elegantrl.train.config import Arguments
from elegantrl.envs.request_env_no_sim import RequestEnvNoSim
from elegantrl.train.evaluator import \
    get_episode_return_and_step_and_metrics
from baseline.agent import EDF


class RequestEnvNoSimWrapper():

    def __init__(self, task_num, more_than_threshold_penalty_scale=-4) -> None:
        self.env = RequestEnvNoSim(task_num)
        self.env_num = 1
        self.env_name = 'RequestEnvNoSim'
        self.max_step = len(self.env.all_request
                            ) + self.env.state_dim  # 每个episode的最大步数（就是从 env.reset() 开始到 env.step()返回 done=True 的步数上限）
        self.state_dim = self.env.state_dim  # feature number of state
        self.action_dim = self.env.action_dim  # feature number of action
        self.target_return = 270
        self.if_discrete = False
        self.env.more_than_threshold_penalty_scale = more_than_threshold_penalty_scale
        self.env.action_optim = True
        self.env.avoid_more_than_threshold = True
        self.threshold = self.env.threshold

    def reset(self):
        reset_state = np.asarray(self.env.reset(), dtype=np.float32) / self.env.threshold
        return reset_state

    def step(self, action: np.ndarray):
        # I suggest to set action space as (-1, +1) when you design your own env.
        state, reward, done, info_dict = self.env.step(action)  # state, reward, done, info_dict
        return np.asarray(state, dtype=np.float32) / self.env.threshold, reward, done, info_dict

    def get_violation_rate(self):
        return self.env.get_violation_rate()

    def get_fail_rate(self):
        return self.env.get_fail_rate()

    def get_more_provision_mean(self):
        return self.env.get_more_provision_mean()

    def get_over_prov_rate(self):
        return self.env.get_over_prov_rate()

    def get_more_than_threshold_rate(self):
        return self.env.get_more_than_threshold_rate()

    def get_submit_request_num_per_second_variance(self):
        return self.env.get_submit_request_num_per_second_variance()

    def print_wait_time_avg(self):
        return self.env.print_wait_time_avg()

    def get_more_provision_rate(self):
        return self.env.get_more_provision_rate()

    def get_success_request(self):
        return self.env.get_success_request()

    def get_success_request_dic_key_is_end_time_and_rtl_list(self):
        return self.env.get_success_request_dic_key_is_end_time_and_rtl_list()


def evaluate_agent():
    # 流程任务数
    task_num = 1
    env = RequestEnvNoSimWrapper(task_num, more_than_threshold_penalty_scale=0)
    agent = AgentPPO
    args = Arguments(agent, env=env)
    act = agent(args.net_dim, env.state_dim, env.action_dim).act
    two_task_actor_path = 'RequestEnvNoSim0.95_PPO_0/actor_04752485_05638.627.pth'
    one_task_actor_path = 'RequestEnvNoSim0.85_PPO_0/actor_00248219_01867.330.pth'
    actor_path =  one_task_actor_path
    # actor_path='actor_00975952_05888.821.pth'
    act.load_state_dict(torch.load(actor_path, map_location=lambda storage, loc: storage))

    eval_times = 1
    metric_ary = [get_episode_return_and_step_and_metrics(env, act) for _ in range(eval_times)]
    metric_ary = np.array(metric_ary, dtype=np.float32)
    s_avg, r_avg, violation_rate_avg, fail_rate_avg, more_provision_mean_avg, over_prov_rate_avg, variance_avg, more_than_threshold_rate_avg = metric_ary.mean(
        axis=0)  # average of episode return and episode step

    print(
        "步数平均值：{:.1f}, 奖励：{:.1f}, sla违约率：{:.1f}%, sla失败率{:.1f}%, 超供均值{:.1f}, 超供面积比例：{:.1f}%, 每秒提交量方差：{:.1f},提交量大于阈值的概率：{:.5f}%"
        .format(s_avg, r_avg, violation_rate_avg, fail_rate_avg, more_provision_mean_avg, over_prov_rate_avg * 100,
                variance_avg, more_than_threshold_rate_avg))

    env.print_wait_time_avg()

    success_request_dic_key_is_end_time, rtl_list = env.get_success_request_dic_key_is_end_time_and_rtl_list()
    sns.set()
    fig = plt.figure()
    plt.xlabel('time(second)')
    x = list(success_request_dic_key_is_end_time.keys())
    rtl_avg_wait_time_dic = {}
    # {rtl1:[],rtl2:[]}
    for rtl in rtl_list:
        rtl_avg_wait_time_dic[rtl] = []
    for end_time in success_request_dic_key_is_end_time.keys():
        rtl_wait_time_dic = {}
        # {rtl1:[],rtl2:[]}
        for rtl in rtl_list:
            rtl_wait_time_dic[rtl] = []
        for request in success_request_dic_key_is_end_time[end_time]:
            rtl_wait_time_dic[request['rtl']].append(request['wait_time'])
        for rtl in rtl_wait_time_dic:
            if rtl_wait_time_dic[rtl] == []:
                rtl_avg_wait_time_dic[rtl].append(np.nan)
            else:
                rtl_avg_wait_time_dic[rtl].append(np.mean(rtl_wait_time_dic[rtl]))

    for rtl in rtl_list:
        mask = np.isfinite(rtl_avg_wait_time_dic[rtl])
        line, = plt.plot(np.array(x)[mask], np.array(rtl_avg_wait_time_dic[rtl])[mask], ls="--", lw=1)
        plt.plot(x, rtl_avg_wait_time_dic[rtl], color=line.get_color(), lw=1.5, label=rtl)
        # 辅助线
        sup_line = [rtl for i in range(len(x))]
        plt.plot(x, sup_line, color='black', linestyle='--', linewidth='1')

    plt.legend()
    plt.savefig("more_provision")
    # plt.show()


if __name__ == "__main__":
    evaluate_agent()
