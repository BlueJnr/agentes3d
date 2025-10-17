# agent_robot.py
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

# Direcciones y rotaciones posibles en el espacio 3D.
_ORIENT_VECT: Dict[str, Tuple[int, int, int]] = {
    '+X': (1, 0, 0), '-X': (-1, 0, 0),
    '+Y': (0, 1, 0), '-Y': (0, -1, 0),
    '+Z': (0, 0, 1), '-Z': (0, 0, -1)
}

_ROTATE_RIGHT: Dict[str, str] = {
    '+X': '+Y', '+Y': '-X', '-X': '-Y', '-Y': '+X',
    '+Z': '+Z', '-Z': '-Z'
}
_ROTATE_LEFT: Dict[str, str] = {v: k for k, v in _ROTATE_RIGHT.items()}

PerceptionKey = Tuple[bool, bool, bool, bool]  # (energometro, roboscanner, monstroscopio, vacuscopio)


class AgenteRobot:
    """
    Agente racional con memoria interna y aprendizaje simbólico por mapeo.

    Implementa cinco sensores (giroscopio, monstroscopio, vacuscopio,
    energómetro y roboscanner) y tres efectores (propulsor, reorientador, vacuumator).
    La decisión se sigue según la jerarquía de prioridades P0–P4 definida en el diseño.
    """

    def __init__(self, id: int, x: int, y: int, z: int, orientation: Optional[str] = None) -> None:
        """
        Inicializa el agente robot.

        Args:
            id: Identificador único del robot.
            x, y, z: Coordenadas iniciales en el entorno (enteros).
            orientation: Orientación inicial ('+X', '-X', '+Y', '-Y', '+Z', '-Z').
                         Si es None se elige aleatoriamente.
        """
        self.id: int = id
        self.x: int = int(x)
        self.y: int = int(y)
        self.z: int = int(z)
        self.orientation: str = (
            orientation if orientation in _ORIENT_VECT else random.choice(list(_ORIENT_VECT.keys()))
        )

        # Memoria interna: historial, conocimiento de paredes y últimas posiciones de monstruos
        self.memory: Dict[str, Any] = {
            'history': [],  # list[tuple[int, dict, str]]  (tick, percepcion, accion)
            'known_walls': set(),  # set[tuple[int,int,int]]
            'last_seen_monsters': {}  # dict[monster_id, (x,y,z,tick)]
        }

        # Tabla de mapeo percepción -> acción (aprendizaje simbólico simple)
        self.mapping_table: Dict[PerceptionKey, str] = defaultdict(lambda: 'PROPULSOR')
        # Inicializaciones heurísticas según el documento
        self.mapping_table[(True, False, False, False)] = 'VACUUMATOR'
        self.mapping_table[(False, True, False, False)] = 'REORIENTADOR'
        self.mapping_table[(False, False, True, False)] = 'PROPULSOR'

        # Conjunto para depuración/estadísticas de reglas usadas
        self.rules_used: Set[int] = set()

    # -------------------------------------------------------------------------
    # SENSORES / PERCEPCIÓN
    # -------------------------------------------------------------------------
    def perceive(self, entorno: Any, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """
        Obtener la percepción actual a partir de los cinco sensores.

        Args:
            entorno: Instancia de Entorno3D (debe exponer get_cell_type(x,y,z)).
            robots: Lista de robots presentes en el entorno.
            monstruos: Lista de monstruos presentes en el entorno.

        Returns:
            dict: Diccionario con claves:
                - 'giroscopio' (str): orientación actual.
                - 'monstroscopio' (bool): monstruo en celdas adyacentes (excepto posterior).
                - 'vacuscopio' (bool): hay zona vacía/pared en la celda frontal.
                - 'energometro' (bool): monstruo en la misma celda.
                - 'roboscanner' (bool): robot en la celda frontal.
                - 'front_cell' (tuple): coordenadas de la celda frontal.
        """
        giroscopio: str = self.orientation
        dx, dy, dz = _ORIENT_VECT[self.orientation]
        front = (self.x + dx, self.y + dy, self.z + dz)

        # Energómetro: monster in same cell
        energometro: bool = any((m.x, m.y, m.z) == (self.x, self.y, self.z) for m in monstruos)

        # Roboscanner: another robot in front cell
        roboscanner: bool = any((r.x, r.y, r.z) == front and r.id != self.id for r in robots)

        # Vacuscopio: check cell type in front (treat out-of-bounds as vacía)
        cell_front_type = entorno.get_cell_type(*front)
        vacuscopio: bool = (cell_front_type == 1)

        # Monstroscopio: check neighbor cells except the cell behind
        behind = (-dx, -dy, -dz)
        neighbor_dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0),
                         (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        # Excluir la dirección posterior
        neighbor_dirs = [d for d in neighbor_dirs if d != behind]

        monstroscopio = any(
            any((m.x, m.y, m.z) == (self.x + ddx, self.y + ddy, self.z + ddz) for m in monstruos)
            for ddx, ddy, ddz in neighbor_dirs
        )

        return {
            'giroscopio': giroscopio,
            'monstroscopio': monstroscopio,
            'vacuscopio': vacuscopio,
            'energometro': energometro,
            'roboscanner': roboscanner,
            'front_cell': front
        }

    # -------------------------------------------------------------------------
    # DECISIÓN
    # -------------------------------------------------------------------------
    def decide_action(self, percepcion: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """
        Determinar la acción a ejecutar según la jerarquía de prioridades P0–P4.

        Retorna:
            (accion, parametro) donde 'accion' es una de:
              - 'VACUUMATOR', 'REORIENTADOR', 'PROPULSOR', ...
            y 'parametro' es información adicional (por ejemplo '+90' para giro).
        """
        # P0: Energómetro → Vacuumator (máxima prioridad)
        if percepcion['energometro']:
            self.rules_used.add(0)
            return 'VACUUMATOR', None

        # P1: Vacío/pared adelante o memoria indica pared → Reorientador
        if percepcion['vacuscopio'] or percepcion['front_cell'] in self.memory['known_walls']:
            self.rules_used.add(1)
            return 'REORIENTADOR', '+90'

        # P2: Otro robot en la celda frontal → Reorientador (cooperación simplificada)
        if percepcion['roboscanner']:
            self.rules_used.add(2)
            return 'REORIENTADOR', '+90'

        # P3: Monstruo en vecindad → Propulsor
        if percepcion['monstroscopio']:
            self.rules_used.add(3)
            return 'PROPULSOR', None

        # P4: Exploración/Política aprendida (mapping_table)
        key: PerceptionKey = (
            bool(percepcion['energometro']),
            bool(percepcion['roboscanner']),
            bool(percepcion['monstroscopio']),
            bool(percepcion['vacuscopio'])
        )
        accion = self.mapping_table[key]
        self.rules_used.add(4)
        return accion, None

    # -------------------------------------------------------------------------
    # EFECTORES
    # -------------------------------------------------------------------------
    def _propulsor(self, entorno: Any) -> Dict[str, Any]:
        """
        Moverse una celda en la orientación actual si la celda destino es transitable.

        Devuelve un dict con el resultado del intento de movimiento.
        """
        dx, dy, dz = _ORIENT_VECT[self.orientation]
        nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
        cell_type = entorno.get_cell_type(nx, ny, nz)

        if cell_type == 0:
            # Movimiento exitoso
            self.x, self.y, self.z = nx, ny, nz
            return {'moved': True}
        # Colisión: registrar pared conocida
        self.memory['known_walls'].add((nx, ny, nz))
        return {'moved': False, 'collision': True}

    def _reorientador(self, direction: str = '+90') -> Dict[str, Any]:
        """
        Reorientar el agente ±90 grados en el plano XY (rotación simplificada).

        Args:
            direction: '+90' (derecha) o '-90' (izquierda).
        """
        if direction == '+90':
            self.orientation = _ROTATE_RIGHT.get(self.orientation, self.orientation)
        else:
            self.orientation = _ROTATE_LEFT.get(self.orientation, self.orientation)
        return {'rotated': True, 'new_orientation': self.orientation}

    def _vacuumator(self, entorno: Any, monstruos: List[Any]) -> Dict[str, Any]:
        """
        Efectuar la acción terminal: destruir monstruos en la misma celda y marcar la celda como vacía.

        Nota: el simulador es responsable de eliminar los objetos monstruo de la lista.
        """
        killed = [m for m in monstruos if (m.x, m.y, m.z) == (self.x, self.y, self.z)]
        # Marcar celda como vacía (obstáculo permanente)
        entorno.grid[self.x, self.y, self.z] = 1
        return {'killed_monsters': killed, 'robot_destroyed': True, 'cell': (self.x, self.y, self.z)}

    # -------------------------------------------------------------------------
    # INTERFAZ: ciclo percepción→decisión→acción
    # -------------------------------------------------------------------------
    def decide_and_act(self, t: int, entorno: Any, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """
        Ejecuta un ciclo completo: percibir, decidir y actuar.

        Args:
            t: Tick actual de simulación.
            entorno: Entorno3D.
            robots: Lista de robots.
            monstruos: Lista de monstruos.

        Returns:
            dict: Evento con la acción ejecutada y metadatos (id, tick, resultado).
        """
        percepcion = self.perceive(entorno, robots, monstruos)
        accion, param = self.decide_action(percepcion)
        self.update_memory(t, percepcion, accion)

        event: Dict[str, Any] = {'agent_id': self.id, 't': t, 'action': accion}

        if accion == 'PROPULSOR':
            event.update(self._propulsor(entorno))
        elif accion == 'REORIENTADOR':
            event.update(self._reorientador(param if param is not None else '+90'))
        elif accion == 'VACUUMATOR':
            event.update(self._vacuumator(entorno, monstruos))

        return event

    # -------------------------------------------------------------------------
    # MEMORIA Y APRENDIZAJE
    # -------------------------------------------------------------------------
    def update_memory(self, t: int, percepcion: Dict[str, Any], accion: str) -> None:
        """
        Registrar percepción y acción en la memoria histórica y actualizar conocimiento local.

        Args:
            t: Tick actual.
            percepcion: Diccionario de percepción.
            accion: Acción ejecutada.
        """
        # Append shallow copy of perception to history
        self.memory['history'].append((t, dict(percepcion), accion))
        if percepcion.get('vacuscopio'):
            self.memory['known_walls'].add(percepcion.get('front_cell'))

    def learn_from_event(self, event: Dict[str, Any], reward: float = 0.0) -> None:
        """
        Refuerzo simbólico: asociar la última percepción con la acción si reward > 0.

        Args:
            event: Evento producido por la acción (informal, para trazabilidad).
            reward: Recompensa (valor >0 refuerza la acción tomada).
        """
        if reward <= 0 or not self.memory['history']:
            return
        _, p, a = self.memory['history'][-1]
        key: PerceptionKey = (bool(p['energometro']), bool(p['roboscanner']),
                              bool(p['monstroscopio']), bool(p['vacuscopio']))
        self.mapping_table[key] = a

    def __repr__(self) -> str:
        """Representación concisa del agente para depuración."""
        return f"<AgenteRobot id={self.id} pos=({self.x},{self.y},{self.z}) ori={self.orientation}>"
