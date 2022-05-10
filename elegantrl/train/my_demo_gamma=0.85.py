import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])
from elegantrl.train.continuous_action_on_policy import continuous_action_on_policy

continuous_action_on_policy = continuous_action_on_policy(0.85)
