import numpy as np

class RoadSimulation:
    def __init__(self, time_limit, delta_t, a_max, b, delta, s_0, car_length):
        self.time_limit = time_limit

        self.pos = np.zeros((1,time_limit))
        self.acc = np.zeros((1,time_limit))
        self.spd = np.zeros((1,time_limit))
        self.delta_t = delta_t
        self.a_max = a_max
        self.delta = delta
        self.b = b
        self.s_0 = s_0
        self.car_length = car_length

        self.headway = []
        self.time_out = []
        self.time_in = []
        self.arrived = set()

    def enter(self, a, t):
        if t != 0:
            new_agent = np.zeros((1,self.time_limit))
            self.pos = np.vstack((self.pos, new_agent))
            self.acc = np.vstack((self.acc, new_agent))
            self.spd = np.vstack((self.spd, new_agent))
        
        self.headway.append(np.random.lognormal(mean=0.15, sigma=0.22))

        spd = np.random.uniform(low=8.33, high=11.11, size=1).item() # Entre 30 y 45 km/h

        self.pos[a,t] = 1
        self.spd[a,t] = spd
        self.acc[a,t] = 0

        self.time_in.append(t)

    def update(self, t):
        i = 0
        chocados_test = set()
        while i < len(self.pos[:,t]):
            
            # velocidad deseada v_0
            v_0 = 22.22 
            if self.pos[i, t-1] > 13000:
                v_0 = 27.77
            
            self.pos[i, t] = self.pos[i, t-1] + self.spd[i, t-1] * self.delta_t
            self.spd[i, t] = max(0.0, self.spd[i, t-1] + self.acc[i, t-1] * self.delta_t)

            if i == 0:
                acc = self.a_max
            else:
                v = self.spd[i, t]
                s = self.pos[i, t] - self.pos[i-1, t] - self.car_length

                s_star = self.s_0 + v*self.headway[i] + (v * (v - self.spd[i-1, t])) / (2*np.sqrt(self.a_max*self.b))
                acc = self.a_max * (1 - (v / v_0) ** self.delta - (s_star / s) ** 2)
            
            if acc + self.spd[i,t] > v_0:
                acc = v_0 - self.spd[i,t]
            
            acc_noise = np.random.normal(loc=0, scale=0.25)
            indicadora = np.random.uniform(low=0, high=1)
            lm = 0.001

            if indicadora < lm:
                magnitud = np.random.normal(loc=0, scale=1.5) 
                self.acc[i,t] = acc + acc_noise + magnitud
            else:
                self.acc[i,t] = acc + acc_noise

            # ver bien desp
            if acc < -8:
                print("Mucho frenado de " + str(i) + " en t=" + str(t))

            if i != 0 and i not in chocados_test:
                if self.pos[i-1,t] < self.pos[i,t]:
                    print("Choque de "+ str(i) + " con " + str(i-1) + " en t="+str(t))
                    chocados_test.add(i)
                    chocados_test.add(i-1)

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
            p = np.random.random(size=1)
            # Con alguna proba entra un auto nuevo:
            if p > 0.5:
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
