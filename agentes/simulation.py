# simulation.py
import random
import time
from typing import Tuple

from agentes.agent_monster import AgenteReflejoMonstruo
from agentes.agent_robot import AgenteRacionalRobot
from agentes.environment import EntornoOperacion
from agentes.visual_3d_manual import Visualizador3DManual


class SimulacionEnergetica:
    """Motor principal que coordina la interacción entre entorno, robots y monstruos."""

    def __init__(
            self,
            N: int = 6,
            Nrobots: int = 2,
            Nmonstruos: int = 2,
            ticks: int = 15,
            K_monstruo: int = 3,
            seed: int | None = None,
            Pfree: float = 0.8,
            Psoft: float = 0.2,
            p_movimiento: float = 0.7
    ) -> None:
        """Inicializa el entorno y crea los agentes energéticos y materiales."""
        self.N = N
        self.Nrobots = Nrobots
        self.Nmonstruos = Nmonstruos
        self.ticks = ticks
        self.K_monstruo = K_monstruo
        self.Pfree = Pfree
        self.Psoft = Psoft
        self.p_movimiento = p_movimiento
        self.seed = seed

        self.entorno = EntornoOperacion(N=N, Psoft=Psoft, Pfree=Pfree, seed=seed)
        self.entorno.simulacion = self  # vínculo circular controlado

        # Registro de métricas
        self.metricas = {
            "reglas_usadas": set(),
            "acciones": {"avances": 0, "rotaciones": 0, "vacuumator": 0},
            "colisiones": 0,
            "colisiones_pre_primera_caza": 0,
            "bucles_detectados": 0,
            "exitos_totales": 0,
            "acciones_totales": 0,
            "monstruos_destruidos": 0,
            "posiciones_iniciales": {},
            "posiciones_finales": {},
            "ticks_totales": 0,
            "primer_vacuumator": False,
            "tiempo_total": 0.0,
        }

        self._inicializar_agentes()

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN INICIAL
    # -------------------------------------------------------------------------
    def _inicializar_agentes(self) -> None:
        """Crea y posiciona robots y monstruos en Zonas Libres aleatorias."""
        for i in range(self.Nrobots):
            while True:
                x, y, z = self._posicion_aleatoria()
                robot = AgenteRacionalRobot(id=i + 1, x=x, y=y, z=z)
                robot.simulacion = self  # para registrar métricas
                if self.entorno.registrar_robot(robot):
                    self.metricas["posiciones_iniciales"][f"robot_{i + 1}"] = (x, y, z)
                    break

        for i in range(self.Nmonstruos):
            while True:
                x, y, z = self._posicion_aleatoria()
                monstruo = AgenteReflejoMonstruo(id=i + 1, x=x, y=y, z=z, p_movimiento=self.p_movimiento)
                monstruo.simulacion = self
                if self.entorno.registrar_monstruo(monstruo):
                    break

    def _posicion_aleatoria(self) -> Tuple[int, int, int]:
        """Devuelve una posición aleatoria válida dentro del entorno N³."""
        return (
            random.randint(0, self.N - 1),
            random.randint(0, self.N - 1),
            random.randint(0, self.N - 1)
        )

    def ejecutar_manual_3d(self) -> None:
        """Ejecuta la simulación en modo 3D manual controlado por el usuario."""
        print("🧊 Iniciando simulación 3D manual...")
        vis = Visualizador3DManual(self)
        vis.iniciar()

    # -------------------------------------------------------------------------
    # MOTOR DE SIMULACIÓN
    # -------------------------------------------------------------------------
    def ejecutar(self, delay: float = 0.0) -> None:
        """Ejecuta el ciclo energético principal de la simulación (modo silencioso)."""

        # ------------------------------------------------------------
        # ENCABEZADO INICIAL: parámetros configurables
        # ------------------------------------------------------------
        print(f"\n{'=' * 70}")
        print("⚡ SIMULACIÓN ENERGÉTICA 3D - PARÁMETROS INICIALES")
        print(f"{'=' * 70}")
        print(f"📦 Tamaño del entorno (N³): {self.N}x{self.N}x{self.N}")
        print(f"🤖 Robots racionales: {self.Nrobots}")
        print(f"👾 Monstruos reflejo: {self.Nmonstruos}")
        print(f"🔁 Ciclos totales: {self.ticks}")
        print(f"⏱️ Frecuencia de monstruos (K): {self.K_monstruo}")
        print(f"🌱 Semilla aleatoria: {self.seed}")
        print(f"🟩 Proporción zonas libres (Pfree): {self.Pfree}")
        print(f"⬛ Proporción zonas vacías (Psoft): {self.Psoft}")
        print(f"👣 Probabilidad movimiento monstruos: {self.p_movimiento}")
        print(f"{'=' * 70}\n")

        tiempo_inicio = time.perf_counter()

        # ------------------------------------------------------------
        # CICLO PRINCIPAL
        # ------------------------------------------------------------
        for t in range(self.ticks):
            # Monstruos reflejo activos
            for monstruo in [m for m in self.entorno.monstruos if getattr(m, "activo", True)]:
                monstruo.percibir_decidir_actuar(t, self.entorno, self.K_monstruo)

            # Robots racionales activos
            for robot in [r for r in self.entorno.robots if getattr(r, "activo", True)]:
                evento = robot.percibir_decidir_actuar(t, self.entorno)
                self.metricas["acciones_totales"] += 1
                if evento.get("exito", False):
                    self.metricas["exitos_totales"] += 1

            # Fin anticipado si no quedan agentes activos
            if not any(getattr(r, "activo", False) for r in self.entorno.robots) and \
                    not any(getattr(m, "activo", False) for m in self.entorno.monstruos):
                break

            time.sleep(delay)

        # ------------------------------------------------------------
        # FINALIZACIÓN Y CÁLCULOS
        # ------------------------------------------------------------
        self.metricas["tiempo_total"] = time.perf_counter() - tiempo_inicio
        self.metricas["ticks_totales"] = t + 1

        # Guardar posiciones finales
        for r in self.entorno.robots:
            self.metricas["posiciones_finales"][f"robot_{r.id}"] = (r.x, r.y, r.z)

        # ------------------------------------------------------------
        # MOSTRAR ESTADÍSTICAS
        # ------------------------------------------------------------
        self._mostrar_estadisticas()

    # -------------------------------------------------------------------------
    # ESTADÍSTICAS Y MÉTRICAS
    # -------------------------------------------------------------------------
    def _mostrar_estadisticas(self):
        """Muestra en consola las métricas detalladas de desempeño del agente."""
        m = self.metricas
        print(f"\n{'=' * 70}")
        print("📊 ESTADÍSTICAS FINALES")
        print(f"{'=' * 70}")
        print(f"Reglas usadas (distintas): {len(m['reglas_usadas'])}")
        print(f"Avances ejecutados: {m['acciones']['avances']}")
        print(f"Rotaciones ejecutadas: {m['acciones']['rotaciones']}")
        print(f"Vacuumator activado: {m['acciones']['vacuumator']}")
        print(f"Colisiones totales: {m['colisiones']}")
        print(f"Colisiones antes de primera caza: {m['colisiones_pre_primera_caza']}")
        print(f"Bucles detectados: {m['bucles_detectados']}")
        print(f"Ticks totales: {m['ticks_totales']}")
        print(f"Tiempo total de simulación: {m['tiempo_total']:.3f} s")

        # ---------------------------------------------------------------------
        # MÉTRICAS DERIVADAS
        # ---------------------------------------------------------------------
        acciones_totales = max(1, m["acciones_totales"])
        monstruos_totales = max(1, self.Nmonstruos)

        # Cálculos base
        m["tasa_colision"] = m["colisiones"] / acciones_totales
        m["porc_efectividad"] = (m["monstruos_destruidos"] / monstruos_totales) * 100
        m["complejidad"] = m["acciones_totales"] + len(m["reglas_usadas"]) + m["bucles_detectados"]
        m["tiempo_medio_ciclo"] = m["tiempo_total"] / max(1, m["ticks_totales"])

        # ---------------------------------------------------------------------
        # RACIONALIDAD (mejorada)
        # ---------------------------------------------------------------------
        # Ponderaciones (puedes ajustarlas)
        alpha, beta, lamb = 0.5, 0.3, 0.2

        md = m["monstruos_destruidos"]
        mt = monstruos_totales
        ae = m["exitos_totales"]
        at = acciones_totales
        bd = m["bucles_detectados"]

        # Cálculo de racionalidad ponderada
        m["racionalidad"] = (alpha * (md / mt)) + (beta * (ae / at)) - (lamb * (bd / at))

        # ---------------------------------------------------------------------
        # SALIDA FINAL
        # ---------------------------------------------------------------------
        print("\n🔢 MÉTRICAS DERIVADAS:")
        print(f"→ Complejidad del agente: {m['complejidad']}")
        print(
            f"→ Porcentaje de efectividad: {m['porc_efectividad']:.1f}% ({m['monstruos_destruidos']}/{self.Nmonstruos})")
        print(f"→ Tasa de colisión: {m['tasa_colision']:.3f}")
        print(f"→ Tiempo medio por ciclo: {m['tiempo_medio_ciclo']:.4f} s")
        print(f"→ Desempeño (racionalidad): {m['racionalidad']:.3f}")

        for rid, pos_final in m["posiciones_finales"].items():
            pos_ini = m["posiciones_iniciales"].get(rid)
            print(f"¿{rid} retorna a posición inicial? {'Sí' if pos_ini == pos_final else 'No'}")

        print(f"{'=' * 70}\n")

    def __repr__(self) -> str:
        """Retorna una representación textual de la configuración de la simulación."""
        return (
            f"<SimulacionEnergetica N={self.N}, Robots={len(self.entorno.robots)}, "
            f"Monstruos={len(self.entorno.monstruos)}, Ticks={self.ticks}>"
        )
