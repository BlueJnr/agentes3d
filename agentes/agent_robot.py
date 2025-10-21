# agent_robot.py
import copy
import random
from typing import Any, Dict, List, Optional, Set, Tuple

# Direcciones y rotaciones posibles en el espacio energético tridimensional
_ORIENTACIONES: Dict[str, Tuple[int, int, int]] = {
    '+X': (1, 0, 0), '-X': (-1, 0, 0),
    '+Y': (0, 1, 0), '-Y': (0, -1, 0),
    '+Z': (0, 0, 1), '-Z': (0, 0, -1)
}

# Rotación cíclica en el plano XY
_ORIENTACIONES_CICLICAS = ['+X', '+Y', '-X', '-Y']

# Clave de percepción extendida: (energómetro, roboscanner, (monstroscopio_detectado, pos_relativa), vacuscopio)
PercepcionClave = Tuple[bool, bool, Tuple[bool, Optional[str]], bool]


class AgenteRacionalRobot:
    """Agente racional tipo robot que caza monstruos en el entorno N³."""

    _TABLA_BASE: Dict[PercepcionClave, Dict[str, Any]] = {
        # Nivel 1: Energómetro activo
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

        # Nivel 2: Vacuscopio activo
        (False, True, (True, "al_frente"), True): {"accion": "REORIENTADOR", "param": "+90",
                                                   "razon": "obstaculo_detectado"},
        (False, True, (True, "al_lado"), True): {"accion": "REORIENTADOR", "param": "+90",
                                                 "razon": "obstaculo_detectado"},
        (False, True, (False, None), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},
        (False, False, (True, "al_frente"), True): {"accion": "REORIENTADOR", "param": "+90",
                                                    "razon": "obstaculo_detectado"},
        (False, False, (True, "al_lado"), True): {"accion": "REORIENTADOR", "param": "+90",
                                                  "razon": "obstaculo_detectado"},
        (False, False, (False, None), True): {"accion": "REORIENTADOR", "param": "+90", "razon": "obstaculo_detectado"},

        # Nivel 3: Robot al frente
        (False, True, (True, "al_frente"), False): {"accion": "REORIENTADOR", "param": "+90",
                                                    "razon": "robot_al_frente"},
        (False, True, (True, "al_lado"), False): {"accion": "REORIENTADOR", "param": "+90", "razon": "robot_al_frente"},
        (False, True, (False, None), False): {"accion": "REORIENTADOR", "param": "+90", "razon": "robot_al_frente"},

        # Nivel 4: Monstruo cerca
        (False, False, (True, "al_frente"), False): {"accion": "PROPULSOR", "razon": "monstruo_en_frente"},
        (False, False, (True, "al_lado"), False): {"accion": "REORIENTADOR", "razon": "alinear_con_monstruo"},

        # Nivel 5: Acción por defecto
        (False, False, (False, None), False): {"accion": "PROPULSOR", "razon": "accion_por_defecto"},
    }

    def __init__(self, id: int, x: int, y: int, z: int, orientacion: Optional[str] = None) -> None:
        """Inicializa el robot con posición, orientación y memoria independiente."""
        self.id = id
        self.x, self.y, self.z = int(x), int(y), int(z)
        self.orientacion = orientacion if orientacion in _ORIENTACIONES else random.choice(list(_ORIENTACIONES.keys()))
        self.memoria = {'historial': [], 'vacuscopio_activado': False, 'posicion_anterior': (x, y, z)}
        self.tabla_mapeo = copy.deepcopy(self._TABLA_BASE)
        self.reglas_usadas: Set[int] = set()
        self.activo = True

    # -------------------------------------------------------------------------
    # PERCEPCIÓN
    # -------------------------------------------------------------------------
    def percibir(self, robots: List[Any], monstruos: List[Any]) -> Dict[str, Any]:
        """Lee sensores locales para construir la percepción actual del entorno."""
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

    def _detectar_monstruos(self, monstruos: List[Any], dx: int, dy: int, dz: int) -> Tuple[
        bool, Optional[str], Optional[str]]:
        """Detecta monstruos al frente o a los lados, excluyendo la parte posterior."""
        atras = (-dx, -dy, -dz)
        for dir_label, (ddx, ddy, ddz) in _ORIENTACIONES.items():
            if (ddx, ddy, ddz) == atras:
                continue
            if any((m.x, m.y, m.z) == (self.x + ddx, self.y + ddy, self.z + ddz) for m in monstruos):
                return (True, "al_frente", dir_label) if (ddx, ddy, ddz) == (dx, dy, dz) else (True, "al_lado",
                                                                                               dir_label)
        return False, None, None

    # -------------------------------------------------------------------------
    # DECISIÓN Y ACCIÓN
    # -------------------------------------------------------------------------
    def decidir_accion(self, percepcion: Dict[str, Any]) -> Dict[str, Any]:
        """Selecciona la acción según la tabla percepción–acción."""
        clave = (
            percepcion["energometro"],
            percepcion["roboscanner"],
            percepcion["monstroscopio"][:2],
            percepcion["vacuscopio"]
        )
        self.memoria["vacuscopio_activado"] = False
        regla = self.tabla_mapeo.get(clave)
        if regla:
            # MÉTRICA: registrar regla usada
            if hasattr(self, "simulacion"):
                self.simulacion.metricas["reglas_usadas"].add(id(regla))
            return {"accion": regla["accion"], "param": regla.get("param", percepcion["monstroscopio"][2]),
                    "razon": regla["razon"]}
        return {"accion": "PROPULSOR", "param": percepcion["monstroscopio"][2], "razon": "accion_por_defecto"}

    def ejecutar_accion(self, accion: str, param: Optional[str], entorno: Any, monstruos: List[Any]) -> Dict[str, Any]:
        """Ejecuta el efector correspondiente (propulsor, reorientador o vacuumator)."""
        if accion == "PROPULSOR":
            return self._propulsor(entorno)
        if accion == "REORIENTADOR":
            return self._reorientador(param or "+90")
        if accion == "VACUUMATOR":
            return self._vacuumator(entorno, monstruos)
        return {"exito": False, "razon": "accion_no_reconocida", "resultado": {}}

    # -------------------------------------------------------------------------
    # EFECTORES
    # -------------------------------------------------------------------------
    def _propulsor(self, entorno: Any) -> Dict[str, Any]:
        """Avanza hacia adelante según la orientación; activa Vacuscopio si choca."""
        dx, dy, dz = _ORIENTACIONES[self.orientacion]
        nx, ny, nz = self.x + dx, self.y + dy, self.z + dz
        tipo = entorno.obtener_tipo_celda(nx, ny, nz)
        # MÉTRICA
        if hasattr(entorno, "simulacion"):
            entorno.simulacion.metricas["acciones"]["avances"] += 1
        if tipo == entorno.ZONA_LIBRE:
            self.memoria['posicion_anterior'] = (self.x, self.y, self.z)
            self.x, self.y, self.z = nx, ny, nz
            self.memoria['vacuscopio_activado'] = False
            return {"accion": "PROPULSOR", "exito": True, "razon": "avance_exitoso"}
        else:
            # MÉTRICA: colisión
            if hasattr(entorno, "simulacion"):
                entorno.simulacion.metricas["colisiones"] += 1
                if not entorno.simulacion.metricas["primer_vacuumator"]:
                    entorno.simulacion.metricas["colisiones_pre_primera_caza"] += 1
            self.memoria['vacuscopio_activado'] = True
            return {"accion": "PROPULSOR", "exito": False, "resultado": {"colision": True},
                    "razon": "colision_con_pared"}

    def _reorientador(self, sentido: str = '+90') -> Dict[str, Any]:
        """Gira 90° o se alinea a una dirección específica."""
        if hasattr(self, "simulacion"):
            self.simulacion.metricas["acciones"]["rotaciones"] += 1  # MÉTRICA
        if sentido in _ORIENTACIONES:
            self.orientacion = sentido
            return {"accion": "REORIENTADOR", "exito": True, "razon": "alineacion_directa"}
        if self.orientacion not in _ORIENTACIONES_CICLICAS:
            self.orientacion = '+X'
        i = _ORIENTACIONES_CICLICAS.index(self.orientacion)
        self.orientacion = _ORIENTACIONES_CICLICAS[(i + 1) % 4] if sentido == '+90' else _ORIENTACIONES_CICLICAS[
            (i - 1) % 4]
        return {"accion": "REORIENTADOR", "exito": True, "razon": "rotacion_lateral"}

    def _vacuumator(self, entorno: Any, monstruos: List[Any]) -> Dict[str, Any]:
        """Destruye monstruos en la celda actual y se autodestruye."""
        eliminados = [m for m in monstruos if (m.x, m.y, m.z) == (self.x, self.y, self.z)]
        for m in eliminados:
            entorno.eliminar_monstruo(m.id)
        entorno.eliminar_robot(self.id)
        entorno.grid[self.x, self.y, self.z] = entorno.ZONA_VACIA
        # MÉTRICA
        if hasattr(entorno, "simulacion"):
            entorno.simulacion.metricas["acciones"]["vacuumator"] += 1
            entorno.simulacion.metricas["monstruos_destruidos"] += len(eliminados)
            if len(eliminados) > 0:
                entorno.simulacion.metricas["primer_vacuumator"] = True
        return {"accion": "VACUUMATOR", "exito": bool(eliminados), "razon": "autodestruccion_si_exitoso"}

    # -------------------------------------------------------------------------
    # CICLO DE VIDA
    # -------------------------------------------------------------------------
    def percibir_decidir_actuar(self, t: int, entorno: Any) -> Dict[str, Any]:
        """Ejecuta un ciclo completo: percepción, decisión y acción, con evasión de bucles."""
        percepcion = self.percibir(entorno.robots, entorno.monstruos)
        decision = self.decidir_accion(percepcion)
        accion, param = decision["accion"], decision["param"]
        self.actualizar_memoria(t, percepcion, accion)
        evento = self.ejecutar_accion(accion, param, entorno, entorno.monstruos)

        bucle = self.detectar_bucle()
        if bucle:
            longitud, repeticiones = bucle
            if repeticiones >= 2:
                self._evadir_bucle(entorno)

        return {"accion": accion, "exito": evento.get("exito", False), "razon": evento.get("razon", decision["razon"])}

    # -------------------------------------------------------------------------
    # MEMORIA Y BUCLES
    # -------------------------------------------------------------------------
    def actualizar_memoria(self, t: int, percepcion: Dict[str, Any], accion: str) -> None:
        """Guarda percepciones y acciones en la memoria simbólica."""
        self.memoria['historial'].append({
            't': t,
            'p': {
                'ori': percepcion.get('giroscopio'),
                'E': percepcion.get('energometro', False),
                'R': percepcion.get('roboscanner', False),
                'M': bool(percepcion.get('monstroscopio')),
                'V': percepcion.get('vacuscopio', False),
                'pos_prev': percepcion.get('posicion_anterior'),
            },
            'a': accion
        })

    def detectar_bucle(self, min_len: int = 2, min_repeticiones: int = 2) -> Optional[Tuple[int, int]]:
        """Detecta repeticiones consecutivas de patrones de percepción–acción."""
        historial = self.memoria.get('historial', [])
        n = len(historial)
        if n < min_len * min_repeticiones:
            return None
        secuencia = [(tuple(sorted(h['p'].items())), h['a']) for h in historial]
        for l in range(min_len, n // min_repeticiones + 1):
            patron = secuencia[-l:]
            repeticiones = 1
            for i in range(2, min_repeticiones + 3):
                if n - i * l < 0:
                    break
                if patron == secuencia[-i * l:-(i - 1) * l]:
                    repeticiones += 1
                else:
                    break
            if repeticiones >= min_repeticiones:
                if hasattr(self, "simulacion"):
                    self.simulacion.metricas["bucles_detectados"] += 1  # MÉTRICA
                return l, repeticiones
        return None

    def _evadir_bucle(self, entorno: Any) -> None:
        """Cambia orientación y movimiento si se detecta un bucle conductual."""
        opuestas = {"+X": "-X", "-X": "+X", "+Y": "-Y", "-Y": "+Y", "+Z": "-Z", "-Z": "+Z"}
        historial = self.memoria.get('historial', [])[-6:]
        ultimas_oris = [h["p"]["ori"] for h in historial if "p" in h and "ori" in h["p"]]

        orientaciones_filtradas = [
                                      o for o in _ORIENTACIONES.keys()
                                      if o not in (self.orientacion,
                                                   opuestas.get(self.orientacion)) and o not in ultimas_oris
                                  ] or [
                                      o for o in _ORIENTACIONES.keys()
                                      if o not in (self.orientacion, opuestas.get(self.orientacion))
                                  ]
        nueva_dir = random.choice(orientaciones_filtradas)
        self._reorientador(nueva_dir)
        if random.random() < 0.4:
            self._propulsor(entorno)

    def __repr__(self) -> str:
        """Representación simplificada del robot."""
        return f"<AgenteRacionalRobot id={self.id} pos=({self.x},{self.y},{self.z}) ori={self.orientacion}>"
