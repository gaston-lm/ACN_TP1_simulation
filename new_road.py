import math
import numpy as np

# Intelligent Driver Model:
# x_t = x_t-1 + s_t-1 * delta_t
# s_t = s_t-1 + a_t-1 * delta_t
# a_t = acceleration * (1 - (v_t / desired_velocity) ** delta - (minimum_spacing + v_t * headway + ((v_t * (v_t - v_leader)) / 2 * math.sqrt(acceleration * braking_desaceleration)) / x_leader - x_t - vehicle_length) ** 2

class Agent:
    def __init__(self, desired_velocity, minimum_spacing, headway, acceleration, braking_desacceleration, vehicle_length, delta, initial_t):

        self.d_v = desired_velocity
        self.m_s = minimum_spacing
        self.T = headway
        self.a = acceleration
        self.b = braking_desacceleration
        self.l = vehicle_length
        self.delta = delta

        self.initial_t = initial_t
        self.arrived_t = -1

        self.x_t = 0
        self.v_t = 0
        self.a_t = 0
        
        self.x_t_prev = 0
        self.v_t_prev = 0
        self.a_t_prev = 0

        self.im_leader = False

    def make_leader(self):
        self.is_leader = True
    
    def is_leader(self):
        return self.im_leader
    
    def update_agent(self, leader):
        # Guardo los valores del t antes de actualizar.
        x_t = self.x_t
        self.x_t_prev = x_t
        v_t = self.v_t
        self.s_t_prev = v_t
        a_t = self.a_t
        self.a_t_prev = a_t

        # Actualizo los valores de posición y velocidad.
        self.x_t = x_t + v_t 
        self.v_t = v_t + a_t

        # Actualizo la aceleración.
        if self.is_leader():
            acc = self.a * (1 - (self.v_t / self.d_v) ** self.delta)
        else:
            acc = self.a * (1 - (self.v_t / self.d_v) ** self.delta - (self.m_s + self.v_t * self.T + (((self.v_t * (self.v_t - leader.v_t_prev)) / 2 * math.sqrt(self.a * self.b)) / (leader.x_t_prev - self.x_t - leader.l)) ** 2))

        # Tengo en cuenta los límites físicos de aceleración y des-aceleración.
        if acc < -self.b:
            acc = -self.b
        elif acc > self.a:
            acc = self.a
        
        # Introduzco distracciones.
        indicadora = np.random.uniform(low=0, high=1, size=1)
        lm = 0.0001 # Probabilidad de distracción en cada segundo.

        if indicadora > lm: 
            self.acc = acc # Si no ocurren distracciones, actualizo mi velocidad. Si ocurre una distracción no me di cuenta y mantuve la aceleración como venía.


class NewRoadSim:
    def __init__(self, time_limit, minimum_spacing, acceleration, braking_desacceleration, vehicle_length, delta):
        self.lane = []
        self.arrived = []

        self.time_limit = time_limit
        self.minimum_spacing = minimum_spacing
        self.max_acceleration = acceleration
        self.braking_desacceleration = braking_desacceleration
        self.vehicle_length = vehicle_length
        self.delta = delta

    def enter(self, agent):
        if len(self.lane) == 0:
            agent.make_leader()
        
        self.lane.append(agent)
    
    def simulate(self):
        # Inicializo la lane con un leader:
        d_v = 22.22
        T = 2
        initial_t = 0
        leader = Agent(d_v, self.minimum_spacing, T, self.max_acceleration, self.braking_desacceleration, self.vehicle_length, self.delta, initial_t)
        self.lane.append(leader)

        # Van ingresando los demás autos:
        t = 1
        while t < self.time_limit:
            for i, agent in enumerate(self.lane):
                if agent.is_leader():
                    agent.update_agent(agent)
                    self.lane[i] = agent
                else:
                    agent.update_agent(self.lane[i-1])
                    self.lane[i] = agent

            if t % 2 == 0:
                new_agent = Agent(d_v, self.minimum_spacing, T, self.max_acceleration, self.braking_desacceleration, self.vehicle_length, self.delta, initial_t)
                self.enter(new_agent)

            t += 1