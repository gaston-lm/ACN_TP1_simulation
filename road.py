import numpy as np

class RoadSimulation:
    def __init__(self, time_limit, a_max, b, delta, s_0, car_length):
        # Public
        self.time_limit = time_limit

        self.pos = np.zeros((1,time_limit))
        self.acc = np.zeros((1,time_limit))
        self.spd = np.zeros((1,time_limit))
        self.a_max = a_max
        self.delta = delta
        self.b = b
        self.s_0 = s_0
        self.car_length = car_length

        # Private
        self.headway = []
        self.time_out = []
        self.time_in = []
        self.collisioned = []
        self.collisioned_agents = set()
        self.arrived = set()
        self.collisions = 0

    def enter(self, a, t):
        if t != 0:
            new_agent = np.zeros((1,self.time_limit))
            self.pos = np.vstack((self.pos, new_agent))
            self.acc = np.vstack((self.acc, new_agent))
            self.spd = np.vstack((self.spd, new_agent))
        
        self.headway.append(np.random.lognormal(mean=0.15, sigma=0.22))
        self.collisioned.append(-1)

        spd = np.random.uniform(low=8.33, high=11.11, size=1).item() # Entre 30 y 45 km/h

        self.pos[a,t] = 1
        self.spd[a,t] = spd
        self.acc[a,t] = 0

        self.time_in.append(t)

    def update(self, t):
        i = 0
        while i < len(self.pos[:,t]):
            # Velocidad deseada del conductor (máxima de gral. paz ¿+ ruido?)
            v_0 = 22.22 
            if self.pos[i, t-1] > 13000:
                v_0 = 27.77
            
            # Actualización de la posición y velocidad en el segundo t. Física, no es una decisión del agente.
            self.pos[i, t] = self.pos[i, t-1] + self.spd[i, t-1] * 1 # unidad de tiempo (1s)
            self.spd[i, t] = max(0.0, self.spd[i, t-1] + self.acc[i, t-1] * 1) # unidad de tiempo (1s) 

            # Cuanto voy a acelerar en este período según la posición y velocidad del auto que tengo adelante. IDM Model.
            v = self.spd[i, t]
            s = self.pos[i-1, t] - self.pos[i, t] - self.car_length

            # Si soy el lider, acelero sin tener en cuenta al auto de adelante (no hay auto de adelante)
            if i == 0:
                acc = self.a_max * (1 - (v / v_0) ** self.delta)
            # Si no, acelero teniendo en cuenta mi distancia con el conductor de adelante y a cuantos segundos quiero estar del mismo, la velocidad deseada, y mas parámetros del modelo.
            else:
                s_star = self.s_0 + v * self.headway[i] + (v * (v - self.spd[i-1, t])) / (2 * np.sqrt(self.a_max * self.b))
                acc = self.a_max * (1 - (v / v_0) ** self.delta - (s_star / s) ** 2)
            
            # Límites físicos de la aceleración:
            if acc < - 4:
                acc = -4
            elif acc > 2:
                acc = 2

            # Distracciones y actualización de la matriz.
            indicadora = np.random.uniform(low=0, high=1)
            lm = 0.001

            if indicadora < lm:
                self.acc[i,t] = self.acc[i, t-1] # Me distraje y no modifiqué mi aceleración anterior.
            else:
                self.acc[i,t] = acc # Modifico la aceleracion acorde al modelo.

            if i != 0 and i not in self.collisioned_agents:
                if self.pos[i-1,t] - self.car_length <= self.pos[i,t]:
                    print("Choque de "+ str(i) + " con " + str(i-1) + " en t="+str(t))  # Choque leve < 13.88
                    self.collisioned_agents.add(i)
                    self.collisioned[i-1] = t              
                    self.collisioned[i] = t
                    self.collisions += 1

            if self.pos[i, t] >= 15500 and i not in self.arrived:
                self.time_out.append(t)
                self.arrived.add(i)

            i += 1

    def simulate(self):
        agents_enter = 0
        self.enter(agents_enter,0)
        t = 1
        agents_enter = 1

        while t < self.time_limit:
            self.update(t)
            # Con alguna proba entra un auto nuevo:
            if t % 2 == 0:
                self.enter(agents_enter, t)
                agents_enter += 1
            
            t += 1
    
    def get_avg_travel_time(self):
        time_out = np.array(self.time_out)
        time_in = np.array(self.time_in[:time_out.shape[0]])
        
        travel_time = time_out - time_in
        avg_travel_time = np.mean(travel_time)

        return avg_travel_time

    def get_avg_travel_speed(self):
        sum_spd = 0

        for i in range(len(self.arrived)):
            spd_agent = self.spd[i][self.time_in[i]:self.time_out[i]+1]
            sum_spd += np.mean(spd_agent)

        return sum_spd / len(self.time_out)

    def get_avg_travel_acce(self):
        sum_acc = 0

        for i in range(len(self.arrived)):
            spd_agent = self.acc[i][self.time_in[i]:self.time_out[i]+1]
            sum_acc += np.mean(spd_agent)

        return sum_acc / len(self.time_out)

    def get_collisions(self):
        return self.collisions