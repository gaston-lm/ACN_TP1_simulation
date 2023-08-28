class Agent:
    def __init__(self, pos, speed, acceleration):
        self.pos = pos
        self.spd = spd
        self.acc = acc

    def update_acc(self, neighbour, max_spd):
        dist = neighbour.pos - self.pos
        relation_time_dist = dist / self.spd
        
        new_acc = self.acc

        if relation_time_dist > 2:
            new_acc += 0 # ver magnitud
        elif relation_time_dist < 2:
            new_acc -= 0 # ver magnitud

        if self.spd + new_acc <= max_spd:
            self.acc = new_acc

    def update_pos(self):
        self.pos = self.pos + self.spd # * time 

    def update_spd(self):
        self.spd = self.spd + self.acc # * time 

    def update(self):
        self.update_spd()
        self.update_pos()
        self.update_acc(neighbour, max_spd)