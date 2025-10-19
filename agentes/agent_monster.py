# agent_monster.py
import random
from typing import Tuple, Optional, List, Dict, Any


class AgenteReflejoMonstruo:
    """
    Agente reflejo simple de tipo **Monstruo** dentro del Entorno de Operación Energético.

    Este agente representa una **entidad energética inmaterial** cuya existencia ocupa
    un cubo dentro del entorno N³. Su comportamiento está definido por las siguientes
    características (según los requisitos del sistema):

    - No posee memoria interna ni capacidad de aprendizaje.
    - Su conducta es puramente **reactiva** ante las condiciones del entorno inmediato.
    - Opera con una **frecuencia de activación** cada `K` ciclos energéticos.
    - En su ciclo de activación, con probabilidad `p_movimiento`, se desplaza de manera
      **aleatoria** hacia una de las **Zonas Libres** adyacentes (6 lados posibles).
    - Las **Zonas Vacías** son regiones energéticas bloqueadas e intransitables, por lo
      que el agente nunca puede entrar en ellas ni atravesarlas.

    Este agente refleja la definición de "agente reflejo simple" especificada en los
    requisitos: una entidad que actúa basándose únicamente en su percepción actual,
    sin razonamiento histórico ni planificación futura.
    """

    # Direcciones ortogonales posibles (movimiento cartesiano 3D)
    _DIRECCIONES: Dict[str, Tuple[int, int, int]] = {
        '+X': (1, 0, 0), '-X': (-1, 0, 0),
        '+Y': (0, 1, 0), '-Y': (0, -1, 0),
        '+Z': (0, 0, 1), '-Z': (0, 0, -1)
    }

    def __init__(self, id: int, x: int, y: int, z: int, p_movimiento: float = 0.7) -> None:
        """
        Inicializa un agente reflejo simple de tipo Monstruo.

        Args:
            id (int): Identificador único del agente.
            x (int): Coordenada X inicial dentro del entorno energético.
            y (int): Coordenada Y inicial dentro del entorno energético.
            z (int): Coordenada Z inicial dentro del entorno energético.
            p_movimiento (float): Probabilidad de desplazamiento en cada ciclo activo.
                Por defecto es 0.7 (70% de probabilidad de moverse cuando se activa).

        Atributos principales:
            - `p_movimiento`: define la naturaleza probabilística del movimiento.
            - `acciones_realizadas`: cuenta la cantidad de desplazamientos ejecutados.
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
        Percibe su **entorno energético inmediato**, identificando las **Zonas Libres**
        adyacentes a su posición actual dentro del espacio N³.

        Este método corresponde al subsistema sensorial del agente reflejo. Solo
        considera el entorno inmediato (6 direcciones ortogonales), sin capacidad de
        memorizar o inferir estados anteriores.

        Args:
            entorno (EntornoOperacion): Instancia activa del Entorno de Operación Energético.

        Returns:
            Dict[str, Any]: Estructura con la percepción mínima necesaria para decidir:
                - `'posicion'`: coordenadas actuales (x, y, z).
                - `'movimientos_validos'`: lista de desplazamientos posibles
                  hacia Zonas Libres [(dx, dy, dz), ...].
                - `'puede_moverse'`: indicador booleano de si hay celdas libres disponibles.
        """
        movimientos_validos = self._obtener_movimientos_validos(entorno)
        return {
            'movimientos_validos': movimientos_validos,
            'puede_moverse': bool(movimientos_validos)
        }

    def _obtener_movimientos_validos(self, entorno: Any) -> List[Tuple[int, int, int]]:
        """
        Determina las direcciones válidas hacia **Zonas Libres** dentro del entorno.

        Recorre las seis direcciones ortogonales posibles y verifica, mediante
        `_es_movimiento_valido`, cuáles son transitables.

        Args:
            entorno (EntornoOperacion): Referencia al entorno energético actual.

        Returns:
            List[Tuple[int, int, int]]: Lista de vectores (dx, dy, dz) que representan
            los desplazamientos posibles hacia Zonas Libres.
        """
        movimientos_validos = []
        for _, (dx, dy, dz) in self._DIRECCIONES.items():
            nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
            if self._es_movimiento_valido(entorno, nx, ny, nz):
                movimientos_validos.append((dx, dy, dz))
        return movimientos_validos

    def _es_movimiento_valido(self, entorno: Any, x: int, y: int, z: int) -> bool:
        """
        Verifica si una coordenada destino corresponde a una **Zona Libre** válida.

        Args:
            entorno (EntornoOperacion): Entorno de operación energético.
            x (int): Coordenada X destino.
            y (int): Coordenada Y destino.
            z (int): Coordenada Z destino.

        Returns:
            bool: True si la celda es una Zona Libre y está dentro de los límites del
            entorno; False si es una Zona Vacía o está fuera del cubo energético.
        """
        if not (0 <= x < entorno.N and 0 <= y < entorno.N and 0 <= z < entorno.N):
            return False
        return entorno.grid[x, y, z] != entorno.ZONA_VACIA

    # -------------------------------------------------------------------------
    # DECISIÓN Y ACCIÓN
    # -------------------------------------------------------------------------
    def decidir_accion(self, percepcion: Dict[str, Any], ciclo_actual: int, K: int) -> Dict[str, Any]:
        """
        Decide la acción a ejecutar en función de su percepción actual.

        Este método representa el **comportamiento reflejo simple**: sin razonamiento,
        ni memoria, ni planificación. La decisión se basa únicamente en:
          - El ciclo energético actual (`t`).
          - La probabilidad de movimiento (`p_movimiento`).
          - La existencia de Zonas Libres adyacentes.

        Args:
            percepcion (Dict[str, Any]): Resultado del método `percibir`.
            ciclo_actual (int): Número de ciclo energético actual.
            K (int): Frecuencia de activación del agente (cada K ciclos).

        Returns:
            Dict[str, Any]: Acción seleccionada y su justificación, con los campos:
                - `'accion'`: tipo de acción ("mover" o "inactivo").
                - `'param'`: nueva posición si aplica.
                - `'razon'`: descripción del motivo de la decisión.
        """
        # No se activa hasta su ciclo K
        if ciclo_actual % K != 0:
            return {"accion": "inactivo", "direccion": None, "razon": "no_en_ciclo"}

        # Probabilidad de movimiento no superada
        if random.random() > self.p_movimiento:
            return {"accion": "inactivo", "direccion": None, "razon": "no_supera_probabilidad"}

        # No hay direcciones disponibles
        if not percepcion["puede_moverse"]:
            return {"accion": "inactivo", "direccion": None, "razon": "sin_movimientos_validos"}

        direccion = random.choice(percepcion["movimientos_validos"])
        self.acciones_realizadas += 1
        return {"accion": "mover", "direccion": direccion, "razon": "movimiento_aleatorio"}

    def ejecutar_accion(self, accion: str, direccion: Optional[Tuple[int, int, int]]) -> bool:
        """
        Ejecuta físicamente la acción seleccionada, actualizando su posición si aplica.

        Args:
            accion (str): Tipo de acción a ejecutar ("mover" o "inactivo").
            direccion (Optional[Tuple[int, int, int]]): Vector de desplazamiento (dx, dy, dz)
                hacia el cual el agente se moverá si aplica.

        Returns:
            bool: True si el movimiento se ejecutó correctamente, False en caso contrario.
        """
        if accion == "mover" and direccion:
            dx, dy, dz = direccion
            self.x += dx
            self.y += dy
            self.z += dz
            return True
        return False

    # -------------------------------------------------------------------------
    # CICLO DE VIDA DEL AGENTE
    # -------------------------------------------------------------------------
    def percibir_decidir_actuar(self, t: int, entorno: Any, K: int) -> Dict[str, Any]:
        """
        Ejecuta un **ciclo energético completo** del agente reflejo:
        percepción → decisión → acción.

        Args:
            t (int): Ciclo energético actual.
            entorno (EntornoOperacion): Entorno de Operación donde interactúa el agente.
            K (int): Frecuencia de activación del agente reflejo simple.

        Returns:
            Dict[str, Any]: Información estructurada sobre la acción ejecutada:
                - `'accion'`: Acción ejecutada ("mover" o "inactivo").
                - `'exito'`: Indicador booleano del resultado.
                - `'razon'`: Justificación textual de la decisión.
        """
        percepcion = self.percibir(entorno)
        decision = self.decidir_accion(percepcion, t, K)
        accion, direccion = decision["accion"], decision["direccion"]
        exito = self.ejecutar_accion(accion, direccion)
        return {
            "accion": accion,
            "exito": exito,
            "razon": decision.get("razon", "")
        }

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN Y LOGGING
    # -------------------------------------------------------------------------
    def obtener_estado_log(self) -> Dict[str, Any]:
        """
        Retorna el **estado energético actual** del agente reflejo para propósitos
        de registro o monitoreo dentro de la simulación.

        Returns:
            Dict[str, Any]: Estado actual del agente:
                - `'id'`: Identificador del agente.
                - `'x', 'y', 'z'`: Coordenadas actuales en el entorno energético.
                - `'tipo'`: Tipo de agente ("monstruo").
                - `'acciones_realizadas'`: Contador total de movimientos ejecutados.
        """
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'tipo': 'monstruo',
            'acciones_realizadas': self.acciones_realizadas
        }

    def __repr__(self) -> str:
        """
        Representación textual simplificada del agente reflejo para depuración.

        Returns:
            str: Cadena con el identificador, posición y cantidad de acciones realizadas.
        """
        return f"<AgenteReflejoMonstruo id={self.id} pos=({self.x},{self.y},{self.z}) acciones={self.acciones_realizadas}>"
