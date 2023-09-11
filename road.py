import numpy as np

class RoadSimulation:
    def __init__(self, time_limit, a_max, b, delta, s_0, car_length, alert_app_prop):
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
        # For each agent
        self.dsr_spd = []
        self.headway_mean = []
        self.headway = []

        # For results
        self.time_out = []
        self.time_in = []
        self.arrived = set()

        # To handle collisions
        self.collisioned = []
        self.collisioned_agents = set()
        self.collisions = dict()
        self.collisions_in_radar = dict()

        # Results
        self.results = np.empty((0,0))
        self.avg_travel_time = 0
        self.avg_travel_speed = 0
        self.avg_travel_acc = 0

        # Para calcular stats después que llegó el primer auto
        # Flag de primer auto llegó
        self.flag_first_arrived = False
        # Id del primer 
        self.id_first_agent_to_consider = -1

        # For cool finding / hypotesis
        self.alert_app_prop = alert_app_prop
        self.uses_alert_app = []

    def agent_attr(self):
        # Headway
        hdw = np.random.lognormal(mean=0.5, sigma=0.21)
        # Media de headway para este agente
        self.headway_mean.append(hdw)
        # Donde se registra el headway con cierta variabilidad cada 30 segundos
        self.headway.append(hdw)

        # Velocidad deseada
        desired_speed_for_agent = 0
        if hdw < 1.2:
            # Son loquitos
            desired_speed_for_agent = 22.22 + np.random.lognormal(mean=1.5, sigma=0.25)
        elif 1.2 < hdw < 1.5:
            # Van más rápido
            desired_speed_for_agent = 22.22 + np.random.uniform(low=0, high=4)
        elif 1.5 < hdw < 1.8:
            # Van normal
            desired_speed_for_agent = 21.80 + np.random.normal(loc=0, scale=0.4)
        else:
            # Vam más lento
            desired_speed_for_agent = 19.44 + np.random.normal(loc=0, scale=0.8)
       
        self.dsr_spd.append(desired_speed_for_agent)

        # Usa o no app de alerta de radares
        p = np.random.uniform(low=0, high=1)
        if p > self.alert_app_prop:
            self.uses_alert_app.append(True)
        else:
            self.uses_alert_app.append(False)

    def enter(self, a, t):
        if t != 0:
            new_agent = np.zeros((1,self.time_limit))
            self.pos = np.vstack((self.pos, new_agent))
            self.acc = np.vstack((self.acc, new_agent))
            self.spd = np.vstack((self.spd, new_agent))

        # Definimos atributos del agente entrando
        self.agent_attr()

        # Vector para registrar tiempo a esperar si choco
        self.collisioned.append(-1)

        self.pos[a,t] = 0.5

        # Defino acc segun quien veo adelante.
        if t == 0:
            spd = np.random.uniform(low=8.33, high=9.72, size=1) # Entre 30 y 45 km/h
            self.spd[a,t] = spd
            self.acc[a,t] = self.a_max * (1 - (spd / 22.22) ** self.delta)

        else:
            spd_prev = np.random.uniform(low=8.33, high=9.72, size=1)
            acc_prev = min(2, max(-4 , self.a_max * (1 - (spd_prev / 22.22) ** self.delta - ((self.s_0 + spd_prev * self.headway[a] + (spd_prev * (spd_prev - self.spd[a-1, t])) / (2 * np.sqrt(self.a_max * self.b))) / (self.pos[a-1, t] - 1 - self.car_length)) ** 2)))
        
            spd = spd_prev + acc_prev
                
            self.spd[a,t] = spd
            self.acc[a,t] = min(2, max(-4, self.a_max * (1 - (spd / 22.22) ** self.delta - ((self.s_0 + spd * self.headway[a] + (spd * (spd - self.spd[a-1, t])) / (2 * np.sqrt(self.a_max * self.b))) / (self.pos[a-1, t] - 1 - self.car_length)) ** 2)))

        # Registro entrada de autos a partir de llegado el primero
        if self.flag_first_arrived:
            self.time_in.append(t)
            # Tomo agentes para salida a partir de este id (es el primero que se empieza a tener en cuenta)
            if self.id_first_agent_to_consider == -1:
                self.id_first_agent_to_consider = a
    
    def update_pos(self, i, t):
        pos_noise = 0
        # Si este auto choco, no le puedo sumar ruido, debe bajar o mantenerse en 0
        if self.collisioned[i] != -1 and self.spd[i,t] > 0: 
            pos_noise = np.random.normal(loc=0,scale=0.6)

        self.pos[i, t] = pos_noise + self.pos[i, t-1] + self.spd[i, t-1] * 1 # unidad de tiempo (1s)

    def update_spd(self, i, t):
        spd_noise = 0
        # Si este auto choco, no le puedo sumar ruido, debe bajar o mantenerse en 0
        if self.collisioned[i] != -1 and self.spd[i,t] > 0: 
            spd_noise = np.random.normal(loc=0,scale=0.3)

        self.spd[i, t] = max(0.0, spd_noise + self.spd[i, t-1] + self.acc[i, t-1] * 1) # unidad de tiempo (1s) 

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
        acc_noise = np.random.normal(loc=0,scale=0.15)
        acc = acc + acc_noise

        # Límites físicos de la aceleración:
        if acc < - 4.0:
            acc = -4.0
        elif acc > 2.0:
            acc = 2.0

        # Distracciones y actualización de la matriz.
        indicadora = np.random.uniform(low=0, high=1)
        lm = 0.02

        if indicadora < 0.001:
            # Distracción "fuerte"
            # print("Distracción más fuerte")
            self.acc[i,t] = acc - abs(np.random.normal(loc=0, scale=3))
        elif indicadora < lm:
            # Distación "leve"
            # Se distrajo y no modifica la aceleración anterior.
            self.acc[i,t] = self.acc[i, t-1]
            # print("Uy me distraje en "+str(t) +", soy "+str(i))
        else:
            # Modifico la aceleracion acorde al modelo.
            self.acc[i,t] = acc

    def is_in_radar_window(self, i, t):
        vr = False

        # Hay radares en: 2.4k, 6.5k, 12.2k
        radar_windows = [(2000, 2550),(6000, 6650),(11700, 12350)]
        
        if any(start < self.pos[i, t] < end for start, end in radar_windows):
            vr = True

        return vr

    def dsr_spd_based_on_pos(self, i, t, v_0):
        new_v_0 = v_0
        # Si pasó Acceso Norte, dónde la velocidad máxima pasa 100km/h
        if self.pos[i, t-1] > 13000:
            diferencia = 22.22 - v_0 # Si v_0 > 22.22 le gusta ir más rápido, su nueva v_0 también es mayor que 27.77.
            new_v_0 = 27.77 - diferencia 

        if self.is_in_radar_window(i, t-1):
            if self.uses_alert_app[i] and v_0 > 21.5:
                new_v_0 = 21

        return new_v_0
    
    def dsr_spd_change(self, i, t):
        # Calculamos su desired speed basado en sus caracteristicas de conductor + pos
        v_0 = self.dsr_spd_based_on_pos(i, t, self.dsr_spd[i])

        # Con cieta proba le sumamos ruido
        p = np.random.uniform(low=0, high=1)
        v_0_noise = 0
        
        if p > 0.5:
            v_0_noise = np.random.normal(loc=0, scale=1.5)

        return v_0 + v_0_noise
    
    def update_headway(self, i, t):
        p = np.random.uniform(low=0, high=1)
        if p > 0.60 and t % 30 == 0:
            # print("Cambio headway el agente "+str(i))
            self.headway[i] = self.headway_mean[i] + np.random.normal(loc=0, scale=0.3)
    
    def verify_colision(self, i, t):
        if self.collisioned[i] != -1 and t < self.collisioned[i]: # Si este auto choco, verifico que el tiempo para frenar siga vigente para desacelerar manera realista
            # print("Soy " + str(i) + ". Frené por choque. Me falta " + str(self.collisioned[i]-t))
            if self.spd[i,t] > 0.5: # Si aun me queda por frenar
                self.acc[i,t] = -self.b / 2 # no freno tan brusco
            else:
                self.acc[i,t] = 0
                self.spd[i,t] = 0
                self.pos[i,t] = self.pos[i, t-1]
            
        elif self.collisioned[i] == 0:
            # Ya paso el tiempo, vuelve a arrancar
            self.acc[i,t] = 1.67 # Chequear: creo q esto no hace falta, calcula en siguiente t
            self.collisioned[i] = -1
            self.collisioned_agents.remove(i)
            
    def identify_colision(self, i, t):
        if (i != 0) and (i not in self.collisioned_agents) and (self.pos[i,t] < 15500):
            if self.pos[i-1,t] - self.car_length <= self.pos[i,t]: 
                if self.pos[i,t-4] < 2:
                    print("Recien había entrado y ya choque :(")
                
                print("Choque de " + str(i) + " con " + str(i-1) + " en t = " + str(t) + " en " + str(self.pos[i,t]))  # Choque leve < 13.88

                # Registrar choque y agentes involucrados
                self.collisioned_agents.add(i)
                self.collisioned_agents.add(i-1)
                self.collisioned[i] = t + (self.spd[i,t] // self.b) + 120 # Sumamos tiempo que requerira frenarse por completo + tiempo para pasarse datos del seguro
                self.collisioned[i-1] = t + (self.spd[i-1,t] // self.b) + 120 

                if self.is_in_radar_window(i, t):
                    self.collisions_in_radar[i] = (t, self.pos[i,t])
                    self.collisions_in_radar[i-1] = (t, self.pos[i-1,t])
                else:
                    self.collisions[i] = (t, self.pos[i,t])
                    self.collisions[i-1] = (t, self.pos[i-1,t])

    def update(self, t):
        i = 0
        while i < len(self.pos[:,t]):
            # Velocidad deseada del conductor dado por sus caracteristicas + max_spd en ese lugar + ruido
            v_0 = self.dsr_spd_change(i, t)

            # Con cierta proba y frecuenta modifica su headway
            self.update_headway(i, t)
            
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
                    if i != 1: # no entiendo pq a veces entra el 1 acá y entonces se rompe todo los resultados
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
            umbral = 0 # 0: Horario pico, 0.5: Normal, 0.7 Madrugada
            if 0 < t < 4400: # de 5 a 6
                umbral = 0.9
            elif 4400 < t < 8000: # de 6 a 7
                umbral = 0.5
            elif 8000 < t < 11600: # de 7 a 8
                umbral = 0
            elif 11600 < t < 15200: # de 8 a 9
                umbral = 0.2
            elif 15200 < t < 18800: # de 9 a 10
                umbral = 0.4
            else:
                umbral = 0.5

            if self.pos[agents_enter-1,t] > 10 and p > umbral:
                self.enter(agents_enter, t)
                agents_enter += 1
            
            t += 1
    
    def generate_results(self):
        self.time_out = np.array(self.time_out)
        self.time_in = np.array(self.time_in[:self.time_out.shape[0]])
        
        self.results = np.vstack((self.time_in, self.time_out))

        # Calcular tiempo promedio de viaje
        travel_time = self.time_out - self.time_in

        self.results = np.vstack((self.results, travel_time))
        self.avg_travel_time = np.mean(travel_time)

        # Calcular velocidad promedio
        spds = []
        for i in range(len(self.time_out)):
            spd_agent = self.spd[self.id_first_agent_to_consider + i][self.time_in[i]:self.time_out[i]]
            spds.append(np.mean(spd_agent))

        self.results = np.vstack((self.results, np.array(spds)))
        self.avg_travel_speed = np.sum(spds) / len(self.time_out)

        # Calcular aceleración promedio
        accs = []
        for i in range(len(self.time_out)):
            acc_agent = self.acc[self.id_first_agent_to_consider + i][self.time_in[i]:self.time_out[i]]
            accs.append(np.mean(acc_agent))

        self.results = np.vstack((self.results, np.array(accs)))
        self.avg_travel_acc = np.sum(accs) / len(self.time_out)
        
    def get_avg_travel_time(self):
        return self.avg_travel_time

    def get_avg_travel_speed(self):
        return self.avg_travel_speed

    def get_avg_travel_acce(self):
        return self.avg_travel_acc

    def get_collisions(self):
        return len(self.collisions) + len(self.collisions_in_radar)