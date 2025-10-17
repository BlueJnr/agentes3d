# simulation.py
import random
import time
from typing import Tuple

from agent_monster import AgenteMonstruo
from jhunior.agent_robot import AgenteRobot
from john.environmet import Entorno3D


class Simulacion:
    """
    Motor principal de simulación de agentes en un entorno tridimensional.

    Coordina la interacción entre el entorno y los agentes.
    En cada tick temporal, los agentes (robots y monstruos)
    ejecutan su ciclo de percepción, decisión y acción.
    """

    def __init__(
            self,
            N: int = 6,
            n_robots: int = 2,
            n_monstruos: int = 2,
            ticks: int = 15,
            K_monstruo: int = 3,
            seed: int | None = None
    ) -> None:
        """
        Inicializa la simulación configurando el entorno y creando los agentes.

        Args:
            N: Dimensión del entorno cúbico (N×N×N).
            n_robots: Número de robots iniciales.
            n_monstruos: Número de monstruos iniciales.
            ticks: Número total de pasos de simulación.
            K_monstruo: Frecuencia de activación de los monstruos.
            seed: Semilla para reproducibilidad.
        """
        self.N = N
        self.n_robots = n_robots
        self.n_monstruos = n_monstruos
        self.ticks = ticks
        self.K_monstruo = K_monstruo

        self.entorno = Entorno3D(N=N, p_vacia=0.2, seed=seed)
        self._inicializar_agentes()

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN INICIAL
    # -------------------------------------------------------------------------
    def _inicializar_agentes(self) -> None:
        """
        Crea y ubica los robots y monstruos en posiciones aleatorias válidas.
        """
        # Inicialización de robots
        for i in range(self.n_robots):
            while True:
                x, y, z = self._random_posicion()
                robot = AgenteRobot(id=i + 1, x=x, y=y, z=z)
                if self.entorno.registrar_robot(robot):
                    break

        # Inicialización de monstruos
        for i in range(self.n_monstruos):
            while True:
                x, y, z = self._random_posicion()
                monstruo = AgenteMonstruo(id=i + 1, x=x, y=y, z=z)
                if self.entorno.registrar_monstruo(monstruo):
                    break

    def _random_posicion(self) -> Tuple[int, int, int]:
        """
        Devuelve una posición aleatoria válida dentro de los límites del entorno.
        """
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
        Ejecuta el bucle principal de la simulación.

        En cada tick:
            - Los monstruos actúan según su frecuencia K_monstruo.
            - Los robots perciben, deciden y actúan racionalmente.
            - Se visualiza una capa intermedia del entorno.

        Args:
            delay: Tiempo (segundos) de espera entre ticks.
        """
        print(f"\n🚀 Iniciando simulación en entorno {self.N}³")
        print(f"   Robots activos: {len(self.entorno.robots)} | Monstruos activos: {len(self.entorno.monstruos)}\n")

        for t in range(self.ticks):
            print(f"\n=== Tick {t} ===")

            # --- Turno de monstruos ---
            for monstruo in list(self.entorno.monstruos):
                evento = monstruo.decide_and_act(
                    t, self.entorno, self.entorno.robots, self.entorno.monstruos, self.K_monstruo
                )
                if evento["moved"]:
                    print(f"👾 Monstruo {monstruo.id} → {evento['action']} hacia {evento['new_pos']}")

            # --- Turno de robots ---
            for robot in list(self.entorno.robots):
                evento = robot.decide_and_act(t, self.entorno, self.entorno.robots, self.entorno.monstruos)
                print(f"🤖 Robot {robot.id} → {evento['action']} (orientación: {robot.orientation})")

            # --- Visualización parcial ---
            self.entorno.visualizar_capa(self.N // 2)
            time.sleep(delay)

        print("\n✅ Simulación finalizada.")

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """Representación textual de la simulación actual."""
        return (
            f"<Simulacion N={self.N}, robots={len(self.entorno.robots)}, "
            f"monstruos={len(self.entorno.monstruos)}, ticks={self.ticks}>"
        )


if __name__ == "__main__":
    sim = Simulacion(N=6, n_robots=2, n_monstruos=2, ticks=10, K_monstruo=3, seed=42)
    sim.ejecutar(delay=0.2)
