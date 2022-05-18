import time
import datetime
import sys
import os
import torch

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
# from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSim
import threading
from elegantrl.envs.request_env_no_sim_for_server import RequestEnvNoSimForServer
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from elegantrl.agents.AgentPPO import AgentPPO


class Buffer:
    BUFFER_INSTANCE = None
    env = RequestEnvNoSimForServer(action_is_probability=True)
    lock = threading.Lock()
    boss_thread_pool = ThreadPoolExecutor(max_workers=1)
    worker_thread_pool = ThreadPoolExecutor(max_workers=50)
    agent = AgentPPO
    act = agent(net_dim=2**7, state_dim=env.state_dim, action_dim=env.action_dim).act
    actor_path = rootPath + '/elegantrl/train/RequestEnvNoSim0.8_PPO_0/actor_01561000_06050.265.pth'
    act.load_state_dict(torch.load(actor_path, map_location=lambda storage, loc: storage))

    def __init__(self) -> None:
        self.env = RequestEnvNoSimForServer()
        t = Thread(target=self.consume)
        t.start()

    @staticmethod
    def get_instance():
        if Buffer.BUFFER_INSTANCE is None:
            Buffer.lock.acquire()
            if Buffer.BUFFER_INSTANCE is None:
                Buffer.BUFFER_INSTANCE = Buffer()
            Buffer.lock.release()
        return Buffer.BUFFER_INSTANCE

    def produce(self, req):
        self.env.produce(req)

    def consume(self):
        while True:
            # 获取环境值
            state = self.env.get_state()
            # actor得到action
            s_tensor = torch.as_tensor(state, dtype=torch.float32).unsqueeze(0)
            a_tensor = self.act(s_tensor)

    def env_step(self, action):
        return self.boss_thread_pool.submit(self.env.step, action).result()
