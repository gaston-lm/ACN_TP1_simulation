import numpy as np
from agent import *
from typing import List

class Lane_simulation:
    def __init__(self, time_limit, agents, alpha, l, m):
        self.time_limit:int = time_limit

        self.pos:List[List[float]] = np.zeros((1,time_limit))
        self.acc:List[List[float]] = np.zeros((1,time_limit))
        self.spd:List[List[float]] = np.zeros((1,time_limit))

        self.alpha = alpha
        self.l = l
        self.m = m

    def enter(self, a:int, t:int):
        if t != 0:
            new_agent = np.zeros((1,self.time_limit))
            self.pos = np.vstack((self.pos, new_agent))
            self.acc = np.vstack((self.acc, new_agent))
            self.spd = np.vstack((self.spd, new_agent))
        
        spd:float = np.random.uniform(low=8.33, high=11.11, size=1).item() # Entre 30 y 45 km/h
        self.pos[a,t] = 1
        self.spd[a,t] = spd
        self.acc[a,t] = 0

    def update(self, t):
        i = 0
        while i < len(self.acc[:t]):
            # update pos
            # pos_noise = np.random.normal(loc=0.0, scale=1.0)
            pos_noise = 0
            self.pos[i,t] = self.pos[i,t-1] + self.spd[i,t-1] * 1 + pos_noise

            # update spd
            # spd_noise = np.random.normal(loc=0.0, scale=0.5)
            spd_noise = 0
            self.spd[i,t] = self.spd[i,t-1] + self.acc[i,t-1] * 1 + spd_noise

            # update acc

            # De Liniers a Acceso Norte es 80km/h
            max_spd:float = 22.22 # 80 km/h en m/s
            if self.pos[i,t-1] > 13000:
                max_spd = 27.77 # 100 km/h

            if i == 0:
                new_acc = 5
            else:
                new_acc = ((self.alpha * self.spd[i,t-1]**self.m) / (self.pos[i-1,t-1] - self.pos[i,t-1])**self.l) * (self.spd[i-1,t-1] - self.spd[i,t-1])


            if new_acc > 5:
                new_acc = 5
            elif new_acc < -8.82:
                print("me quede corto")
                new_acc = -8.82

            if self.spd[i,t] + new_acc <= max_spd:
                self.acc[i,t] = new_acc # + random error * Indicadora (se distrajo o no) --> poisson?
            else:
                self.acc[i,t] = max_spd - self.spd[i,t]
            
            if i != 0:
                if self.pos[i-1,t] < self.pos[i,t]:
                    print("Choque de "+str(i)+" con "+str(i-1)+" en t="+str(t))

            i += 1
    
    def simulation(self):
        agents_enter = 0
        self.enter(agents_enter,0)
        t = 1
        agents_enter = 1
        while t < self.time_limit:
            
            self.update(t)

            p = np.random.random(size=1)
            # Con alguna proba entra un auto nuevo:
            if p > 0.5:
                self.enter(agents_enter, t)
                agents_enter += 1
            
            t += 1