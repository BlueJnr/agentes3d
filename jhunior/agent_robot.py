# agent_robot.py
import random
from collections import defaultdict

# Orientations and their forward vector
_ORIENT_VECT = {
    '+X': (1, 0, 0), '-X': (-1, 0, 0),
    '+Y': (0, 1, 0), '-Y': (0, -1, 0),
    '+Z': (0, 0, 1), '-Z': (0, 0, -1),
}

# Utility to rotate orientation +/-90 degrees in the 3D grid.
# We'll define a simple rotation set: rotate around Z for X/Y, around Y for X/Z, etc.
# For simplicity use a deterministic small rotation table (90° right/left).
_ROTATE_RIGHT = {
    '+X': '+Y', '+Y': '-X', '-X': '-Y', '-Y': '+X',
    '+Z': '+Z', '-Z': '-Z'   # rotating around Z keeps +Z/-Z
}
_ROTATE_LEFT = {v: k for k, v in _ROTATE_RIGHT.items()}


class AgenteRobot:
    """
    Agente Robot con memoria interna, 5 sensores y 3 efectores.
    Implementa:
      - perceive(entorno, robots, monstruos)
      - decide_action(percepcion)
      - act(action, entorno, robots, monstruos, t)
      - update_memory(t, percepcion, accion)
    """

    def __init__(self, id, x, y, z, orientation=None):
        self.id = id
        self.x, self.y, self.z = int(x), int(y), int(z)
        self.orientation = orientation if orientation in _ORIENT_VECT else random.choice(list(_ORIENT_VECT.keys()))
        # Memoria interna
        self.memory = {
            'history': [],              # list of (t, perception, action)
            'known_walls': set(),       # set of (x,y,z) detected by vacuscopio
            'last_seen_monsters': {},   # monster_id -> (x,y,z,t)
        }
        # Tabla de mapeo percepción -> acción (simple, puede actualizarse)
        # keys: tuple(perception flags) -> action
        # we'll keep a default policy but allow learning updates
        self.mapping_table = defaultdict(lambda: 'PROPULSOR')  # default explore
        # initialize some mapping heuristics
        # (energometro, roboscanner, monstroscopio, vacuscopio_front) -> action
        self.mapping_table[(True, False, False, False)] = 'VACUUMATOR'
        self.mapping_table[(False, True, False, False)] = 'REORIENTADOR'
        self.mapping_table[(False, False, True, False)] = 'PROPULSOR'
        self.rules_used = set()

    # -----------------------
    # SENSORES / PERCEPCIONES
    # -----------------------
    def perceive(self, entorno, robots, monstruos):
        """
        Genera la percepción simulando los 5 sensores descritos:
         - giroscopio: orientation
         - monstroscopio: boolean (hay monstruo en las 5 celdas adyacentes excluyendo la posterior)
         - vacuscopio: boolean (se activará si intentamos mover al frente y hay zona vacía) --> here we provide frontal-check
         - energometro: boolean (monstruo en la misma celda)
         - roboscanner: boolean (otro robot en la celda frontal)
        """
        giroscopio = self.orientation

        # Forward vector
        dx, dy, dz = _ORIENT_VECT[self.orientation]
        front = (self.x + dx, self.y + dy, self.z + dz)

        # Energómetro: check same cell for any monster
        energometro = any((m.x, m.y, m.z) == (self.x, self.y, self.z) for m in monstruos)

        # Roboscanner: is there another robot in the front cell?
        roboscanner = any((r.x, r.y, r.z) == front and r.id != self.id for r in robots)

        # Vacuscopio frontal check (does front cell exist and is free?)
        cell_front_type = entorno.get_cell_type(*front)
        vacuscopio = (cell_front_type == 1)  # True if it's a Zona Vacía or outside bounds

        # Monstroscopio: check the 5 adjacent cells excluding the posterior
        # We'll generate adjacent directions except the one exactly behind.
        behind_dx, behind_dy, behind_dz = tuple(-v for v in (dx, dy, dz))
        adj_dirs = [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
        # exclude behind
        check_dirs = [d for d in adj_dirs if d != (behind_dx, behind_dy, behind_dz)]
        monstroscopio = False
        for ddx, ddy, ddz in check_dirs:
            nx, ny, nz = self.x + ddx, self.y + ddy, self.z + ddz
            # if any monster occupies any of these cells, monstroscopio triggers
            if any((m.x, m.y, m.z) == (nx, ny, nz) for m in monstruos):
                monstroscopio = True
                break

        percepcion = {
            'giroscopio': giroscopio,
            'monstroscopio': monstroscopio,
            'vacuscopio': vacuscopio,
            'energometro': energometro,
            'roboscanner': roboscanner,
            'front_cell': front
        }
        return percepcion

    # -----------------------
    # DECISION (jerarquía)
    # -----------------------
    def decide_action(self, percepcion):
        """
        Implementa la jerarquía:
          P0 Energómetro -> VACUUMATOR (máxima prioridad)
          P1 Si memoria indica pared en front -> REORIENTADOR
          P2 Roboscanner -> REORIENTADOR (cooperación simplificada)
          P3 Monstroscopio -> PROPULSOR (caza informada)
          P4 Explorar -> PROPULSOR
        """
        # P0
        if percepcion['energometro']:
            self.rules_used.add(0)
            return ('VACUUMATOR', None)

        # P1: check memory-known walls for front cell
        front = percepcion['front_cell']
        if front in self.memory['known_walls'] or percepcion['vacuscopio']:
            self.rules_used.add(1)
            # decide turn direction heuristically: prefer right
            return ('REORIENTADOR', '+90')

        # P2
        if percepcion['roboscanner']:
            self.rules_used.add(2)
            return ('REORIENTADOR', '+90')

        # P3
        if percepcion['monstroscopio']:
            self.rules_used.add(3)
            # try to move forward (propulsor) hoping to find monster
            return ('PROPULSOR', None)

        # P4 default exploration - consult mapping table (simple learning)
        # Create perception key for mapping: (energ, robor,monstr, vac_front)
        key = (percepcion['energometro'], percepcion['roboscanner'],
               percepcion['monstroscopio'], percepcion['vacuscopio'])
        mapped = self.mapping_table.get(key, 'PROPULSOR')
        self.rules_used.add(4)
        return (mapped, None)

    # -----------------------
    # EFECTORES / ACCIONES
    # -----------------------
    def _propulsor(self, entorno, robots, monstruos):
        """Avanza una celda en la orientación actual si es posible. Devuelve resultado y event."""
        dx, dy, dz = _ORIENT_VECT[self.orientation]
        nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
        cell_type = entorno.get_cell_type(nx, ny, nz)
        if cell_type == 0:
            # Move
            self.x, self.y, self.z = nx, ny, nz
            return {'moved': True, 'collision': False}
        else:
            # collision with wall (Vacuscopio triggers)
            self.memory['known_walls'].add((nx, ny, nz))
            return {'moved': False, 'collision': True, 'wall_coord': (nx, ny, nz)}

    def _reorientador(self, direction='+90'):
        """Rotate +/-90 degrees (we implement +90 as right, -90 as left)."""
        if direction == '+90':
            self.orientation = _ROTATE_RIGHT.get(self.orientation, self.orientation)
        else:
            self.orientation = _ROTATE_LEFT.get(self.orientation, self.orientation)
        return {'rotated': True, 'new_orientation': self.orientation}

    def _vacuumator(self, entorno, monstruos):
        """
        Destroys a monster on the same cell and turns the cell into a Zona Vacía.
        Following spec, vacuumator also destroys the robot itself (we'll mark robot as 'dead').
        We will return a dict describing result; caller (simulator) must remove robot and set env cell=1.
        """
        # find any monster in same cell
        killed = []
        for m in list(monstruos):
            if (m.x, m.y, m.z) == (self.x, self.y, self.z):
                killed.append(m)
        # vacuumator effect: environment cell becomes empty (1)
        entorno.grid[self.x, self.y, self.z] = 1
        # robot is destroyed; the simulator should remove it
        return {'killed_monsters': killed, 'robot_destroyed': True, 'cell': (self.x, self.y, self.z)}

    # -----------------------
    # INTERFAZ: decidir y actuar
    # -----------------------
    def decide_and_act(self, t, entorno, robots, monstruos):
        percepcion = self.perceive(entorno, robots, monstruos)
        accion, param = self.decide_action(percepcion)

        # update memory with current perception and tentative action
        self.update_memory(t, percepcion, accion)

        # execute the action and return an event describing what happened
        event = {'agent_id': self.id, 't': t, 'action': accion, 'param': param}

        if accion == 'PROPULSOR':
            res = self._propulsor(entorno, robots, monstruos)
            event.update(res)
        elif accion == 'REORIENTADOR':
            res = self._reorientador(direction=param if param else '+90')
            event.update(res)
        elif accion == 'VACUUMATOR':
            res = self._vacuumator(entorno, monstruos)
            event.update({'killed_count': len(res['killed_monsters'])})
            # caller/simulator must remove monsters in res['killed_monsters'] and the robot itself if destroyed
            event.update(res)
        else:
            event.update({'noop': True})

        return event

    # -----------------------
    # MEMORIA / APRENDIZAJE
    # -----------------------
    def update_memory(self, t, percepcion, accion):
        # Append history
        self.memory['history'].append((t, percepcion.copy(), accion))
        # If vacuscopio/collision front -> record wall (already done in _propulsor), but double-check:
        if percepcion.get('vacuscopio'):
            front = percepcion.get('front_cell')
            if front:
                self.memory['known_walls'].add(front)

    def learn_from_event(self, event, reward=0.0):
        """
        Simple symbolic learning: update mapping_table based on reward.
        If action produced positive reward, increase chance to repeat action for that perception.
        We'll keep it simple: map exact perception key -> action if reward > 0
        """
        percep = event.get('percepcion_key')
        if percep is None:
            # Try to derive a key from last history element
            if self.memory['history']:
                _, p, a = self.memory['history'][-1]
                key = (p['energometro'], p['roboscanner'], p['monstroscopio'], p['vacuscopio'])
            else:
                return
        else:
            key = percep

        if reward > 0:
            # reinforce
            self.mapping_table[key] = event.get('action', self.mapping_table[key])

    # Nice repr
    def __repr__(self):
        return f"<AgenteRobot id={self.id} pos=({self.x},{self.y},{self.z}) ori={self.orientation}>"
