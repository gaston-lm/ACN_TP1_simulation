import numpy as np
import copy

class Agent:
    def __init__(self, id, position, speed, acceleration):
        self.pos = position
        self.spd = speed
        self.acc = acceleration
        self.id = id

    def update_first(self):
        # agregar condicion si le importa la max_speed
        prev_spd = copy.deepcopy(self.spd)
        prev_pos = copy.deepcopy(self.pos)
        prev_acc = copy.deepcopy(self.acc)

        # De Liniers a Acceso Norte es 80km/h
        max_spd:float = 22.22 # 80 km/h en m/s
        if prev_pos > 10000:
            max_spd = 27.77 # 100 km/h

        self.pos = prev_pos + prev_spd * 1 + 0.5 * prev_acc * 1**2 # 1s frac de tiempo

        self.spd = prev_spd + prev_acc * 1 # 1s frac de tiempo

        new_acc = 3.5 # acelero según aceleración según autos promedio

        if self.spd + new_acc < max_spd:
            self.acc = new_acc # + random error * Indicadora (se distrajo o no) --> poisson?
        else:
            self.acc = max_spd - self.spd

    def update(self, self_prev_pos, self_prev_spd, self_prev_acc, neigbour_prev_pos, neigbour_prev_spd, alpha, l, m):
        prev_spd = self_prev_spd
        prev_pos = self_prev_pos
        prev_acc = self_prev_acc

        sensitivity_coeff = (neigbour_prev_pos - prev_pos) / prev_spd
        t = np.random.exponential(scale=100, size=1).item()

        # De Liniers a Acceso Norte es 80km/h
        max_spd:float = 22.22 # 80 km/h en m/s
        if prev_pos > 10000:
            max_spd = 27.77 # 100 km/h

        # update pos
        self.pos = prev_pos + prev_spd * 1 + 0.5 * prev_acc * 1**2 # 1s frac de tiempo

        # update spd
        self.spd = prev_spd + prev_acc * 1 # 1s frac de tiempo

        print(neigbour_prev_pos, prev_pos)
        # if abs(neigbour_prev_pos - prev_pos) < 0.01:
            

        # update acc
        # new_acc = 0
        # if sensitivity_coeff > t:
        #     new_acc = 3.5 # acelero según aceleración según autos promedio
        # elif sensitivity_coeff < t:
        #     # formula "segura"
        new_acc = ((alpha * prev_spd**m) / (neigbour_prev_pos - prev_pos)**l) * (neigbour_prev_spd - prev_spd)

        # no es real que pueda acelerar en 1s en más de 3.5 m/s
        if new_acc > 3.5:
            new_acc = 3.5

        if self.spd + new_acc <= max_spd:
            self.acc = new_acc # + random error * Indicadora (se distrajo o no) --> poisson?
        else:
            self.acc = max_spd - self.spd

        # si veo las luces rojas del adelante está frenando, lo podríamos ver con su acc negativa?