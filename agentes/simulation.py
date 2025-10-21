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
                if self.entorno.registrar_robot(robot):
                    break

        for i in range(self.Nmonstruos):
            while True:
                x, y, z = self._posicion_aleatoria()
                monstruo = AgenteReflejoMonstruo(id=i + 1, x=x, y=y, z=z, p_movimiento=self.p_movimiento)
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
    def ejecutar(self, delay: float = 0.5) -> None:
        """Ejecuta el ciclo energético principal de la simulación."""
        print(f"\n{'=' * 70}")
        print("⚡ INICIO DE SIMULACIÓN ENERGÉTICA 3D")
        print(f"{'-' * 70}")
        print(f"📦 Tamaño del entorno: {self.N}x{self.N}x{self.N}")
        print(f"🤖 Robots: {len(self.entorno.robots)} | 👾 Monstruos: {len(self.entorno.monstruos)}")
        print(f"🔁 Ciclos: {self.ticks} | Frecuencia monstruo K={self.K_monstruo}")
        print(f"{'=' * 70}\n")

        for t in range(self.ticks):
            print(f"\n{'-' * 60}")
            print(f"⚙️  [Ciclo Energético {t}]")
            print(f"{'-' * 60}")

            # Monstruos reflejo (solo activos)
            print("👾 MONSTRUOS REFLEJO:")
            for monstruo in [m for m in self.entorno.monstruos if getattr(m, "activo", True)]:
                evento = monstruo.percibir_decidir_actuar(t, self.entorno, self.K_monstruo)
                accion = evento.get("accion", "N/A")
                exito = evento.get("exito", False)
                razon = evento.get("razon", "")
                if exito:
                    print(
                        f"  ✅ [Monstruo {monstruo.id}] Acción: {accion:<10} "
                        f"→ Nueva posición: ({monstruo.x}, {monstruo.y}, {monstruo.z})"
                    )
                else:
                    print(f"  💤 [Monstruo {monstruo.id}] Inactivo → {razon}")

            # Robots racionales (solo activos)
            print("\n🤖 ROBOTS RACIONALES:")
            for robot in [r for r in self.entorno.robots if getattr(r, "activo", True)]:
                evento = robot.percibir_decidir_actuar(t, self.entorno)
                accion = evento.get("accion", "?")
                exito = evento.get("exito", False)
                razon = evento.get("razon", "sin motivo")
                orient = getattr(robot, "orientacion", "?")

                estado = "✅ Éxito" if exito else "⚠️ Fallo"
                print(f"  🤖 [Robot {robot.id}] {accion:<12} | {estado:<10} | Regla: {razon:<35} | Ori: {orient}")

                if accion == "VACUUMATOR" and exito:
                    print(f"     💥 [Robot {robot.id}] se autodestruye tras activar Vacuumator.")

            # Si no quedan agentes activos, termina
            if not any(getattr(r, "activo", False) for r in self.entorno.robots) and \
                    not any(getattr(m, "activo", False) for m in self.entorno.monstruos):
                print("\n🏁 No quedan agentes activos. Fin anticipado de la simulación.")
                break

            # Visualización
            print(f"\n🧩 Visualizando capa central (z={self.N // 2}) del entorno...")
            self.entorno.visualizar_capa(self.N // 2)
            print(f"✅ [Ciclo {t}] completado.\n")
            time.sleep(delay)

        print(f"\n{'=' * 70}")
        print("🏁 SIMULACIÓN ENERGÉTICA FINALIZADA.")
        print(f"{'=' * 70}\n")

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """Retorna una representación textual de la configuración de la simulación."""
        return (
            f"<SimulacionEnergetica N={self.N}, Robots={len(self.entorno.robots)}, "
            f"Monstruos={len(self.entorno.monstruos)}, Ticks={self.ticks}>"
        )
