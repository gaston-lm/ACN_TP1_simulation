class Agent:
    def __init__(self, id, pos, speed, acceleration):
        self.pos = pos
        self.spd = spd
        self.acc = acc
        self.id = id

    def update_acc(self, neighbour, max_spd):
        dist = neighbour.pos - self.pos
        relation_time_dist = dist / self.spd
        
        new_acc = self.acc

        if relation_time_dist > 2:
            new_acc += 0 # ver magnitud
        elif relation_time_dist < 2:
            new_acc -= (self.acc + 0) # ver magnitud --> cierta f(max_speed, neighbout.acc)

        # si veo las luces rojas del adelante está frenando, lo podríamos ver con su acc negativa?        

        if self.spd + new_acc <= max_spd:
            self.acc = new_acc # + random error * Indicadora (se distrajo o no) --> poisson?

    def update_pos(self):
        self.pos = self.pos + self.spd # * time 

    def update_spd(self):
        self.spd = self.spd + self.acc # * time 

    def update(self):
        self.update_spd()
        self.update_pos()
        # De Liniers a Acceso Norte es 80km/h
        max_spd:float = 22.22 # 80 km/h en m/s
        if self.pos > 10000:
            max_spd = 27.77 # 100 km/h
        self.update_acc(neighbour, max_spd)