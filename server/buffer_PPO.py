import sys
import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
import torch
import numpy as np

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSimForServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from elegantrl.agents.AgentPPO import AgentPPO
from my_common.utils import get_logger


class BufferPPO:
    # 流程的任务数
    task_num = 1
    BUFFER_INSTANCE = None
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)
    logger = get_logger('buffer_ppo', logging.INFO)
    two_task_actor_path = 'RequestEnvNoSim0.95_PPO_0/actor_04752485_05638.627.pth'
    one_task_actor_path = 'RequestEnvNoSim0.8_PPO_0/actor_00975952_05888.821.pth'
    actor_path = rootPath + '/elegantrl/train/' + str(task_num) + '-task-end_reward=1/' + one_task_actor_path

    def __init__(self) -> None:
        self.env = RequestEnvNoSimForServer(BufferPPO.task_num, action_is_probability=True)
        self.agent = AgentPPO
        self.act = self.agent(net_dim=2**7, state_dim=self.env.state_dim, action_dim=self.env.action_dim).act
        self.act.load_state_dict(torch.load(BufferPPO.actor_path, map_location=lambda storage, loc: storage))
        self.worker_thread_pool = ThreadPoolExecutor(max_workers=10)
        self.scheduler = BlockingScheduler()
        self.scheduler.add_job(func=self.advance_clock, trigger='interval', seconds=1)
        t = Thread(target=self.scheduler.start)
        t.start()

    @staticmethod
    def get_instance():
        if BufferPPO.BUFFER_INSTANCE is None:
            BufferPPO.lock.acquire()
            if BufferPPO.BUFFER_INSTANCE is None:
                BufferPPO.BUFFER_INSTANCE = BufferPPO()
            BufferPPO.lock.release()
        return BufferPPO.BUFFER_INSTANCE

    def produce(self, req):
        self.env.produce(req)

    def advance_clock(self):
        self.env.advance_clock()
        self.worker_thread_pool.submit(self.consume)

    def consume(self):
        # 获取环境值
        state = self.env.get_state_for_RL()
        self.logger.debug('state' + str(state))
        if self.use_edf(state):
            action = [0] * self.env.action_dim
            if state[0] != 0:
                if state[0] <= 1:
                    action[0] = 1
                else:
                    action[0] = self.env.threshold / state[0]
        else:
            # actor得到action
            s_tensor = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            a_tensor = self.act(s_tensor)
            action = a_tensor.detach().cpu().numpy()[0]
        self.env.do_action(action)
        self.logger.debug('action' + str(self.env.action_probability_to_number(action)))
   
    def use_edf(self,state):
        num_state = []
        for s in state:
            if s != 0:
                num_state.append(s * self.env.threshold)
        if np.mean(num_state) <= self.env.threshold * (1.0 / 4.0):
            return True
        return False