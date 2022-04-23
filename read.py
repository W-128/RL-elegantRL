import numpy as np

s_a_list = np.load('./episode_evaluate/evaluate_baseline.npy',
                   allow_pickle=True).tolist()
states = s_a_list[0]
actions = s_a_list[1]
for index in range(len(states)):
    print('state :' + str(states[index]))
    print('action:' + str(actions[index]))
    print("===========================================")
