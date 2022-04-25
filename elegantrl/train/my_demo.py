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

    def __init__(self, more_than_threshold_penalty_scale=-3) -> None:
        self.env = RequestEnvNoSim()
        self.env_num = 1
        self.env_name = 'RequestEnvNoSim'
        self.max_step = len(
            self.env.new_arrive_request_in_dic
        ) + self.env.state_dim  # 每个episode的最大步数（就是从 env.reset() 开始到 env.step()返回 done=True 的步数上限）
        self.state_dim = self.env.state_dim  # feature number of state
        self.action_dim = self.env.action_dim  # feature number of action
        self.target_return = 243
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

    def get_more_than_threshold_rate(self):
        return self.env.get_more_than_threshold_rate()

    def get_submit_request_num_per_second_variance(self):
        return self.env.get_submit_request_num_per_second_variance()

    def print_wait_time_avg(self):
        return self.env.print_wait_time_avg()

    def get_more_provision_rate(self):
        return self.env.get_more_provision_rate()


def demo_continuous_action_on_policy():
    gpu_id = 0  # >=0 means GPU ID, -1 means CPU
    drl_id = 0  # int(sys.argv[2])

    env = RequestEnvNoSimWrapper()
    env.invalid_action_optim = False
    agent = [AgentPPO, AgentPPO_H][drl_id]

    print("agent", agent.__name__)
    print("gpu_id", gpu_id)
    print("env_name", env.env_name)
    args = Arguments(agent, env=env)
    args.gamma = 0.8
    args.env.target_return = 243  # set target_reward manually for env 'Pendulum-v0'
    args.learner_gpus = gpu_id
    args.random_seed += gpu_id

    if_check = 1
    if if_check:
        train_and_evaluate(args)
    else:
        train_and_evaluate_mp(args)


if __name__ == "__main__":
    demo_continuous_action_on_policy()
