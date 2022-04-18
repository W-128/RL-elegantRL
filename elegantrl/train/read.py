import numpy as np
from elegantrl.envs.request_env_no_sim import numpy_a_to_action

threshold = 40
s_a_list = np.load('episode_evaluate\evaluate_episode0.npy', allow_pickle=True).tolist()
edit_s_a_list=[]
for s_a in s_a_list:
    edit_s_a = []
    s = s_a[0] * threshold
    a = numpy_a_to_action(s_a[1])
    edit_s_a.append(s)
    edit_s_a.append(a)
    edit_s_a_list.append(edit_s_a)
print(edit_s_a_list)
