# simulation.py
import random
import time
from typing import Tuple

from agentes.agent_monster import AgenteReflejoMonstruo
from agentes.agent_robot import AgenteRacionalRobot
from agentes.environment import EntornoOperacion
from agentes.visual_3d_manual import Visualizador3DManual


class SimulacionEnergetica:
    """
    Motor principal de simulación dentro del **Entorno de Operación Energético**.

    Este componente coordina la interacción entre:
      • Los **Agentes Energéticos** (monstruos reflejo).
      • Los **Agentes Materiales** (robots racionales).
      • El **Entorno de Operación Energético** (espacio tridimensional N³).

    Cada iteración representa un **Ciclo Energético**, durante el cual:
      - Los monstruos reflejo se activan de forma periódica (cada K ciclos).
      - Los robots racionales perciben, deciden y actúan en consecuencia.
      - Se actualiza la topología del entorno y se visualiza su estado parcial.

    Este motor constituye la capa de control de alto nivel que gestiona
    la dinámica completa del sistema energético.
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
        Inicializa la simulación configurando el **Entorno de Operación Energético**
        y creando las entidades energéticas (robots racionales y monstruos reflejo).

        Args:
            N (int): Tamaño del lado del entorno cúbico (N×N×N).
            Nrobots (int): Número de robots racionales a generar.
            Nmonstruos (int): Número de monstruos reflejo a generar.
            ticks (int): Duración total de la simulación (número de ciclos energéticos).
            K_monstruo (int): Frecuencia de activación de los monstruos reflejo.
            seed (Optional[int]): Semilla opcional para reproducibilidad.
        """
        self.N = N
        self.Nrobots = Nrobots
        self.Nmonstruos = Nmonstruos
        self.ticks = ticks
        self.K_monstruo = K_monstruo

        # Entorno de Operación Energético inicial
        self.entorno = EntornoOperacion(N=N, Psoft=0.2, Pfree=0.8, seed=seed)
        self._inicializar_agentes()

    # -------------------------------------------------------------------------
    # CONFIGURACIÓN INICIAL
    # -------------------------------------------------------------------------
    def _inicializar_agentes(self) -> None:
        """
        Crea y posiciona los **Agentes Energéticos** y **Materiales** dentro del entorno.

        Este método cumple las reglas de distribución de entidades según los requisitos:
          - Los **Robots Racionales** se ubican en Zonas Libres aleatorias.
          - Los **Monstruos Reflejo** se ubican también en Zonas Libres distintas.
          - Ambos pueden coexistir en la misma celda, pero no con agentes del mismo tipo.
        """
        # Robots racionales (Agentes Materiales)
        for i in range(self.Nrobots):
            while True:
                x, y, z = self._posicion_aleatoria()
                robot = AgenteRacionalRobot(id=i + 1, x=x, y=y, z=z)
                if self.entorno.registrar_robot(robot):
                    break

        # Monstruos reflejo (Agentes Energéticos)
        for i in range(self.Nmonstruos):
            while True:
                x, y, z = self._posicion_aleatoria()
                monstruo = AgenteReflejoMonstruo(id=i + 1, x=x, y=y, z=z)
                if self.entorno.registrar_monstruo(monstruo):
                    break

    def _posicion_aleatoria(self) -> Tuple[int, int, int]:
        """
        Genera una posición aleatoria válida dentro del volumen energético N³.

        Returns:
            Tuple[int, int, int]: Coordenadas (x, y, z) dentro de los límites del entorno.
        """
        return (
            random.randint(0, self.N - 1),
            random.randint(0, self.N - 1),
            random.randint(0, self.N - 1)
        )

    def ejecutar_manual_3d(self):
        """
        Ejecuta la simulación en modo 3D manual:
        - El usuario controla cuándo avanza cada tick.
        - Se muestra un cubo transparente en OpenGL.
        """
        print("🧊 Iniciando simulación 3D manual...")
        vis = Visualizador3DManual(self)
        vis.iniciar()

    # -------------------------------------------------------------------------
    # MOTOR DE SIMULACIÓN
    # -------------------------------------------------------------------------
    def ejecutar(self, delay: float = 0.5) -> None:
        """
        Ejecuta el **Ciclo Energético Principal** de la simulación.

        En cada ciclo del sistema energético:
          1. Los **Monstruos Reflejo** ejecutan su ciclo `percibir_decidir_actuar()`
             con frecuencia K_monstruo.
          2. Los **Robots Racionales** perciben, deciden y actúan de forma racional.
          3. Se actualiza la **Capa Energética** visual del entorno.
          4. Se respeta un retardo temporal (`delay`) entre ciclos.

        Args:
            delay (float): Tiempo (en segundos) de pausa entre ciclos energéticos.
        """
        print(f"\n{'=' * 70}")
        print(f"⚡ INICIO DE SIMULACIÓN ENERGÉTICA 3D")
        print(f"{'-' * 70}")
        print(f"📦 Tamaño del entorno: {self.N}x{self.N}x{self.N}")
        print(f"🤖 Robots: {len(self.entorno.robots)} | 👾 Monstruos: {len(self.entorno.monstruos)}")
        print(f"🔁 Ciclos configurados: {self.ticks} | Frecuencia monstruo K={self.K_monstruo}")
        print(f"{'=' * 70}\n")

        for t in range(self.ticks):
            print(f"\n{'-' * 60}")
            print(f"⚙️  [Ciclo Energético {t}]")
            print(f"{'-' * 60}")

            # --- Activación de los agentes energéticos (monstruos reflejo) ---
            print("👾 MONSTRUOS REFLEJO:")
            for monstruo in list(self.entorno.monstruos):
                evento = monstruo.percibir_decidir_actuar(t, self.entorno, self.K_monstruo)
                accion = evento.get("accion", "N/A")
                exito = evento.get("exito", False)
                razon = evento.get("razon", "")

                if exito:
                    print(
                        f"  ✅ [Monstruo {monstruo.id}] Acción: {accion:<10} → Nueva posición: ({monstruo.x}, {monstruo.y}, {monstruo.z})")
                else:
                    print(f"  💤 [Monstruo {monstruo.id}] Inactivo → {razon}")

            # --- Activación de los agentes materiales (robots racionales) ---
            print("\n🤖 ROBOTS RACIONALES:")
            for robot in list(self.entorno.robots):
                evento = robot.percibir_decidir_actuar(t, self.entorno, self.entorno.robots, self.entorno.monstruos)
                accion = evento.get("accion", "?")
                exito = evento.get("exito", False)
                razon = evento.get("razon", "sin motivo")
                orient = getattr(robot, "orientacion", "?")

                estado = "✅ Éxito" if exito else "⚠️ Fallo"
                print(f"  🤖 [Robot {robot.id}] {accion:<12} | {estado:<10} | Regla: {razon:<35} | Ori: {orient}")

                # Autodestrucción por uso del Vacuumator
                if accion == "VACUUMATOR" and exito:
                    print(f"     💥 [Robot {robot.id}] se autodestruye tras activar Vacuumator.")
                    self.entorno.eliminar_robot(robot.id)
                    break  # salir del loop para evitar iterar sobre lista modificada

            # --- Visualización del entorno en capa central ---
            print(f"\n🧩 Visualizando capa central (z={self.N // 2}) del entorno...")
            self.entorno.visualizar_capa(self.N // 2)

            print(f"✅ [Ciclo {t}] completado.\n")
            time.sleep(delay)

        print(f"\n{'=' * 70}")
        print("🏁 SIMULACIÓN ENERGÉTICA FINALIZADA CON ÉXITO.")
        print(f"{'=' * 70}\n")

    # -------------------------------------------------------------------------
    # REPRESENTACIÓN
    # -------------------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Retorna una representación textual de la configuración de la simulación.

        Returns:
            str: Descripción con tamaño del entorno, número de agentes y duración.
        """
        return (
            f"<SimulacionEnergetica N={self.N}, Robots={len(self.entorno.robots)}, "
            f"Monstruos={len(self.entorno.monstruos)}, Ticks={self.ticks}>"
        )
