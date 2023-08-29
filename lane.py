import numpy as np
from agent import *
from typing import List

class Lane_simulation:
    def __init__(self, time_limit, agents):
        # Pre: agents <= time 
        self.time:int = 0
        self.time_limit:int = time_limit
        self.agents:int = agents

        self.pos:List[List[float]] = np.array(([[-1]*agents])*time_limit)
        self.acc:List[List[float]] = np.array(([[-1]*agents])*time_limit)
        self.spd:List[List[float]] = np.array(([[-1]*agents])*time_limit)

        self.lane:List[Agent] = []

    def enter(self, a:int, t:int):
        spd:float = np.random.uniform(low=8.33, high=16.66, size=1).item() # Entre 30 y 60 km/h
        self.lane.append(Agent(id=a, position=0, speed=spd, acceleration=0))
        self.pos[a,t] = 0
        self.spd[a,t] = spd
        self.acc[a,t] = 0
    
    def simulation(self):
        agents_enter = 0
        for t in range(self.time_limit):
            if self.agents > agents_enter:
                # Con alguna proba:
                self.enter(agents_enter, t)
                agents_enter += 1

            for agent in self.lane:
                self.pos[agent.id,t] = agent.pos
                self.spd[agent.id,t] = agent.spd
                self.acc[agent.id,t] = agent.acc

                # Si ya termino el viaje, borramos al Agent.
                if agent.pos > 12700:
                    self.lane.remove[0] # Eliminamos el primero (el que iba adelante y llegó).

                agent.update(self.lane[agent.id + 1]) # Otra función para el primero? Es el único que no necesita al vecino. Otra opción sería que cada agent tenga almacenado a su vecino.