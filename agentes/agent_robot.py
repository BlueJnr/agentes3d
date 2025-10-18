# agent_robot.py
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

# Direcciones y rotaciones posibles en el espacio energético tridimensional
_DIRECCIONES: Dict[str, Tuple[int, int, int]] = {
    '+X': (1, 0, 0), '-X': (-1, 0, 0),
    '+Y': (0, 1, 0), '-Y': (0, -1, 0),
    '+Z': (0, 0, 1), '-Z': (0, 0, -1)
}

# Rotación cíclica en el plano XY (el robot no tiene arriba ni abajo)
_ORIENTACIONES_CICLICAS = ['+X', '+Y', '-X', '-Y']

PercepcionClave = Tuple[bool, bool, bool, bool]  # (energómetro, roboscanner, monstroscopio, vacuscopio)


class AgenteRacionalRobot:
    """
    Agente racional de tipo **Robot Monstruicida** dentro del Entorno de Operación Energético.

    Este agente representa una **entidad material** con sensores y efectores que le
    permiten cazar monstruos energéticos en el entorno N³. A diferencia de los agentes
    reflejos simples, el robot posee una **memoria interna individual** y una **tabla
    percepción–acción**, lo que le permite ajustar su comportamiento con base en su
    experiencia pasada.

    Según los requisitos:
      - Cada robot es una instancia independiente que no comparte memoria con otros.
      - Su objetivo es destruir monstruos detectados mediante sensores.
      - Opera de manera iterativa (una acción por segundo).
      - No tiene sensor de ubicación absoluta: solo conoce su orientación (giroscopio)
        y sus percepciones locales.
      - Puede comunicarse con otro robot **solo** si lo detecta directamente frente a él.

    Sensores implementados:
      • **Giroscopio** → orientación del robot.
      • **Monstroscopio** → detección de monstruos en los cinco costados visibles.
      • **Vacuscopio** → se activa al colisionar con una Zona Vacía.
      • **Energómetro espectral** → confirma la presencia de un monstruo en la celda actual.
      • **Roboscanner** → detecta otro robot directamente al frente.

    Efectores implementados:
      • **Propulsor Direccional** → movimiento hacia adelante según su orientación.
      • **Reorientador** → rotación 90° o alineación hacia una dirección específica.
      • **Vacuumator** → destruye monstruos y convierte la celda en Zona Vacía.
    """

    def __init__(self, id: int, x: int, y: int, z: int, orientacion: Optional[str] = None) -> None:
        """
        Inicializa una instancia del agente racional Robot.

        Args:
            id (int): Identificador único del robot.
            x, y, z (int): Coordenadas iniciales dentro del entorno energético.
            orientacion (Optional[str]): Dirección inicial; si no se indica, se elige aleatoriamente.

        Atributos internos principales:
            - `memoria`: estructura que almacena historial de percepciones, posiciones previas
              y celdas bloqueadas detectadas por el Vacuscopio.
            - `tabla_mapeo`: tabla simbólica de reglas percepción–acción.
            - `reglas_usadas`: conjunto de índices de reglas activadas (para análisis).
        """
        self.id = id
        self.x, self.y, self.z = int(x), int(y), int(z)
        self.orientacion = orientacion if orientacion in _DIRECCIONES else random.choice(list(_DIRECCIONES.keys()))

        # Memoria interna del agente racional
        self.memoria: Dict[str, Any] = {
            'historial': [],             # [(t, percepcion, accion, posicion)]
            'paredes_conocidas': set(),  # Celdas donde el Vacuscopio se activó
            'vacuscopio_activado': False,
            'posicion_anterior': (x, y, z)
        }

        # Tabla de mapeo simbólico (percepción → acción)
        self.tabla_mapeo: Dict[PercepcionClave, str] = defaultdict(lambda: 'PROPULSOR')
        self.tabla_mapeo[(True, False, False, False)] = 'VACUUMATOR'
        self.tabla_mapeo[(False, True, False, False)] = 'REORIENTADOR'
        self.tabla_mapeo[(False, False, True, False)] = 'PROPULSOR'

        self.reglas_usadas: Set[int] = set()

    # -------------------------------------------------------------------------
    # PERCEPCIÓN
    # -------------------------------------------------------------------------
    def percibir(self, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """
        Percibe su entorno energético inmediato utilizando sus sensores.

        El robot obtiene información de su orientación actual, la presencia de
        obstáculos o entidades cercanas (robots y monstruos), y el estado de su
        Vacuscopio. Esta información compone su **creencia actual**.

        Args:
            robots (List[Any]): Lista de otros robots activos en el entorno.
            monstruos (List[Any]): Lista de monstruos reflejo presentes.

        Returns:
            Dict[str, Any]: Percepción estructurada del entorno local:
                - `'giroscopio'`: orientación actual.
                - `'energometro'`: True si un monstruo ocupa la misma celda.
                - `'roboscanner'`: True si un robot está justo al frente.
                - `'vacuscopio'`: True si el último intento resultó en colisión.
                - `'monstroscopio'`: dirección del monstruo detectado (5 costados).
                - `'celda_frontal'`: coordenadas de la celda hacia la que mira.
        """
        dx, dy, dz = _DIRECCIONES[self.orientacion]
        frente = (self.x + dx, self.y + dy, self.z + dz)

        percepcion_especifica = {
            'giroscopio': self.orientacion,
            'energometro': any((m.x, m.y, m.z) == (self.x, self.y, self.z) for m in monstruos),
            'roboscanner': any((r.x, r.y, r.z) == frente and r.id != self.id for r in robots),
            'vacuscopio': self.memoria.get('vacuscopio_activado', False),
            'monstroscopio': self._detectar_monstruos(monstruos, dx, dy, dz),
            'celda_frontal': frente
        }

        return {
            'id': self.id,
            'tipo': 'robot',
            'posicion': (self.x, self.y, self.z),
            'percepcion': percepcion_especifica
        }

    def _detectar_monstruos(self, monstruos: List[Any], dx: int, dy: int, dz: int) -> Optional[str]:
        """
        Implementa el sensor **Monstroscopio**.

        Detecta la existencia de un monstruo en cualquiera de los cinco costados
        visibles del robot (frontal, laterales y superior/inferior relativos),
        excluyendo su parte posterior.

        Args:
            monstruos (List[Any]): Lista de entidades monstruo activas.
            dx, dy, dz (int): Dirección actual del frente del robot.

        Returns:
            Optional[str]: Etiqueta de dirección ('+X', '-Y', etc.) donde se detectó
            el monstruo; None si no hay detección.
        """
        atras = (-dx, -dy, -dz)
        for dir_label, (ddx, ddy, ddz) in _DIRECCIONES.items():
            if (ddx, ddy, ddz) == atras:
                continue
            if any((m.x, m.y, m.z) == (self.x + ddx, self.y + ddy, self.z + ddz) for m in monstruos):
                return dir_label
        return None

    # -------------------------------------------------------------------------
    # DECISIÓN
    # -------------------------------------------------------------------------
    def decidir_accion(self, percepcion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determina la acción a ejecutar en función de la percepción actual.

        El robot aplica una jerarquía de reglas racionales basada en la tabla
        percepción–acción y su memoria interna. Las prioridades son:

            1. **Energómetro** activo → usar Vacuumator.
            2. **Vacuscopio** activo → girar (Reorientador).
            3. **Roboscanner** detecta robot al frente → coordinar rotación.
            4. **Monstroscopio** detecta monstruo → orientarse o avanzar.
            5. Caso por defecto → aplicar acción según tabla mapeo (aprendida).

        Args:
            percepcion (Dict[str, Any]): Resultado del sensor `percibir()`.

        Returns:
            Dict[str, Any]: Acción seleccionada con su motivo:
                - `'accion'`: nombre del efector a usar.
                - `'param'`: dirección o ángulo si aplica.
                - `'razon'`: justificación textual.
        """
        p = percepcion['percepcion']

        # 1. Monstruo en la misma celda → destruir
        if p['energometro']:
            self.reglas_usadas.add(0)
            return {"accion": "VACUUMATOR", "param": None, "razon": "monstruo_en_celda"}

        # 2. Colisión previa (Vacuscopio) → girar
        if p['vacuscopio']:
            self.reglas_usadas.add(1)
            return {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"}

        # 3. Robot al frente → decisión cooperativa
        if p['roboscanner']:
            self.reglas_usadas.add(2)
            return {"accion": "REORIENTADOR", "param": "+90", "razon": "robot_al_frente"}

        # 4. Monstruo detectado cerca → orientar o avanzar
        if p['monstroscopio']:
            self.reglas_usadas.add(3)
            direccion = p['monstroscopio']
            if direccion == self.orientacion:
                return {"accion": "PROPULSOR", "param": None, "razon": "monstruo_en_frente"}
            else:
                return {"accion": "REORIENTADOR", "param": direccion, "razon": "alinear_con_monstruo"}

        # 5. Acción por defecto → usar mapeo simbólico aprendido
        clave: PercepcionClave = (
            p['energometro'],
            p['roboscanner'],
            bool(p['monstroscopio']),
            p['vacuscopio']
        )
        accion = self.tabla_mapeo[clave]
        self.reglas_usadas.add(4)
        return {"accion": accion, "param": None, "razon": "accion_por_defecto"}

    # -------------------------------------------------------------------------
    # EFECTORES
    # -------------------------------------------------------------------------
    def _propulsor(self, entorno: Any, robots: List[Any]) -> Dict[str, Any]:
        """
        Efector **Propulsor Direccional**.

        Intenta avanzar hacia adelante según la orientación actual. Si la celda
        frontal es una Zona Libre, actualiza su posición; si es una Zona Vacía,
        activa su Vacuscopio y registra la colisión.

        Args:
            entorno (EntornoOperacion): Referencia al entorno energético.
            robots (List[Any]): Otros robots presentes (para evitar superposición).

        Returns:
            Dict[str, Any]: Resultado del intento de movimiento:
                - `'exito'`: True si se movió correctamente.
                - `'resultado'`: nueva posición o celda bloqueada.
                - `'razon'`: descripción textual del evento.
        """
        dx, dy, dz = _DIRECCIONES[self.orientacion]
        nx, ny, nz = self.x + dx, self.y + dy, self.z + dz

        tipo = entorno.obtener_tipo_celda(nx, ny, nz)
        if tipo == entorno.ZONA_LIBRE:
            self.memoria['posicion_anterior'] = (self.x, self.y, self.z)
            self.x, self.y, self.z = nx, ny, nz
            self.memoria['vacuscopio_activado'] = False
            return {
                "accion": "PROPULSOR",
                "exito": True,
                "resultado": {"nueva_posicion": (nx, ny, nz)},
                "razon": "avance_exitoso"
            }

        # Colisión con Zona Vacía → activa Vacuscopio
        self.memoria['paredes_conocidas'].add((nx, ny, nz))
        self.memoria['vacuscopio_activado'] = True
        return {
            "accion": "PROPULSOR",
            "exito": False,
            "resultado": {"colision": True, "celda_bloqueada": (nx, ny, nz)},
            "razon": "colision_con_pared"
        }

    def _reorientador(self, sentido: str = '+90') -> Dict[str, Any]:
        """
        Efector **Reorientador**.

        Permite girar 90° hacia un lado o alinearse directamente con una
        dirección específica, dependiendo del parámetro recibido.

        Args:
            sentido (str): Ángulo o dirección destino ('+90', '-90', '+X', etc.).

        Returns:
            Dict[str, Any]: Resultado de la rotación:
                - `'nueva_orientacion'`: orientación posterior al giro.
                - `'razon'`: motivo del cambio.
        """
        if sentido in _DIRECCIONES:
            self.orientacion = sentido
            return {
                "accion": "REORIENTADOR",
                "exito": True,
                "resultado": {"nueva_orientacion": self.orientacion},
                "razon": "alineacion_directa_con_monstruo"
            }

        # Rotación cíclica en plano XY
        if self.orientacion not in _ORIENTACIONES_CICLICAS:
            self.orientacion = '+X'
        i = _ORIENTACIONES_CICLICAS.index(self.orientacion)
        self.orientacion = _ORIENTACIONES_CICLICAS[(i + 1) % 4] if sentido == '+90' else _ORIENTACIONES_CICLICAS[(i - 1) % 4]

        return {
            "accion": "REORIENTADOR",
            "exito": True,
            "resultado": {"nueva_orientacion": self.orientacion},
            "razon": "rotacion_lateral"
        }

    def _vacuumator(self, entorno: Any, monstruos: List[Any]) -> Dict[str, Any]:
        """
        Efector **Vacuumator**.

        Arma de destrucción energética que elimina monstruos presentes en la
        celda actual. Convierte la celda en una **Zona Vacía**, destruyendo
        tanto al monstruo como al propio robot (según los requisitos).

        Args:
            entorno (EntornoOperacion): Entorno energético activo.
            monstruos (List[Any]): Lista de monstruos presentes.

        Returns:
            Dict[str, Any]: Resultado de la operación de eliminación:
                - `'monstruos_eliminados'`: IDs de monstruos destruidos.
                - `'celda'`: coordenadas afectadas.
                - `'razon'`: descripción del resultado.
        """
        eliminados = [m for m in monstruos if (m.x, m.y, m.z) == (self.x, self.y, self.z)]

        for m in eliminados:
            entorno.eliminar_monstruo(m.id)

        entorno.grid[self.x, self.y, self.z] = entorno.ZONA_VACIA

        return {
            "accion": "VACUUMATOR",
            "exito": bool(eliminados),
            "resultado": {
                "monstruos_eliminados": [m.id for m in eliminados],
                "celda": (self.x, self.y, self.z)
            },
            "razon": "monstruo_destruido" if eliminados else "sin_objetivos"
        }

    # -------------------------------------------------------------------------
    # CICLO DE VIDA
    # -------------------------------------------------------------------------
    def percibir_decidir_actuar(self, t: int, entorno: Any, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """
        Ejecuta un ciclo completo del robot: percepción → decisión → acción.

        Este ciclo corresponde a una iteración del tiempo energético (1 segundo).
        Cada robot racional procesa su entorno, elige una acción y la ejecuta
        mediante sus efectores.

        Args:
            t (int): Ciclo energético actual.
            entorno (EntornoOperacion): Entorno de Operación donde interactúa.
            robots (List[Any]): Otros robots activos.
            monstruos (List[Any]): Monstruos reflejo presentes.

        Returns:
            Dict[str, Any]: Resultado del ciclo de vida:
                - `'accion'`: efector utilizado.
                - `'exito'`: indicador booleano del resultado.
                - `'razon'`: descripción del motivo de la acción.
                - `'resultado'`: detalles de la ejecución.
        """
        percepcion = self.percibir(robots, monstruos)
        decision = self.decidir_accion(percepcion)
        accion, param = decision["accion"], decision["param"]
        self.actualizar_memoria(t, percepcion, accion)

        if accion == "PROPULSOR":
            evento = self._propulsor(entorno, robots)
        elif accion == "REORIENTADOR":
            evento = self._reorientador(param or "+90")
        elif accion == "VACUUMATOR":
            evento = self._vacuumator(entorno, monstruos)
        else:
            evento = {"exito": False, "razon": "accion_no_reconocida", "resultado": {}}

        return {
            "agent_id": self.id,
            "tipo": "robot",
            "tick": t,
            "accion": accion,
            "exito": evento.get("exito", False),
            "razon": evento.get("razon", decision.get("razon", "")),
            "resultado": evento.get("resultado", {}),
        }

    # -------------------------------------------------------------------------
    # MEMORIA Y APRENDIZAJE
    # -------------------------------------------------------------------------
    def actualizar_memoria(self, t: int, percepcion: Dict[str, Any], accion: str) -> None:
        """
        Actualiza la **memoria simbólica** del agente racional.

        Registra las percepciones y la acción ejecutada, permitiendo el
        aprendizaje basado en experiencias previas (refuerzo simbólico).

        Args:
            t (int): Ciclo energético actual.
            percepcion (Dict[str, Any]): Información percibida del entorno.
            accion (str): Acción ejecutada durante el ciclo.
        """
        self.memoria['historial'].append((t, dict(percepcion), accion, (self.x, self.y, self.z)))
        if percepcion['percepcion'].get('vacuscopio'):
            self.memoria['paredes_conocidas'].add(percepcion['percepcion'].get('celda_frontal'))

    def aprender_de_evento(self, evento: Dict[str, Any], recompensa: float = 0.0) -> None:
        """
        Aprendizaje simbólico basado en refuerzo.

        Reasigna la acción de una combinación percepción–estado si el evento
        resultó exitoso y obtuvo recompensa positiva.

        Args:
            evento (Dict[str, Any]): Resultado del último ciclo.
            recompensa (float): Valor de refuerzo (positiva si fue exitosa).
        """
        if recompensa <= 0 or not self.memoria['historial']:
            return
        _, p, a, _ = self.memoria['historial'][-1]
        clave: PercepcionClave = (p['energometro'], p['roboscanner'], bool(p['monstroscopio']), p['vacuscopio'])
        self.tabla_mapeo[clave] = a

    def __repr__(self) -> str:
        """Representación textual simplificada del robot para depuración."""
        return f"<AgenteRacionalRobot id={self.id} pos=({self.x},{self.y},{self.z}) ori={self.orientacion}>"
