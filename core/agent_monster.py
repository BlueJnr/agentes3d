# Contenido de agent_monster.py
import random


class AgenteMonstruo:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x, self.y, self.z = x, y, z

    def decide_action(self, entorno):
        direcciones = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        random.shuffle(direcciones)

        for dx, dy, dz in direcciones:
            next_x, next_y, next_z = self.x + dx, self.y + dy, self.z + dz
            if entorno.get_cell_type(next_x, next_y, next_z) == 0:
                return (next_x, next_y, next_z)

        return (self.x, self.y, self.z)
