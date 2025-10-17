# Contenido de simulation.py
import pandas as pd

from agent_monster import AgenteMonstruo
from agent_robot import AgenteRobot
from environment import Entorno3D


class Simulation:
    def __init__(self, N, Pfree, Nrobot, Nmonstruos, K, seed):
        self.entorno = Entorno3D(N, Pfree, seed)
        self.K = K
        self.log = []
        self.robots = [AgenteRobot(i, *self.entorno.get_random_free_cell()) for i in range(Nrobot)]
        self.monstruos = [AgenteMonstruo(i, *self.entorno.get_random_free_cell()) for i in range(Nmonstruos)]

    def run(self, max_steps=100):
        for t in range(max_steps):
            # Turno de los Robots
            for robot in self.robots:
                # ... (Ciclo percepción-acción-memoria) ...
                self.log.append(...)

            # Turno de los Monstruos
            if t % self.K == 0:
                for monstruo in self.monstruos:
                    # ... (Lógica de movimiento aleatorio) ...
                    self.log.append(...)

        df = pd.DataFrame(self.log)
        df.to_csv("simulation_log.csv")
