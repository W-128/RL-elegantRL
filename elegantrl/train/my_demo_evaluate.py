import torch
import sys
import os
import numpy as np

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])

from elegantrl.train.run import *
from elegantrl.agents import *
from elegantrl.train.config import Arguments
from elegantrl.envs.request_env_no_sim import RequestEnvNoSim
from elegantrl.train.evaluator import \
    get_episode_return_and_step_and_success_rate_and_more_provision_and_variance_and_more_than_threshold_rate
"""custom env"""


class RequestEnvNoSimWrapper():

    def __init__(self, more_than_threshold_penalty_scale=-4) -> None:
        self.env = RequestEnvNoSim()
        self.env_num = 1
        self.env_name = 'RequestEnvNoSim'
        self.max_step = len(
            self.env.new_arrive_request_in_dic
        ) + self.env.state_dim  # 每个episode的最大步数（就是从 env.reset() 开始到 env.step()返回 done=True 的步数上限）
        self.state_dim = self.env.state_dim  # feature number of state
        self.action_dim = self.env.action_dim  # feature number of action
        self.target_return = 270
        self.if_discrete = False
        self.env.more_than_threshold_penalty_scale = more_than_threshold_penalty_scale

    def reset(self):
        reset_state = np.asarray(self.env.reset(),
                                 dtype=np.float32) / self.env.threshold
        return reset_state

    def step(self, action: np.ndarray):
        # I suggest to set action space as (-1, +1) when you design your own env.
        state, reward, done, info_dict = self.env.step(
            action)  # state, reward, done, info_dict
        return np.asarray(
            state,
            dtype=np.float32) / self.env.threshold, reward, done, info_dict

    def get_success_rate(self):
        return self.env.get_success_rate()

    def get_more_provision_sum(self):
        return self.env.get_more_provision_sum()

    def get_submit_request_num_per_second_variance_and_more_than_threshold_rate(
            self):
        return self.env.get_submit_request_num_per_second_variance_and_more_than_threshold_rate(
        )


def evaluate_agent():
    env = RequestEnvNoSimWrapper(more_than_threshold_penalty_scale=0)
    agent = AgentPPO
    args = Arguments(agent, env=env)
    act = agent(args.net_dim, env.state_dim, env.action_dim).act
    actor_path = 'RequestEnvNoSim_PPO_0/actor_00974997_00185.450.pth'
    act.load_state_dict(
        torch.load(actor_path, map_location=lambda storage, loc: storage))

    eval_times = 4
    r_s_success_rate_more_provision_variance_more_than_threshold_rate_ary = [
        get_episode_return_and_step_and_success_rate_and_more_provision_and_variance_and_more_than_threshold_rate(
            env, act) for _ in range(eval_times)
    ]
    r_s_success_rate_more_provision_variance_more_than_threshold_rate_ary = np.array(
        r_s_success_rate_more_provision_variance_more_than_threshold_rate_ary,
        dtype=np.float32)
    r_avg, s_avg, success_rate_avg, more_provision_avg, variance_avg, more_than_threshold_rate_avg = r_s_success_rate_more_provision_variance_more_than_threshold_rate_ary.mean(
        axis=0)  # average of episode return and episode step

    print(
        "奖励平均值：{:.1f}, 步数平均值：{:.1f}, 成功率平均值：{:.1f}%, 超供量平均值：{:.1f}, 方差平均值：{:.1f}, 提交量大于阈值的概率：{:.1f}%"
        .format(r_avg, s_avg, success_rate_avg, more_provision_avg,
                variance_avg, more_than_threshold_rate_avg))


if __name__ == "__main__":
    evaluate_agent()
