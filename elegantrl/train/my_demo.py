import sys
import gym
from elegantrl.train.run import *
from elegantrl.agents import *
from elegantrl.train.config import Arguments
from elegantrl.envs.request_env_no_sim import RequestEnvNoSim

"""custom env"""


class PendulumEnv(gym.Wrapper):  # [ElegantRL.2021.11.11]
    def __init__(self, gym_env_id="Pendulum-v1", target_return=-200):
        # Pendulum-v0 gym.__version__ == 0.17.0
        # Pendulum-v1 gym.__version__ == 0.21.0
        gym.logger.set_level(40)  # Block warning
        super(PendulumEnv, self).__init__(env=gym.make(gym_env_id))

        # from elegantrl.envs.Gym import get_gym_env_info
        # get_gym_env_info(env, if_print=True)  # use this function to print the env information
        self.env_num = 1  # the env number of VectorEnv is greater than 1
        self.env_name = gym_env_id  # the name of this env.
        self.max_step = 200  # the max step of each episode
        self.state_dim = 3  # feature number of state
        self.action_dim = 1  # feature number of action
        self.if_discrete = False  # discrete action or continuous action
        self.target_return = target_return  # episode return is between (-1600, 0)

    def reset(self):
        return self.env.reset().astype(np.float32)

    def step(self, action: np.ndarray):
        # PendulumEnv set its action space as (-2, +2). It is bad.  # https://github.com/openai/gym/wiki/Pendulum-v0
        # I suggest to set action space as (-1, +1) when you design your own env.
        state, reward, done, info_dict = self.env.step(
            action * 2
        )  # state, reward, done, info_dict
        return state.astype(np.float32), reward, done, info_dict


class HumanoidEnv(gym.Wrapper):  # [ElegantRL.2021.11.11]
    def __init__(self, gym_env_id="Humanoid-v3", target_return=3000):
        gym.logger.set_level(40)  # Block warning
        super(HumanoidEnv, self).__init__(env=gym.make(gym_env_id))

        # from elegantrl.envs.Gym import get_gym_env_info
        # get_gym_env_info(env, if_print=True)  # use this function to print the env information
        self.env_num = 1  # the env number of VectorEnv is greater than 1
        self.env_name = gym_env_id  # the name of this env.
        self.max_step = 1000  # the max step of each episode
        self.state_dim = 376  # feature number of state
        self.action_dim = 17  # feature number of action
        self.if_discrete = False  # discrete action or continuous action
        self.target_return = target_return  # episode return is between (-1600, 0)

    def reset(self):
        return self.env.reset()

    def step(self, action: np.ndarray):
        # PendulumEnv set its action space as (-2, +2). It is bad.  # https://github.com/openai/gym/wiki/Pendulum-v0
        # I suggest to set action space as (-1, +1) when you design your own env.
        # action_space.high = 0.4
        # action_space.low = -0.4
        state, reward, done, info_dict = self.env.step(
            action * 2.5
        )  # state, reward, done, info_dict
        return state.astype(np.float32), reward, done, info_dict



"""demo"""


def demo_continuous_action_on_policy():
    gpu_id = 0  # >=0 means GPU ID, -1 means CPU
    drl_id = 0  # int(sys.argv[2])


    env = RequestEnvNoSim()
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


if __name__ == "__main__":
    demo_continuous_action_on_policy()
