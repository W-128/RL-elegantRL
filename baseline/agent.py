import numpy as np


class RandomChoose:

    def __init__(self, action_dim, N):
        self.action_dim = action_dim  # 总的动作个数
        self.N = N

    def predict(self, observation, threshold):
        action = [0] * self.action_dim
        remaining_num = threshold
        while remaining_num != 0 and np.sum(observation) != 0:
            choose_list = []
            for index in range(0, len(observation)):
                if observation[index] != 0:
                    choose_list.append(index)
            submit_index = np.random.choice(choose_list)
            observation[submit_index] -= 1
            action[submit_index] += 1
            remaining_num -= 1
        return action


class EDF:

    def __init__(self, action_dim, N):
        self.action_dim = action_dim  # 总的动作个数
        self.N = N

    def predict(self, observation, threshold):
        action = [0] * self.action_dim
        action[self.N] = min(threshold, observation[self.N])
        return action


class EDFSubmitThreshold:

    def __init__(self, action_dim, N):
        self.action_dim = action_dim  # 总的动作个数
        self.N = N

    def predict(self, observation, threshold):
        observation_temp = list(observation)
        action = [0] * self.action_dim
        remaining_num = threshold
        for index in range(self.N, len(observation_temp)):
            if remaining_num == 0:
                break
            if observation_temp[index] != 0:
                if remaining_num > observation_temp[index]:
                    action[index] = observation_temp[index]
                    remaining_num = remaining_num - observation_temp[index]
                    observation_temp[index] = 0
                else:
                    action[index] = remaining_num
                    observation_temp[
                        index] = observation_temp[index] - remaining_num
                    remaining_num = 0
        if remaining_num != 0:
            for index in range(0, self.N):
                if remaining_num == 0:
                    break
                if observation_temp[index] != 0:
                    if remaining_num > observation_temp[index]:
                        action[index] = observation_temp[index]
                        remaining_num = remaining_num - observation_temp[index]
                        observation_temp[index] = 0
                    else:
                        action[index] = remaining_num
                        observation_temp[
                            index] = observation_temp[index] - remaining_num
                        remaining_num = 0
        return action
