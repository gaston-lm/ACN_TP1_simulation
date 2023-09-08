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

        # Para calcular stats después que llegó el primer auto

        # Flag de primer auto llegó
        self.flag_first_arrived = False
        # Id del primer 
        self.id_first_agent_to_consider = -1

        # Private
        
        # For each agent
        self.dsr_spd = []
        self.headway = []
        # For results
        self.time_out = []
        self.time_in = []
        self.arrived = set()
        # To handdle collisions
        self.collisioned = []
        self.collisioned_agents = set()
        self.collisions = 0


    def enter(self, a, t):
        if t != 0:
            new_agent = np.zeros((1,self.time_limit))
            self.pos = np.vstack((self.pos, new_agent))
            self.acc = np.vstack((self.acc, new_agent))
            self.spd = np.vstack((self.spd, new_agent))
        
        # Definimos variables de cada agente
        hdw = np.random.lognormal(mean=0.15, sigma=0.22)
        self.headway.append(hdw)
        # desired_speed_for_agent = np.random
        # self.dsr_spd.append

        self.collisioned.append(-1)

        self.pos[a,t] = 0.5

        # defino acc segun quien veo adelante
        if t == 0:
            spd = np.random.uniform(low=8.33, high=9.72, size=1) # Entre 30 y 45 km/h
            self.spd[a,t] = spd
            self.acc[a,t] = self.a_max * (1 - (spd / 22.22) ** self.delta)
        else:
            spd = self.spd[a-1,t] + np.random.lognormal(mean=0,sigma=0.3)
            self.spd[a,t] = spd
            s = self.pos[a-1, t] - 1 - self.car_length
            s_star = self.s_0 + spd * hdw + (spd * (spd - self.spd[a-1, t])) / (2 * np.sqrt(self.a_max * self.b))
            self.acc[a,t] = self.a_max * (1 - (spd / 22.22) ** self.delta - (s_star / s) ** 2)

        self.time_in.append(t)

    def update_acc(self, i, t, v_0):
            v = self.spd[i, t]
            # Si soy el lider, acelero sin tener en cuenta al auto de adelante (no hay auto de adelante)
            if i == 0:
                acc = self.a_max * (1 - (v / v_0) ** self.delta)
            # Si no, acelero teniendo en cuenta mi distancia con el conductor de adelante y a cuantos segundos quiero estar del mismo, la velocidad deseada, y mas parámetros del modelo.
            else:
                s = self.pos[i-1, t] - self.pos[i, t] - self.car_length
                s_star = self.s_0 + v * self.headway[i] + (v * (v - self.spd[i-1, t])) / (2 * np.sqrt(self.a_max * self.b))
                acc = self.a_max * (1 - (v / v_0) ** self.delta - (s_star / s) ** 2)
            
            # Límites físicos de la aceleración:
            if acc < - 4.0:
                acc = -4.0
            elif acc > 2.0:
                acc = 2.0

            # Distracciones y actualización de la matriz.

            indicadora = np.random.uniform(low=0, high=1)
            lm = 0.07

            if indicadora < lm:
                # print("Uy me distraje en "+str(t) +", soy "+str(i))
                self.acc[i,t] = self.acc[i, t-1] # Me distraje y no modifiqué mi aceleración anterior.
            else:
                self.acc[i,t] = acc # Modifico la aceleracion acorde al modelo.

    def verify_colission(self, i, t):
            if self.collisioned[i] != -1 and t < self.collisioned[i]: # si este auto choco, verifico que el tiempo para frenar siga vigente para desacelerar manera realista
                print("Soy " +str(i)+".Frené pq choque. me falta " + str(self.collisioned[i]-t))
                if self.spd[i,t] > 0.5: # si aun me queda por frenar
                    self.acc[i,t] = -self.b
                else:
                    self.acc[i,t] = 0

                # le resto tiempo que aun tiene que esperar para comenzar de nuevo a andar
                self.collisioned[i] -= 1
                
            elif self.collisioned[i] == 0:
                # Ya paso el tiempo, vuelve a arrancar
                self.acc[i,t] = 1.67 # chquear
                self.collisioned[i] = -1
            
    def identify_colission(self, i, t):
            if i != 0 and i not in self.collisioned_agents:
                if self.pos[i-1,t] - self.car_length <= self.pos[i,t]: 
                    if self.pos[i,t-4] < 2:
                        print("recien habia entrado y ya choque")
                    print("Choque de "+ str(i) + " con " + str(i-1) + " en t="+str(t))  # Choque leve < 13.88

                    # Registrar choque y agentes involucrados
                    self.collisions += 1
                    self.collisioned_agents.add(i)
                    self.collisioned_agents.add(i-1)
                    self.collisioned[i] = t + (self.spd[i,t] // self.b) + 60 # sumamos tiempo que requerira frenarse por completo + tiempo para pasarse datos del seguro
                    self.collisioned[i-1] = t + (self.spd[i-1,t] // self.b) + 60 

    def update(self, t):
        i = 0
        while i < len(self.pos[:,t]):
            # Velocidad deseada del conductor (máxima de gral. paz ¿+ ruido?)
            v_0 = self.dsr_spd[i]
            if self.pos[i, t-1] > 13000:
                diferencia = 22.22 - v_0 # si v_0 > 22.22 le gusta ir más rápido, su nueva v_0 también es mayor q 27.77
                v_0 = 27.77 - diferencia 
            
            # Chequeo si el auto esta por llegar a una entrada
            interceptions = [
                (800, 1000), (1800, 2000), (2400, 2600), 
                (3500, 3700), (6600, 6700), (7500, 7700), 
                (9700, 9900), (11500, 13500)
            ] # Lista de todas las intercepciones en los primeros 13.000 metros (hasta acceso norte)

            if any(start < self.pos[i, t-1] < end for start, end in interceptions):
                diferencia = 22.2 - v_0 
                v_0 = 15.27 - diferencia
            
            # Actualización de la posición y velocidad en el segundo t. Física, no es una decisión del agente.
            self.pos[i, t] = self.pos[i, t-1] + self.spd[i, t-1] * 1 # unidad de tiempo (1s)
            self.spd[i, t] = max(0.0, self.spd[i, t-1] + self.acc[i, t-1] * 1) # unidad de tiempo (1s) 

            self.update_acc(i, t, v_0) # Actualización de la aceleración

            # Manejo las colisiones

            self.verify_colission(i, t)
            self.identify_colission(i, t)
                  
            # Registro de llegada de agentes
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
            # if t % 2 == 0:
            if self.pos[agents_enter-1,t] > 10:
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