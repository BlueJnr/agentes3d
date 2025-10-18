# agent_robot.py
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

# Direcciones y rotaciones posibles en el espacio energético 3D
_DIRECCIONES: Dict[str, Tuple[int, int, int]] = {
    '+X': (1, 0, 0), '-X': (-1, 0, 0),
    '+Y': (0, 1, 0), '-Y': (0, -1, 0),
    '+Z': (0, 0, 1), '-Z': (0, 0, -1)
}

_ROTAR_DERECHA: Dict[str, str] = {
    '+X': '+Y', '+Y': '-X', '-X': '-Y', '-Y': '+X',
    '+Z': '+Z', '-Z': '-Z'
}
_ROTAR_IZQUIERDA: Dict[str, str] = {v: k for k, v in _ROTAR_DERECHA.items()}

PercepcionClave = Tuple[bool, bool, bool, bool]  # (energómetro, roboscanner, monstroscopio, vacuscopio)


class AgenteRacionalRobot:
    """
    Representa un agente racional dentro del Entorno de Operación Energético.

    Este agente:
      - Posee memoria interna y capacidad de aprendizaje simbólico por mapeo.
      - Utiliza cinco sensores:
            1. Giroscopio      → orientación actual.
            2. Monstroscopio   → detección de monstruos cercanos.
            3. Vacuscopio      → detección de zonas vacías.
            4. Energómetro     → detección de monstruos en la misma celda.
            5. Roboscanner     → detección de otros robots.
      - Ejecuta tres efectores:
            - Propulsor      → desplazamiento.
            - Reorientador   → cambio de orientación.
            - Vacuumator     → neutralización de monstruos.
    """

    def __init__(self, id: int, x: int, y: int, z: int, orientacion: Optional[str] = None) -> None:
        """
        Inicializa el agente racional tipo Robot.

        Args:
            id: Identificador único.
            x, y, z: Coordenadas iniciales en el entorno energético.
            orientacion: Dirección inicial ('+X', '-X', '+Y', '-Y', '+Z', '-Z').
                         Si no se especifica, se elige aleatoriamente.
        """
        self.id: int = id
        self.x: int = int(x)
        self.y: int = int(y)
        self.z: int = int(z)
        self.orientacion: str = (
            orientacion if orientacion in _DIRECCIONES else random.choice(list(_DIRECCIONES.keys()))
        )

        # Memoria interna: historial y conocimiento del entorno
        self.memoria: Dict[str, Any] = {
            'historial': [],               # [(tick, percepcion, accion)]
            'paredes_conocidas': set(),    # {(x, y, z)}
            'monstruos_recientes': {}      # {monster_id: (x, y, z, tick)}
        }

        # Tabla de mapeo (aprendizaje simbólico)
        self.tabla_mapeo: Dict[PercepcionClave, str] = defaultdict(lambda: 'PROPULSOR')
        self.tabla_mapeo[(True, False, False, False)] = 'VACUUMATOR'
        self.tabla_mapeo[(False, True, False, False)] = 'REORIENTADOR'
        self.tabla_mapeo[(False, False, True, False)] = 'PROPULSOR'

        self.reglas_usadas: Set[int] = set()

    # -------------------------------------------------------------------------
    # SENSORES
    # -------------------------------------------------------------------------
    def percibir(self, entorno: Any, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """
        Percibe el entorno inmediato usando los cinco sensores energéticos.
        """
        giroscopio = self.orientacion
        dx, dy, dz = _DIRECCIONES[self.orientacion]
        frente = (self.x + dx, self.y + dy, self.z + dz)

        energometro = any((m.x, m.y, m.z) == (self.x, self.y, self.z) for m in monstruos)
        roboscanner = any((r.x, r.y, r.z) == frente and r.id != self.id for r in robots)
        tipo_frente = entorno.obtener_tipo_celda(*frente)
        vacuscopio = tipo_frente == entorno.ZONA_VACIA

        # Monstroscopio: detecta monstruos en celdas adyacentes (excepto detrás)
        atras = (-dx, -dy, -dz)
        direcciones_vecinas = [(1, 0, 0), (-1, 0, 0),
                               (0, 1, 0), (0, -1, 0),
                               (0, 0, 1), (0, 0, -1)]
        direcciones_vecinas = [d for d in direcciones_vecinas if d != atras]
        monstroscopio = any(
            any((m.x, m.y, m.z) == (self.x + ddx, self.y + ddy, self.z + ddz) for m in monstruos)
            for ddx, ddy, ddz in direcciones_vecinas
        )

        return {
            'giroscopio': giroscopio,
            'monstroscopio': monstroscopio,
            'vacuscopio': vacuscopio,
            'energometro': energometro,
            'roboscanner': roboscanner,
            'celda_frontal': frente
        }

    # -------------------------------------------------------------------------
    # DECISIÓN
    # -------------------------------------------------------------------------
    def decidir_accion(self, percepcion: Dict[str, Any]) -> Tuple[str, Optional[str]]:
        """Aplica la jerarquía de prioridades P0–P4 para decidir la acción."""
        if percepcion['energometro']:
            self.reglas_usadas.add(0)
            return 'VACUUMATOR', None
        if percepcion['vacuscopio'] or percepcion['celda_frontal'] in self.memoria['paredes_conocidas']:
            self.reglas_usadas.add(1)
            return 'REORIENTADOR', '+90'
        if percepcion['roboscanner']:
            self.reglas_usadas.add(2)
            return 'REORIENTADOR', '+90'
        if percepcion['monstroscopio']:
            self.reglas_usadas.add(3)
            return 'PROPULSOR', None

        clave: PercepcionClave = (
            percepcion['energometro'],
            percepcion['roboscanner'],
            percepcion['monstroscopio'],
            percepcion['vacuscopio']
        )
        accion = self.tabla_mapeo[clave]
        self.reglas_usadas.add(4)
        return accion, None

    # -------------------------------------------------------------------------
    # EFECTORES
    # -------------------------------------------------------------------------
    def _propulsor(self, entorno: Any) -> Dict[str, Any]:
        """Avanza una celda si la Zona está libre."""
        dx, dy, dz = _DIRECCIONES[self.orientacion]
        nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
        tipo = entorno.obtener_tipo_celda(nx, ny, nz)

        if tipo == entorno.ZONA_LIBRE:
            self.x, self.y, self.z = nx, ny, nz
            return {'mover': True}
        self.memoria['paredes_conocidas'].add((nx, ny, nz))
        return {'mover': False, 'colision': True}

    def _reorientador(self, direccion: str = '+90') -> Dict[str, Any]:
        """Gira la orientación del robot ±90° en el plano XY."""
        if direccion == '+90':
            self.orientacion = _ROTAR_DERECHA.get(self.orientacion, self.orientacion)
        else:
            self.orientacion = _ROTAR_IZQUIERDA.get(self.orientacion, self.orientacion)
        return {'rotado': True, 'nueva_orientacion': self.orientacion}

    def _vacuumator(self, entorno: Any, monstruos: List[Any]) -> Dict[str, Any]:
        """Destruye monstruos en la misma celda y marca la zona como vacía."""
        eliminados = [m for m in monstruos if (m.x, m.y, m.z) == (self.x, self.y, self.z)]
        entorno.grid[self.x, self.y, self.z] = entorno.ZONA_VACIA
        return {'monstruos_eliminados': eliminados, 'celda': (self.x, self.y, self.z)}

    # -------------------------------------------------------------------------
    # CICLO DE VIDA
    # -------------------------------------------------------------------------
    def percibir_decidir_actuar(self, t: int, entorno: Any, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """Ejecuta un ciclo completo de percepción → decisión → acción."""
        percepcion = self.percibir(entorno, robots, monstruos)
        accion, param = self.decidir_accion(percepcion)
        self.actualizar_memoria(t, percepcion, accion)

        evento = {'agent_id': self.id, 'tick': t, 'accion': accion}

        if accion == 'PROPULSOR':
            evento.update(self._propulsor(entorno))
        elif accion == 'REORIENTADOR':
            evento.update(self._reorientador(param or '+90'))
        elif accion == 'VACUUMATOR':
            evento.update(self._vacuumator(entorno, monstruos))

        return evento

    # -------------------------------------------------------------------------
    # MEMORIA Y APRENDIZAJE
    # -------------------------------------------------------------------------
    def actualizar_memoria(self, t: int, percepcion: Dict[str, Any], accion: str) -> None:
        """Registra percepciones y acciones para reforzar conocimiento local."""
        self.memoria['historial'].append((t, dict(percepcion), accion))
        if percepcion.get('vacuscopio'):
            self.memoria['paredes_conocidas'].add(percepcion.get('celda_frontal'))

    def aprender_de_evento(self, evento: Dict[str, Any], recompensa: float = 0.0) -> None:
        """Aprendizaje simbólico: refuerza la última acción si la recompensa es positiva."""
        if recompensa <= 0 or not self.memoria['historial']:
            return
        _, p, a = self.memoria['historial'][-1]
        clave: PercepcionClave = (p['energometro'], p['roboscanner'], p['monstroscopio'], p['vacuscopio'])
        self.tabla_mapeo[clave] = a

    def __repr__(self) -> str:
        """Representación legible del agente racional para depuración."""
        return f"<AgenteRacionalRobot id={self.id} pos=({self.x},{self.y},{self.z}) ori={self.orientacion}>"
