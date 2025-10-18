# agent_monster.py
import random
from typing import Tuple, Optional, List, Dict, Any


class AgenteReflejoMonstruo:
    """
    Representa un agente reflejo simple de tipo Monstruo dentro del Entorno de Operación Energético.

    Este agente:
      - No posee memoria interna ni aprendizaje.
      - Su comportamiento es puramente reactivo ante su entorno inmediato.
      - Se activa periódicamente (cada K ciclos) y, con cierta probabilidad,
        se desplaza aleatoriamente hacia una Zona Libre adyacente.

    Las Zonas Vacías son intransitables y representan regiones energéticas bloqueadas.
    """

    # Direcciones ortogonales posibles (movimiento cartesiano 3D)
    _DIRECCIONES: Dict[str, Tuple[int, int, int]] = {
        '+X': (1, 0, 0), '-X': (-1, 0, 0),
        '+Y': (0, 1, 0), '-Y': (0, -1, 0),
        '+Z': (0, 0, 1), '-Z': (0, 0, -1)
    }

    def __init__(self, id: int, x: int, y: int, z: int, p_movimiento: float = 0.7) -> None:
        """
        Inicializa un agente reflejo tipo Monstruo.

        Args:
            id: Identificador único del agente.
            x, y, z: Coordenadas iniciales dentro del entorno energético.
            p_movimiento: Probabilidad de moverse cuando se activa (por defecto = 0.7).
        """
        self.id: int = id
        self.x: int = int(x)
        self.y: int = int(y)
        self.z: int = int(z)
        self.p_movimiento: float = p_movimiento
        self.acciones_realizadas: int = 0

    # -------------------------------------------------------------------------
    # PERCEPCIÓN
    # -------------------------------------------------------------------------
    def percibir(self, entorno: Any) -> Dict[str, Any]:
        """
        Percibe el entorno inmediato, identificando las Zonas Libres adyacentes disponibles.

        Args:
            entorno: Instancia del EntornoOperacion.

        Returns:
            dict: Información perceptual mínima:
                - 'posicion_actual': coordenadas actuales.
                - 'movimientos_validos': desplazamientos posibles (dx, dy, dz).
                - 'puede_moverse': indicador booleano.
        """
        movimientos_validos = self._obtener_movimientos_validos(entorno)
        return {
            'posicion_actual': (self.x, self.y, self.z),
            'movimientos_validos': movimientos_validos,
            'puede_moverse': bool(movimientos_validos)
        }

    def _obtener_movimientos_validos(self, entorno: Any) -> List[Tuple[int, int, int]]:
        """Determina las direcciones válidas hacia Zonas Libres."""
        movimientos_validos = []
        for _, (dx, dy, dz) in self._DIRECCIONES.items():
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if self._es_movimiento_valido(entorno, nx, ny, nz):
                movimientos_validos.append((dx, dy, dz))
        return movimientos_validos

    def _es_movimiento_valido(self, entorno: Any, x: int, y: int, z: int) -> bool:
        """Verifica si la celda destino es una Zona Libre dentro del entorno."""
        if not (0 <= x < entorno.N and 0 <= y < entorno.N and 0 <= z < entorno.N):
            return False
        return entorno.grid[x, y, z] != entorno.ZONA_VACIA

    # -------------------------------------------------------------------------
    # DECISIÓN Y ACCIÓN
    # -------------------------------------------------------------------------
    def decidir_accion(
            self,
            percepcion: Dict[str, Any],
            ciclo_actual: int,
            K: int
    ) -> Tuple[str, Optional[Tuple[int, int, int]]]:
        """
        Decide la acción a ejecutar según una política reflejo energética.
        Usa la percepción inmediata para decidir si puede moverse.

        Reglas:
            - Se activa cada K ciclos energéticos.
            - Cuando se activa, se mueve con probabilidad p_movimiento.
            - Si no hay Zonas Libres adyacentes, permanece quieto.

        Args:
            percepcion: Información perceptual del entorno.
            ciclo_actual: Ciclo de simulación actual.
            K: Frecuencia de activación.

        Returns:
            tuple[str, Optional[tuple[int, int, int]]]: ('mover' o 'inactivo', nueva posición si aplica).
        """
        if ciclo_actual % K != 0:
            return 'inactivo', None
        if random.random() > self.p_movimiento:
            return 'inactivo', None
        if not percepcion['puede_moverse']:
            return 'inactivo', None

        dx, dy, dz = random.choice(percepcion['movimientos_validos'])
        nueva_pos = (
            percepcion['posicion_actual'][0] + dx,
            percepcion['posicion_actual'][1] + dy,
            percepcion['posicion_actual'][2] + dz
        )
        self.acciones_realizadas += 1
        return 'mover', nueva_pos

    def ejecutar_accion(self, accion: str, nueva_posicion: Optional[Tuple[int, int, int]]) -> None:
        """Ejecuta la acción elegida, actualizando la posición si se mueve."""
        if accion == 'mover' and nueva_posicion:
            self.x, self.y, self.z = nueva_posicion

    # -------------------------------------------------------------------------
    # CICLO DE VIDA DEL AGENTE
    # -------------------------------------------------------------------------
    def percibir_decidir_actuar(self, t: int, entorno: Any, K: int) -> Dict[str, Any]:
        """
        Ejecuta el ciclo completo de percepción–decisión–acción del agente reflejo.

        Args:
            t: Ciclo energético actual.
            entorno: Entorno de Operación.
            K: Frecuencia de activación.

        Returns:
            dict: Evento con información de la acción ejecutada.
        """
        percepcion = self.percibir(entorno)
        accion, nueva_pos = self.decidir_accion(percepcion, t, K)
        self.ejecutar_accion(accion, nueva_pos)

        return {
            'agent_id': self.id,
            'ciclo': t,
            'accion': accion,
            'nueva_pos': (self.x, self.y, self.z),
            'tipo': 'monstruo',
            'se_movio': accion == 'mover'
        }

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN Y LOGGING
    # -------------------------------------------------------------------------
    def obtener_estado_log(self) -> Dict[str, Any]:
        """Retorna el estado actual del agente para registro o monitoreo."""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'tipo': 'monstruo',
            'acciones_realizadas': self.acciones_realizadas
        }

    def __repr__(self) -> str:
        """Representación textual del agente para depuración."""
        return f"<AgenteReflejoMonstruo id={self.id} pos=({self.x},{self.y},{self.z}) acciones={self.acciones_realizadas}>"
