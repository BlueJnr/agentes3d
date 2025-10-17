# agent_monster.py
import random
from typing import Tuple, Optional, List, Dict, Any


class AgenteMonstruo:
    """
    Agente reflejo simple que representa un monstruo dentro del entorno 3D.

    Este agente no posee memoria interna ni capacidad de aprendizaje.
    Su comportamiento es puramente reactivo: se activa de forma periódica
    y, con cierta probabilidad, se desplaza aleatoriamente hacia una celda
    válida adyacente.
    """

    # Direcciones ortogonales posibles en el espacio tridimensional
    _DIRECCIONES: Dict[str, Tuple[int, int, int]] = {
        '+X': (1, 0, 0), '-X': (-1, 0, 0),
        '+Y': (0, 1, 0), '-Y': (0, -1, 0),
        '+Z': (0, 0, 1), '-Z': (0, 0, -1)
    }

    def __init__(self, id: int, x: int, y: int, z: int, p_move: float = 0.7) -> None:
        """
        Inicializa un agente reflejo tipo monstruo.

        Args:
            id: Identificador único del agente.
            x, y, z: Coordenadas iniciales dentro del entorno.
            p_move: Probabilidad de moverse cuando se activa (default = 0.7).
        """
        self.id: int = id
        self.x: int = int(x)
        self.y: int = int(y)
        self.z: int = int(z)
        self.p_move: float = p_move
        self.acciones_realizadas: int = 0

    # -------------------------------------------------------------------------
    # PERCEPCIÓN
    # -------------------------------------------------------------------------
    def perceive(self, entorno: Any) -> Dict[str, Any]:
        """
        Percibe el entorno inmediato, identificando las celdas vecinas válidas.

        Args:
            entorno: Instancia del entorno tridimensional (Entorno3D).

        Returns:
            dict: Percepción mínima con las claves:
                - 'posicion_actual': coordenadas actuales del agente.
                - 'movimientos_validos': lista de desplazamientos posibles.
                - 'puede_moverse': indicador booleano de posibilidad de movimiento.
        """
        movimientos_validos = self._obtener_movimientos_validos(entorno)
        return {
            'posicion_actual': (self.x, self.y, self.z),
            'movimientos_validos': movimientos_validos,
            'puede_moverse': bool(movimientos_validos)
        }

    def _obtener_movimientos_validos(self, entorno: Any) -> List[Tuple[int, int, int]]:
        """
        Determina las direcciones hacia celdas transitables del entorno.

        Args:
            entorno: Instancia del entorno 3D.

        Returns:
            list[tuple[int, int, int]]: Desplazamientos válidos (dx, dy, dz).
        """
        movimientos_validos = []
        for _, (dx, dy, dz) in self._DIRECCIONES.items():
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if self._es_movimiento_valido(entorno, nx, ny, nz):
                movimientos_validos.append((dx, dy, dz))
        return movimientos_validos

    def _es_movimiento_valido(self, entorno: Any, x: int, y: int, z: int) -> bool:
        """
        Verifica si la celda destino está dentro de los límites y es transitable.

        Args:
            entorno: Instancia del entorno 3D.
            x, y, z: Coordenadas destino.

        Returns:
            bool: True si la celda es válida; False en caso contrario.
        """
        if not (0 <= x < entorno.N and 0 <= y < entorno.N and 0 <= z < entorno.N):
            return False
        # Una celda marcada con 1 representa un espacio vacío o bloqueado
        return entorno.grid[x, y, z] != 1

    # -------------------------------------------------------------------------
    # DECISIÓN Y ACCIÓN
    # -------------------------------------------------------------------------
    def decide_action(
            self, entorno: Any, tick_actual: int, K: int
    ) -> Tuple[str, Optional[Tuple[int, int, int]]]:
        """
        Decide la acción a ejecutar según una política reflejo.

        Reglas:
            - Se activa solo cada K ticks.
            - Si se activa, se mueve con probabilidad p_move.
            - Si no hay movimientos válidos, permanece inactivo.

        Args:
            entorno: Instancia del entorno 3D.
            tick_actual: Tick actual de simulación.
            K: Frecuencia de activación.

        Returns:
            tuple: ('move' o 'idle', nueva posición si aplica).
        """
        # Frecuencia de activación
        if tick_actual % K != 0:
            return 'idle', None

        # Probabilidad de movimiento
        if random.random() > self.p_move:
            return 'idle', None

        # Determinar movimientos posibles
        movimientos_validos = self._obtener_movimientos_validos(entorno)
        if not movimientos_validos:
            return 'idle', None

        # Movimiento aleatorio
        dx, dy, dz = random.choice(movimientos_validos)
        nueva_pos = (self.x + dx, self.y + dy, self.z + dz)
        self.acciones_realizadas += 1
        return 'move', nueva_pos

    def ejecutar_accion(self, accion: str, nueva_posicion: Optional[Tuple[int, int, int]]) -> None:
        """
        Ejecuta la acción seleccionada, actualizando la posición si corresponde.

        Args:
            accion: Acción ejecutada ('move' o 'idle').
            nueva_posicion: Coordenadas destino, si aplica.
        """
        if accion == 'move' and nueva_posicion:
            self.x, self.y, self.z = nueva_posicion

    # -------------------------------------------------------------------------
    # INTERFAZ PRINCIPAL (percepción–decisión–acción)
    # -------------------------------------------------------------------------
    def decide_and_act(self, t: int, entorno: Any, robots: List[Any],
                       monstruos: List[Any], K: int) -> Dict[str, Any]:
        """
        Ejecuta un ciclo completo de percepción, decisión y acción.

        Args:
            t: Tick de simulación.
            entorno: Entorno 3D.
            robots: Lista de robots (no utilizada).
            monstruos: Lista de monstruos activos (incluye este agente).
            K: Frecuencia de activación.

        Returns:
            dict: Evento con los resultados de la acción.
        """
        percepcion = self.perceive(entorno)
        accion, nueva_pos = self.decide_action(entorno, t, K)
        self.ejecutar_accion(accion, nueva_pos)

        return {
            'agent_id': self.id,
            't': t,
            'action': accion,
            'new_pos': (self.x, self.y, self.z),
            'tipo': 'monster',
            'moved': accion == 'move'
        }

    # -------------------------------------------------------------------------
    # REGISTRO Y REPRESENTACIÓN
    # -------------------------------------------------------------------------
    def obtener_estado_log(self) -> Dict[str, Any]:
        """
        Devuelve el estado actual del agente para registro o depuración.

        Returns:
            dict: Datos básicos de identificación y estado.
        """
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'tipo': 'monster',
            'acciones_realizadas': self.acciones_realizadas
        }

    def __repr__(self) -> str:
        """Representación legible para depuración."""
        return f"<AgenteMonstruo id={self.id} pos=({self.x},{self.y},{self.z}) acciones={self.acciones_realizadas}>"
