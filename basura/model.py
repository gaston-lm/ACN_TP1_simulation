from agent import *
from lane import *

# Establezco cuantos paths voy a simular
paths_n:int = 10000

# Limite de tiempo de cada path (medido en segundos) y la cantidad de agentes que hay en cada path.
time_limit:int = 10000 
agents_n:int = 20

# Armo una variable donde almacenar los paths.
paths:List[Lane_simulation] = []

# Hago las paths_n simulaciones y las guardo en paths, con los parametros de time_limit y agents_n inicializados anteriormente.
for _ in range(paths_n):
    lane = Lane_simulation(time_limit, agents_n)
    lane.simulation()
    paths.append(lane)


test = np.array(([[-1]*agents_n])*time_limit)
print(test)