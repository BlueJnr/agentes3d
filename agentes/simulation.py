# simulation.py
import random
import time
from typing import Tuple

from agentes.agent_monster import AgenteReflejoMonstruo
from agentes.agent_robot import AgenteRacionalRobot
from agentes.environment import EntornoOperacion


class SimulacionEnergetica:
    """
    Motor principal de simulación dentro del Entorno de Operación Energético.

    Coordina la interacción entre el Entorno y los agentes energéticos
    (robots racionales y monstruos reflejo).
    Cada ciclo temporal representa una transición del sistema energético.
    """

    def __init__(
            self,
            N: int = 6,
            Nrobots: int = 2,
            Nmonstruos: int = 2,
            ticks: int = 15,
            K_monstruo: int = 3,
            seed: int | None = None
    ) -> None:
        """
        Inicializa la simulación configurando el Entorno de Operación
        y creando las entidades energéticas.

        Args:
            N: Tamaño del lado del entorno cúbico (N×N×N).
            Nrobots: Número de robots racionales.
            Nmonstruos: Número de monstruos reflejo.
            ticks: Número total de ciclos de simulación.
            K_monstruo: Frecuencia de activación de los monstruos reflejo.
            seed: Semilla para reproducibilidad.
        """
        self.N = N
        self.Nrobots = Nrobots
        self.Nmonstruos = Nmonstruos
        self.ticks = ticks
        self.K_monstruo = K_monstruo

        # Inicializa el entorno de operación energético
        self.entorno = EntornoOperacion(N=N, Psoft=0.2, Pfree=0.8, seed=seed)
        self._inicializar_agentes()

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN INICIAL
    # -------------------------------------------------------------------------
    def _inicializar_agentes(self) -> None:
        """
        Crea y posiciona los agentes energéticos (robots y monstruos)
        en Zonas Libres aleatorias dentro del Entorno de Operación.
        """
        # Robots racionales
        for i in range(self.Nrobots):
            while True:
                x, y, z = self._posicion_aleatoria()
                robot = AgenteRacionalRobot(id=i + 1, x=x, y=y, z=z)
                if self.entorno.registrar_robot(robot):
                    break

        # Monstruos reflejo
        for i in range(self.Nmonstruos):
            while True:
                x, y, z = self._posicion_aleatoria()
                monstruo = AgenteReflejoMonstruo(id=i + 1, x=x, y=y, z=z)
                if self.entorno.registrar_monstruo(monstruo):
                    break

    def _posicion_aleatoria(self) -> Tuple[int, int, int]:
        """Genera una posición aleatoria dentro de los límites del entorno."""
        return (
            random.randint(0, self.N - 1),
            random.randint(0, self.N - 1),
            random.randint(0, self.N - 1)
        )

    # -------------------------------------------------------------------------
    # MOTOR DE SIMULACIÓN
    # -------------------------------------------------------------------------
    def ejecutar(self, delay: float = 0.5) -> None:
        """
        Ejecuta el ciclo principal de la simulación energética.

        En cada ciclo:
          - Los monstruos reflejo actúan cada K_monstruo ciclos.
          - Los robots racionales perciben, deciden y actúan.
          - Se visualiza una capa del Entorno de Operación.

        Args:
            delay: Tiempo (segundos) de espera entre ticks.
        """
        print(f"\n⚡ Iniciando Simulación Energética (N={self.N})")
        print(f"   Robots: {len(self.entorno.robots)} | Monstruos: {len(self.entorno.monstruos)}\n")

        for t in range(self.ticks):
            print(f"\n=== Ciclo Energético {t} ===")

            # --- Monstruos reflejo ---
            for monstruo in list(self.entorno.monstruos):
                evento = monstruo.percibir_decidir_actuar(
                    t, self.entorno, self.K_monstruo
                )

                if evento.get("se_movio", False):
                    print(f"👾 Monstruo {monstruo.id} → {evento['accion']} hacia {evento['nueva_pos']}")
                else:
                    print(f"👾 Monstruo {monstruo.id} permanece inactivo en {evento['nueva_pos']}")

            # --- Robots racionales ---
            for robot in list(self.entorno.robots):
                evento = robot.percibir_decidir_actuar(
                    t, self.entorno, self.entorno.robots, self.entorno.monstruos
                )
                accion = evento.get("accion", "?")
                print(f"🤖 Robot {robot.id} → {accion} (orientación: {robot.orientacion})")

            # --- Visualización del entorno energético ---
            self.entorno.visualizar_capa(self.N // 2)
            time.sleep(delay)

        print("\n✅ Simulación Energética finalizada.")

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """Representación textual de la simulación energética."""
        return (
            f"<SimulacionEnergetica N={self.N}, Robots={len(self.entorno.robots)}, "
            f"Monstruos={len(self.entorno.monstruos)}, Ticks={self.ticks}>"
        )
