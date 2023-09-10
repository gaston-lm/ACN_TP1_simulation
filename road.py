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
        # To handle collisions
        self.collisioned = []
        self.collisioned_agents = set()
        self.collisions = 0
        # Results
        self.avg_travel_time = 0
        self.avg_travel_speed = 0
        self.avg_travel_acc = 0

    def enter(self, a, t):
        if t != 0:
            new_agent = np.zeros((1,self.time_limit))
            self.pos = np.vstack((self.pos, new_agent))
            self.acc = np.vstack((self.acc, new_agent))
            self.spd = np.vstack((self.spd, new_agent))
        
        # Definimos variables de cada agente
        hdw = np.random.lognormal(mean=0.15, sigma=0.22)
        self.headway.append(hdw)
        desired_speed_for_agent = np.random.normal(loc=20.27, scale=1)
        self.dsr_spd.append(desired_speed_for_agent)

        self.collisioned.append(-1)

        self.pos[a,t] = 0.5

        # Defino acc segun quien veo adelante.
        if t == 0:
            spd = np.random.uniform(low=8.33, high=9.72, size=1) # Entre 30 y 45 km/h
            self.spd[a,t] = spd
            self.acc[a,t] = self.a_max * (1 - (spd / 22.22) ** self.delta)

        else:
            spd_prev = np.random.uniform(low=8.33, high=9.72, size=1)
            acc_prev = min(2, max(-4 , self.a_max * (1 - (spd_prev / 22.22) ** self.delta - ((self.s_0 + spd_prev * hdw + (spd_prev * (spd_prev - self.spd[a-1, t])) / (2 * np.sqrt(self.a_max * self.b))) / (self.pos[a-1, t] - 1 - self.car_length)) ** 2)))
        
            spd = spd_prev + acc_prev
                
            self.spd[a,t] = spd
            self.acc[a,t] = min(2, max(-4, self.a_max * (1 - (spd / 22.22) ** self.delta - ((self.s_0 + spd * hdw + (spd * (spd - self.spd[a-1, t])) / (2 * np.sqrt(self.a_max * self.b))) / (self.pos[a-1, t] - 1 - self.car_length)) ** 2)))

        # Registro entrada de autos a partir de llegado el primero
        if self.flag_first_arrived:
            self.time_in.append(t)
            # Tomo agentes para salida a partir de este id (es el primero que se empieza a tener en cuenta)
            if self.id_first_agent_to_consider == -1:
                self.id_first_agent_to_consider = a
    
    def update_pos(self, i, t):
        pos_noise = 0
        if self.collisioned[i] != -1: # si este auto choco, no le puedo sumar ruido, debe bajar o mantenerse en 0
            pos_noise = np.random.normal(loc=0,scale=0.7)

        self.pos[i, t] = self.pos[i, t-1] + self.spd[i, t-1] * 1 + pos_noise # unidad de tiempo (1s)

    def update_spd(self, i, t):
        spd_noise = 0
        if self.collisioned[i] != -1: # si este auto choco, no le puedo sumar ruido, debe bajar o mantenerse en 0
            spd_noise = np.random.normal(loc=0,scale=0.3)

        self.spd[i, t] = max(0.0, self.spd[i, t-1] + self.acc[i, t-1] * 1 + spd_noise) # unidad de tiempo (1s) 

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
        
        # Ruido acc
        acc_noise = np.random.normal(loc=0,scale=0.5)
        acc = acc + acc_noise

        # Límites físicos de la aceleración:
        if acc < - 4.0:
            acc = -4.0
        elif acc > 2.0:
            acc = 2.0

        # Distracciones y actualización de la matriz.
        indicadora = np.random.uniform(low=0, high=1)
        lm = 0.02

        if indicadora < lm:
            # print("Uy me distraje en "+str(t) +", soy "+str(i))
            self.acc[i,t] = self.acc[i, t-1] # Me distraje y no modifiqué mi aceleración anterior.
        elif indicadora < 0.0001:
            print("Distracción extrema")
            self.acc[i,t] = acc + np.random.normal(loc=0, scale=0.5)
        else:
            self.acc[i,t] = acc # Modifico la aceleracion acorde al modelo.

    def dsr_spd_based_on_pos(self, i, t, v_0):
        new_v_0 = v_0
        # Si pasó Acceso Norte, dónde la velocidad máxima pasa 100km/h
        if self.pos[i, t-1] > 13000:
            diferencia = 22.22 - v_0 # Si v_0 > 22.22 le gusta ir más rápido, su nueva v_0 también es mayor que 27.77.
            new_v_0 = 27.77 - diferencia 

        # Chequeo si el auto esta por llegar a una entrada
        # interceptions = [
        #     (800, 900), (1800, 1900), (2400, 2500), 
        #     (3500, 3600), (6600, 6700), (7500, 7600), 
        #     (9700, 9800), (11500, 12500)
        # ] # Lista de todas las intercepciones en los primeros 13.000 metros (hasta acceso norte)

        entradas = [(2500, 2650), (4350,4500),(5900, 6050),(7450, 7800),(12550, 12700)]

        if any(start < self.pos[i, t-1] < end for start, end in entradas):
            diferencia = 22.2 - v_0 
            new_v_0 = 18.5 - diferencia

        # if 13500 < self.pos[i, t-1] < 13530:
        #     diferencia = 27.77 - v_0 
        #     v_0 = 16.67 - diferencia

        return new_v_0
    
    def dsr_spd_change(self, i, t):
        # Calculamos su desird speed basado en sus caracteristicas de conductor + pos
        v_0 = self.dsr_spd_based_on_pos(i, t, self.dsr_spd[i])

        # Con cieta proba le sumamos ruido
        p = np.random.uniform(low=0, high=1)
        v_0_noise = 0
        
        if p > 0.5:
            v_0_noise = np.random.normal(loc=0, scale=1.5)

        return v_0 + v_0_noise
    
    def verify_colision(self, i, t):
        if self.collisioned[i] != -1 and t < self.collisioned[i]: # Si este auto choco, verifico que el tiempo para frenar siga vigente para desacelerar manera realista
            print("Soy " + str(i) + ". Frené por choque. Me falta " + str(self.collisioned[i]-t))
            if self.spd[i,t] > 0.5: # Si aun me queda por frenar
                self.acc[i,t] = -self.b / 2 # no freno tan brusco
            else:
                self.acc[i,t] = 0

            # Le resto tiempo que aun tiene que esperar para comenzar de nuevo a andar
            self.collisioned[i] -= 1
            
        elif self.collisioned[i] == 0:
            # Ya paso el tiempo, vuelve a arrancar
            self.acc[i,t] = 1.67 # Chequear: creo q esto no hace falta, calcula en siguiente t
            self.collisioned[i] = -1
            self.collisioned_agents.remove(i)
            
    def identify_colision(self, i, t):
        if i != 0 and i not in self.collisioned_agents:
            if self.pos[i-1,t] - self.car_length <= self.pos[i,t]: 
                if self.pos[i,t-4] < 2:
                    print("Recien había entrado y ya choque :(")
                print("Choque de " + str(i) + " con " + str(i-1) + " en t = " + str(t))  # Choque leve < 13.88

                # Registrar choque y agentes involucrados
                self.collisions += 1
                self.collisioned_agents.add(i)
                self.collisioned_agents.add(i-1)
                self.collisioned[i] = t + (self.spd[i,t] // self.b) + 60 # Sumamos tiempo que requerira frenarse por completo + tiempo para pasarse datos del seguro
                self.collisioned[i-1] = t + (self.spd[i-1,t] // self.b) + 60 

    def update(self, t):
        i = 0
        while i < len(self.pos[:,t]):
            # Velocidad deseada del conductor dado por sus caracteristicas + max_spd en ese lugar + ruido
            v_0 = self.dsr_spd_change(i, t)
            
            # Actualización de la posición y velocidad en el segundo t. Física, no es una decisión del agente.
            self.update_pos(i, t)
            self.update_spd(i, t)
            
            # Actualización de la aceleración
            self.update_acc(i, t, v_0)

            # Manejo las colisiones
            self.verify_colision(i, t)
            self.identify_colision(i, t)
            
            # Registro de llegada de agentes
            if self.pos[i, t] >= 15500 and i not in self.arrived:
                if i == 0:
                    self.flag_first_arrived = True
                    self.arrived.add(i)
                    print("El primero llego en t="+str(t))
                    print("Cantidad de autos ahi: "+str(len(self.pos[:,t])))
                elif i < self.id_first_agent_to_consider:
                    self.arrived.add(i)
                elif i >= self.id_first_agent_to_consider:
                    print(i,t)
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
            p = np.random.uniform(low=0, high=1, size=1).item()
            umbral = 0.7 # 0: Horario pico, 0.5: Normal, 0.7 Madrugada
            # if 800 < t < 4400: # de 5 a 6
            #     umbral = 0.8
            # elif 4400 < t < 8000: # de 6 a 7
            #     umbral = 0.5
            # elif 8000 < t < 11600: # de 7 a 8
            #     umbral = 0
            # elif 11600 < t < 15200: # de 8 a 9
            #     umbral = 0.2
            # elif 15200 < t < 18800: # de 9 a 10
            #     umbral = 0.3
            # else:
            #     umbral = 0.5

            if self.pos[agents_enter-1,t] > 10 and p > umbral:
                self.enter(agents_enter, t)
                agents_enter += 1
            
            t += 1
    
    def generate_results(self):
        self.time_out = np.array(self.time_out)
        self.time_in = np.array(self.time_in[:self.time_out.shape[0]])

        # Calcular tiempo promedio de viaje
        travel_time = self.time_out - self.time_in
        avg_travel_time = np.mean(travel_time)

        self.avg_travel_time = avg_travel_time

        # Calcular velocidad promedio
        sum_spd = 0
        for i in range(len(self.time_out)):
            spd_agent = self.spd[self.id_first_agent_to_consider + i][self.time_in[i]:self.time_out[i]]
            sum_spd += np.mean(spd_agent)

        self.avg_travel_speed = sum_spd / len(self.time_out)

        # Calcular aceleración promedio
        sum_acc = 0
        for i in range(len(self.time_out)):
            acc_agent = self.acc[self.id_first_agent_to_consider + i][self.time_in[i]:self.time_out[i]]
            sum_acc += np.mean(acc_agent)

        self.avg_travel_acc = sum_acc / len(self.time_out)
        
    def get_avg_travel_time(self):
        return self.avg_travel_time

    def get_avg_travel_speed(self):
        return self.avg_travel_speed

    def get_avg_travel_acce(self):
        return self.avg_travel_acc

    def get_collisions(self):
        return self.collisions