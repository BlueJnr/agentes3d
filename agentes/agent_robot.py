# agent_robot.py
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

# Direcciones y rotaciones posibles en el espacio energético tridimensional
_ORIENTACIONES: Dict[str, Tuple[int, int, int]] = {
    '+X': (1, 0, 0), '-X': (-1, 0, 0),
    '+Y': (0, 1, 0), '-Y': (0, -1, 0),
    '+Z': (0, 0, 1), '-Z': (0, 0, -1)
}

# Rotación cíclica en el plano XY (el robot no tiene arriba ni abajo)
_ORIENTACIONES_CICLICAS = ['+X', '+Y', '-X', '-Y']

# Estructura de percepción extendida:
# (energómetro, roboscanner, (monstroscopio_detectado, posicion_relativa), vacuscopio)
PercepcionClave = Tuple[bool, bool, Tuple[bool, Optional[str]], bool]

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
        self.orientacion = orientacion if orientacion in _ORIENTACIONES else random.choice(list(_ORIENTACIONES.keys()))

        # Memoria interna del agente racional
        self.memoria: Dict[str, Any] = {
            'historial': [],  # [(t, percepcion, accion, posicion)]
            'vacuscopio_activado': False,
            'posicion_anterior': (x, y, z)
        }

        # Tabla percepción–acción jerárquica
        self.tabla_mapeo: Dict[PercepcionClave, Dict[str, Any]] = {
            # --- Nivel 1: Energómetro activo ---
            (True, True, (True, "al_frente"), True): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, True, (True, "al_lado"), True): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, True, (True, "al_frente"), False): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, True, (True, "al_lado"), False): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, True, (False, None), True): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, True, (False, None), False): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, False, (True, "al_frente"), True): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, False, (True, "al_lado"), True): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, False, (True, "al_frente"), False): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, False, (True, "al_lado"), False): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, False, (False, None), True): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},
            (True, False, (False, None), False): {"accion": "VACUUMATOR", "razon": "monstruo_en_celda"},

            # --- Nivel 2: Vacuscopio activo ---
            (False, True, (True, "al_frente"), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},
            (False, True, (True, "al_lado"), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},
            (False, True, (False, None), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},
            (False, False, (True, "al_frente"), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},
            (False, False, (True, "al_lado"), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},
            (False, False, (False, None), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},

            # --- Nivel 3: Robot al frente ---
            (False, True, (True, "al_frente"), False): {"accion": "REORIENTADOR", "param": "+90", "razon": "robot_al_frente"},
            (False, True, (True, "al_lado"), False): {"accion": "REORIENTADOR", "param": "+90", "razon": "robot_al_frente"},
            (False, True, (False, None), False): {"accion": "REORIENTADOR", "param": "+90", "razon": "robot_al_frente"},

            # --- Nivel 4: Monstruo detectado cerca ---
            (False, False, (True, "al_frente"), False): {"accion": "PROPULSOR", "razon": "monstruo_en_frente"},
            (False, False, (True, "al_lado"), False): {"accion": "REORIENTADOR", "razon": "alinear_con_monstruo"},

            # --- Nivel 5: Acción por defecto ---
            (False, False, (False, None), False): {"accion": "PROPULSOR", "razon": "accion_por_defecto"},
        }

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
        dx, dy, dz = _ORIENTACIONES[self.orientacion]
        frente = (self.x + dx, self.y + dy, self.z + dz)

        return {
            'giroscopio': self.orientacion,
            'energometro': any((m.x, m.y, m.z) == (self.x, self.y, self.z) for m in monstruos),
            'roboscanner': any((r.x, r.y, r.z) == frente and r.id != self.id for r in robots),
            'vacuscopio': self.memoria.get('vacuscopio_activado', False),
            'monstroscopio': self._detectar_monstruos(monstruos, dx, dy, dz),
            'posicion_anterior': self.memoria.get('posicion_anterior')
        }

    def _detectar_monstruos(
            self,
            monstruos: List[Any],
            dx: int,
            dy: int,
            dz: int
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Detecta la presencia y posición relativa de un monstruo mediante el sensor Monstroscopio.

        El sensor analiza los cinco costados visibles del robot (frontal, laterales y superior/inferior),
        excluyendo su parte posterior. Si un monstruo es detectado, devuelve una tupla estructurada con
        el estado de detección, la posición relativa y la orientación espacial correspondiente.

        Args:
            monstruos (List[Any]): Lista de entidades monstruo activas en el entorno energético.
            dx (int): Componente X de la orientación actual del robot.
            dy (int): Componente Y de la orientación actual del robot.
            dz (int): Componente Z de la orientación actual del robot.

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: Tupla con la información de detección del Monstroscopio:
                - ``detectado`` (bool): Indica si se detectó un monstruo.
                - ``pos_relativa`` (Optional[str]): Posición del monstruo respecto al robot.
                  Puede ser ``"al_frente"`` o ``"al_lado"``; ``None`` si no se detecta nada.
                - ``orientacion_monstruo`` (Optional[str]): Dirección cardinal donde se encuentra
                  el monstruo (por ejemplo, ``'+X'``, ``'-Y'``); ``None`` si no hay detección.

        """
        atras = (-dx, -dy, -dz)
        for dir_label, (ddx, ddy, ddz) in _ORIENTACIONES.items():
            if (ddx, ddy, ddz) == atras:
                continue
            if any((m.x, m.y, m.z) == (self.x + ddx, self.y + ddy, self.z + ddz) for m in monstruos):
                if (ddx, ddy, ddz) == (dx, dy, dz):
                    return True, "al_frente", dir_label
                else:
                    return True, "al_lado", dir_label
        return False, None, None

    # -------------------------------------------------------------------------
    # DECISIÓN
    # -------------------------------------------------------------------------
    def decidir_accion(self, percepcion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determina la acción a ejecutar a partir de la percepción actual del entorno.

        El agente consulta su tabla percepción–acción para decidir qué efector activar.
        Si la regla correspondiente no especifica un parámetro de dirección (`param`),
        se utiliza la orientación detectada por el sensor `monstroscopio` como valor por defecto.

        La clave de decisión se construye con las siguientes percepciones:
            (energómetro, roboscanner, (monstroscopio.detectado, monstroscopio.pos_relativa), vacuscopio)

        Args:
            percepcion (Dict[str, Any]): Estructura generada por `percibir()`, que contiene
                las lecturas actuales de los sensores del agente.

        Returns:
            Dict[str, Any]: Diccionario con la decisión seleccionada, con los siguientes campos:
                - ``accion`` (str): Nombre del efector a ejecutar (p. ej., "VACUUMATOR", "PROPULSOR").
                - ``param`` (Optional[str]): Dirección o ángulo asociado a la acción. Si no se
                  encuentra definido en la regla, se toma de `monstroscopio[2]`.
                - ``razon`` (str): Descripción textual que explica la justificación de la acción.

        """
        clave = (
            percepcion["energometro"],
            percepcion["roboscanner"],
            percepcion["monstroscopio"][:2],  # (detectado, posicion_relativa)
            percepcion["vacuscopio"]
        )

        # Reinicia el estado del Vacuscopio para la siguiente iteración
        self.memoria["vacuscopio_activado"] = False

        # Recupera la regla correspondiente de la tabla percepción–acción
        regla = self.tabla_mapeo.get(clave)
        if regla:
            # Si no tiene parámetro explícito, usar la dirección detectada por el Monstroscopio
            param = regla.get("param", percepcion["monstroscopio"][2])
            return {
                "accion": regla["accion"],
                "param": param,
                "razon": regla["razon"]
            }

        # Regla por defecto (no se encontró coincidencia en la tabla)
        return {
            "accion": "PROPULSOR",
            "param": percepcion["monstroscopio"][2],
            "razon": "accion_por_defecto"
        }

    def ejecutar_accion(self, accion: str, param: Optional[str], entorno: Any, monstruos: List[Any]) -> Dict[str, Any]:
        """
        Ejecuta físicamente la acción seleccionada mediante sus efectores.

        Args:
            accion (str): Nombre del efector a usar ("PROPULSOR", "REORIENTADOR", "VACUUMATOR").
            param (Optional[str]): Parámetro adicional (ángulo o dirección).
            entorno (EntornoOperacion): Entorno de Operación donde interactúa.
            monstruos (List[Any]): Monstruos reflejo presentes (para el Vacuumator).

        Returns:
            Dict[str, Any]: Resultado estructurado de la acción ejecutada:
                - 'exito': bool, indica si la acción se completó correctamente.
                - 'razon': str, descripción textual del resultado.
                - 'resultado': dict, detalles específicos (posición, entidad afectada, etc.).
        """
        if accion == "PROPULSOR":
            return self._propulsor(entorno)

        elif accion == "REORIENTADOR":
            return self._reorientador(param or "+90")

        elif accion == "VACUUMATOR":
            return self._vacuumator(entorno, monstruos)

        return {
            "exito": False,
            "razon": "accion_no_reconocida",
            "resultado": {}
        }

    # -------------------------------------------------------------------------
    # EFECTORES
    # -------------------------------------------------------------------------
    def _propulsor(self, entorno: Any) -> Dict[str, Any]:
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
        dx, dy, dz = _ORIENTACIONES[self.orientacion]
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
        if sentido in _ORIENTACIONES:
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
        self.orientacion = _ORIENTACIONES_CICLICAS[(i + 1) % 4] if sentido == '+90' else _ORIENTACIONES_CICLICAS[
            (i - 1) % 4]

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
                - 'accion': efector utilizado.
                - 'exito': indicador booleano del resultado.
                - 'razon': descripción del motivo de la acción.
        """
        percepcion = self.percibir(robots, monstruos)
        decision = self.decidir_accion(percepcion)
        accion, param = decision["accion"], decision["param"]
        self.actualizar_memoria(t, percepcion, accion)
        evento = self.ejecutar_accion(accion, param, entorno, monstruos)

        return {
            "accion": accion,
            "exito": evento.get("exito", False),
            "razon": evento.get("razon", decision.get("razon", "")),
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
        estado_perceptual = {
            'ori': percepcion.get('giroscopio'),
            'E': percepcion.get('energometro', False),
            'R': percepcion.get('roboscanner', False),
            'M': bool(percepcion.get('monstroscopio')),
            'V': percepcion.get('vacuscopio', False),
            'pos_prev': percepcion.get('posicion_anterior'),  # único dato espacial permitido
        }

        # Guardar en el historial
        self.memoria['historial'].append({
            't': t,
            'p': estado_perceptual,
            'a': accion
        })

    def __repr__(self) -> str:
        """Representación textual simplificada del robot para depuración."""
        return f"<AgenteRacionalRobot id={self.id} pos=({self.x},{self.y},{self.z}) ori={self.orientacion}>"
