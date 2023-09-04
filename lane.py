import numpy as np
from agent import *
from typing import List

class Lane_simulation:
    def __init__(self, time_limit, agents, alpha, l, m):
        # Pre: agents <= time 
        self.time:int = 0
        self.time_limit:int = time_limit
        self.agents:int = agents

        self.pos:List[List[float]] = np.array(([[0.0]*agents])*time_limit)
        self.acc:List[List[float]] = np.array(([[0.0]*agents])*time_limit)
        self.spd:List[List[float]] = np.array(([[0.0]*agents])*time_limit)

        # self.lane:List[Agent] = []

        self.alpha = alpha
        self.l = l
        self.m = m

    def enter(self, a:int, t:int):
        spd:float = np.random.uniform(low=8.33, high=8.34, size=1).item() # Entre 30 y 60 km/h
        # self.lane.append(Agent(id=a, position=0, speed=spd, acceleration=0))
        self.pos[a,t] = 1
        self.spd[a,t] = spd
        self.acc[a,t] = 0

    def update(self, t):
        i = 0
        while i < len(self.acc[:t]):
            # update pos
            self.pos[i,t] = self.pos[i,t-1] + self.spd[i,t-1] * 1

            # update spd
            self.spd[i,t] = self.spd[i,t-1] + self.acc[i,t-1] * 1

            # update acc

            # De Liniers a Acceso Norte es 80km/h
            max_spd:float = 22.22 # 80 km/h en m/s
            if self.pos[i,t-1] > 10000:
                max_spd = 27.77 # 100 km/h

            if i == 0:
                new_acc = 3.5
            else:
                if self.pos[i-1,t-1] < self.pos[i,t-1]:
                    print("Choque de "+str(i)+" con "+str(i-1)+" en t="+str(t))
                new_acc = ((self.alpha * self.spd[i,t-1]**self.m) / (self.pos[i-1,t-1] - self.pos[i,t-1])**self.l) * (self.spd[i-1,t-1] - self.spd[i,t-1])
            
            if new_acc > 3.5:
                new_acc = 3.5
            elif new_acc < -3.5:
                new_acc = -3.5

            if self.spd[i,t] + new_acc <= max_spd:
                self.acc[i,t] = new_acc # + random error * Indicadora (se distrajo o no) --> poisson?
            else:
                self.acc[i,t] = max_spd - self.spd[i,t]
            
            i += 1
    
    def simulation(self):
        agents_enter = 0
        for t in range(self.time_limit):
            if self.agents > agents_enter:
                # Con alguna proba:
                self.enter(agents_enter, t)
                agents_enter += 1
            
            if t == 0:
                continue
            else:
                self.update(t)

            # for agent in self.lane:
            #     self.pos[agent.id,t] = agent.pos
            #     self.spd[agent.id,t] = agent.spd
            #     self.acc[agent.id,t] = agent.acc

            #     # Si ya termino el viaje, borramos al Agent.
            #     if agent.pos > 12700:
            #         self.lane.pop(0) # Eliminamos el primero (el que iba adelante y llegó).

            #     neigbour_prev_pos = self.pos[agent.id - 1, t - 1]
            #     neigbour_prev_spd = self.spd[agent.id - 1, t - 1]
            #     self_prev_pos = self.pos[agent.id, t-1]
            #     self_prev_spd = self.spd[agent.id, t-1]
            #     self_prev_acc = self.acc[agent.id, t-1]
            #     if agent.id == 0:
            #         agent.update_first()
            #     else:
            #         agent.update(self_prev_pos, self_prev_spd, self_prev_acc, neigbour_prev_pos, neigbour_prev_spd, self.alpha, self.l, self.m) # Otra función para el primero? Es el único que no necesita al vecino. Otra opción sería que cada agent tenga almacenado a su vecino.