# agent_monster.py
import random
from typing import Tuple, Optional, List, Dict, Any


class AgenteReflejoMonstruo:
    """
    Agente reflejo simple que representa un monstruo energético dentro del entorno N³.

    Actúa de forma reactiva sin memoria ni razonamiento, moviéndose aleatoriamente hacia
    una Zona Libre adyacente con probabilidad `p_movimiento` en cada ciclo múltiplo de `K`.
    """

    _DIRECCIONES: Dict[str, Tuple[int, int, int]] = {
        '+X': (1, 0, 0), '-X': (-1, 0, 0),
        '+Y': (0, 1, 0), '-Y': (0, -1, 0),
        '+Z': (0, 0, 1), '-Z': (0, 0, -1)
    }

    def __init__(self, id: int, x: int, y: int, z: int, p_movimiento: float = 0.7) -> None:
        """Inicializa el agente reflejo con posición inicial y probabilidad de movimiento."""
        self.id = id
        self.x, self.y, self.z = int(x), int(y), int(z)
        self.p_movimiento = p_movimiento
        self.activo = True

    def percibir(self, entorno: Any) -> Dict[str, Any]:
        """Obtiene las direcciones válidas de movimiento hacia Zonas Libres adyacentes."""
        movimientos_validos = self._obtener_movimientos_validos(entorno)
        return {
            'movimientos_validos': movimientos_validos,
            'puede_moverse': bool(movimientos_validos)
        }

    def _obtener_movimientos_validos(self, entorno: Any) -> List[Tuple[int, int, int]]:
        """Devuelve las direcciones transitables hacia Zonas Libres dentro del entorno."""
        movimientos_validos = []
        for _, (dx, dy, dz) in self._DIRECCIONES.items():
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if self._es_movimiento_valido(entorno, nx, ny, nz):
                movimientos_validos.append((dx, dy, dz))
        return movimientos_validos

    def _es_movimiento_valido(self, entorno: Any, x: int, y: int, z: int) -> bool:
        """Retorna True si la coordenada destino está dentro del entorno y es Zona Libre."""
        if not (0 <= x < entorno.N and 0 <= y < entorno.N and 0 <= z < entorno.N):
            return False
        return entorno.grid[x, y, z] != entorno.ZONA_VACIA

    def decidir_accion(self, percepcion: Dict[str, Any], ciclo_actual: int, K: int) -> Dict[str, Any]:
        """
        Determina la acción a ejecutar según el ciclo actual, la probabilidad y las zonas libres.
        """
        if ciclo_actual % K != 0:
            return {"accion": "inactivo", "direccion": None, "razon": "no_en_ciclo"}
        if random.random() > self.p_movimiento:
            return {"accion": "inactivo", "direccion": None, "razon": "no_supera_probabilidad"}
        if not percepcion["puede_moverse"]:
            return {"accion": "inactivo", "direccion": None, "razon": "sin_movimientos_validos"}

        direccion = random.choice(percepcion["movimientos_validos"])
        return {"accion": "mover", "direccion": direccion, "razon": "movimiento_aleatorio"}

    def ejecutar_accion(self, accion: str, direccion: Optional[Tuple[int, int, int]]) -> bool:
        """Ejecuta el movimiento actualizando la posición si la acción es 'mover'."""
        if accion == "mover" and direccion:
            dx, dy, dz = direccion
            self.x += dx
            self.y += dy
            self.z += dz
            return True
        return False

    def percibir_decidir_actuar(self, t: int, entorno: Any, K: int) -> Dict[str, Any]:
        """Ejecuta el ciclo completo de percepción, decisión y acción."""
        percepcion = self.percibir(entorno)
        decision = self.decidir_accion(percepcion, t, K)
        exito = self.ejecutar_accion(decision["accion"], decision["direccion"])
        return {
            "accion": decision["accion"],
            "exito": exito,
            "razon": decision.get("razon", "")
        }

    def __repr__(self) -> str:
        """Devuelve una representación textual simplificada del agente."""
        return f"<AgenteReflejoMonstruo id={self.id} pos=({self.x},{self.y},{self.z})>"
