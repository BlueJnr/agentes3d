# Contenido de agent_robot.py
import random


class AgenteRobot:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x, self.y, self.z = x, y, z
        self.orientation = random.choice(['+X', '-X', '+Y', '-Y', '+Z', '-Z'])
        self.memory = {'history': [], 'known_walls': set()}
        self.rules_used = set()

    def perceive(self, entorno, robots, monstruos):
        # ... (Lógica detallada para simular cada sensor) ...
        percepcion = {
            'giroscopio': self.orientation, 'monstroscopio': False,
            'vacuscopio': False, 'energometro': False, 'roboscanner': False
        }
        return percepcion

    def decide_action(self, percepcion):
        # P0: Energómetro
        if percepcion['energometro']:
            self.rules_used.add(0)
            return 'VACUUMATOR', None
        # P2: Roboscanner
        if percepcion['roboscanner']:
            self.rules_used.add(2)
            return 'REORIENTADOR', '+90'
        # P3: Monstroscopio
        if percepcion['monstroscopio']:
            self.rules_used.add(3)
            return 'PROPULSOR', None
        # P4: Exploración
        self.rules_used.add(4)
        return 'PROPULSOR', None

    def update_memory(self, t, percepcion, accion):
        self.memory['history'].append((t, percepcion, accion))
        # ... (Lógica para actualizar known_walls si vacuscopio se activó) ...
