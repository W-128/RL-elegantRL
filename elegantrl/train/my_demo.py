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
from elegantrl.train.evaluator import get_episode_return_and_step_and_success_rate_and_more_provision
"""custom env"""


class RequestEnvNoSimWrapper():

    def __init__(self) -> None:
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

    def get_more_provision(self):
        return self.env.get_more_provision()


"""demo"""


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
    args.gamma = 0.98
    args.env.target_return = 270  # set target_reward manually for env 'Pendulum-v0'
    args.learner_gpus = gpu_id
    args.random_seed += gpu_id

    if_check = 1
    if if_check:
        train_and_evaluate(args)
    else:
        train_and_evaluate_mp(args)


def evaluate_agent():
    env = RequestEnvNoSimWrapper()
    env.invalid_action_optim = False
    agent = AgentPPO
    args = Arguments(agent, env=env)
    act = agent(args.net_dim, env.state_dim, env.action_dim).act
    actor_path = "./RequestEnvNoSim_PPO_0/actor_15253455_00270.234.pth"
    act.load_state_dict(
        torch.load(actor_path, map_location=lambda storage, loc: storage))

    eval_times = 4
    r_s_success_rate_more_provision_ary = [
        get_episode_return_and_step_and_success_rate_and_more_provision(
            env, act) for _ in range(eval_times)
    ]
    r_s_success_rate_more_provision_ary = np.array(
        r_s_success_rate_more_provision_ary, dtype=np.float32)
    r_avg, s_avg, success_rate_avg, more_provision_avg = r_s_success_rate_more_provision_ary.mean(
        axis=0)  # average of episode return and episode step

    print("奖励平均值：{:.1f}, 步数平均值：{:.1f}, 成功率平均值：{:.1f}%, 超供量平均值：{:.1f}".format(
        r_avg, s_avg, success_rate_avg, more_provision_avg))


if __name__ == "__main__":
    demo_continuous_action_on_policy()
    # evaluate_agent()