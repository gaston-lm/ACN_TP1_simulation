import typing
import numpy as np
from agent import *

class Lane_simulation:
    def __init__(self, time_limit, agents):

        self.time:int = 0
        self.time_limit:int = time_limit
        self.agents:int = agents

        self.pos:List[List[float]] = np.array(([-1]*agents)*time_limit)
        self.acc:List[List[float]] = np.array(([-1]*agents)*time_limit)
        self.spd:List[List[float]] = np.array(([-1]*agents)*time_limit)

        self.lane:List[Agent] = []

    def ingreso(self):
        spd = np.random.uniform(low=35, high=55, size=1)
        self.lane.append(Agent(pos=0, speed=spd, acceleration=0))
    