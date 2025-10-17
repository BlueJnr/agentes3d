# Contenido de environment.py
import random

import numpy as np


class Entorno3D:
    """
    Gestiona la malla 3D, su generación aleatoria y el estado de las celdas.
    """

    def __init__(self, N=5, Pfree=0.8, seed=None):
        self.N = N
        # 0: Zona Libre, 1: Zona Vacía
        self.grid = np.zeros((N, N, N), dtype=int)
        self.seed = seed
        self._generate_environment(Pfree)

    def _generate_environment(self, Pfree):
        if self.seed is not None:
            random.seed(self.seed)

        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    if random.random() > Pfree:
                        self.grid[x, y, z] = 1  # Zona Vacía

    def get_cell_type(self, x, y, z):
        if not (0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N):
            return 1  # Borde es Zona Vacía
        return self.grid[x, y, z]

    def get_random_free_cell(self):
        free_cells = np.argwhere(self.grid == 0)
        if len(free_cells) > 0:
            return tuple(random.choice(free_cells))
        return None
