# environment.py
import random
from typing import List, Any, Optional

import numpy as np


class EntornoOperacion:
    """
    Representa el **Entorno de Operación Energético tridimensional (N³)** donde
    interactúan las entidades materiales (robots racionales) y energéticas (monstruos reflejo).

    Este entorno constituye un **hexaedro regular** compuesto por cubos discretos
    denominados **Zonas**, de dos tipos:

      - **Zona Libre (Pfree)**: regiones transitables donde pueden ubicarse o moverse
        los agentes materiales o energéticos.
      - **Zona Vacía (Psoft)**: regiones energéticas bloqueadas, no transitables ni
        atravesables por ningún tipo de agente.

    Según los requisitos:
      • El entorno está completamente rodeado por una **capa exterior de Zonas Vacías**
        imposible de atravesar.
      • Su estructura y contenido se generan **aleatoriamente** en cada ejecución.
      • Administra la posición, registro y eliminación de entidades activas.
    """

    ZONA_LIBRE = 0
    ZONA_VACIA = 1

    def __init__(
            self,
            N: int = 5,
            Pfree: float = 0.8,
            Psoft: float = 0.2,
            seed: Optional[int] = None
    ) -> None:
        """
        Inicializa el entorno energético tridimensional (N×N×N).

        Args:
            N (int): Tamaño del lado del cubo energético (cantidad de celdas por eje).
            Pfree (float): Porcentaje esperado de Zonas Libres dentro del volumen total.
            Psoft (float): Porcentaje esperado de Zonas Vacías (bloqueadas o intransitables).
            seed (Optional[int]): Semilla aleatoria opcional para reproducibilidad del entorno.

        Atributos:
            - `grid`: matriz cúbica N×N×N que almacena el tipo de zona en cada celda.
            - `robots`: lista de robots racionales registrados en el entorno.
            - `monstruos`: lista de monstruos reflejo registrados.
        """
        self.N = N
        self.Pfree = Pfree
        self.Psoft = Psoft

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Malla cúbica que representa las Zonas del entorno energético
        self.grid = np.zeros((N, N, N), dtype=int)
        self._generar_entorno_aleatorio()

        # Listas de entidades activas
        self.robots: List[Any] = []
        self.monstruos: List[Any] = []

    # -------------------------------------------------------------------------
    # GENERACIÓN DEL ESPACIO ENERGÉTICO
    # -------------------------------------------------------------------------
    def _generar_entorno_aleatorio(self) -> None:
        """
        Genera el entorno N³ asignando aleatoriamente **Zonas Libres** y **Zonas Vacías**
        según la proporción establecida en `Psoft`.

        Asegura además que:
          • Las fronteras externas del cubo estén formadas completamente por
            **Zonas Vacías** (barrera energética impenetrable).
          • Las celdas internas se asignen aleatoriamente según `Psoft`.

        El método imprime un resumen del porcentaje de zonas generadas.
        """
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    self.grid[x, y, z] = (
                        self.ZONA_VACIA if random.random() < self.Psoft else self.ZONA_LIBRE
                    )

        # Asegurar un punto visible libre (centro)
        centro = self.N // 2
        self.grid[centro, centro, centro] = self.ZONA_LIBRE

        total_vacias = int(np.sum(self.grid == self.ZONA_VACIA))
        porcentaje = total_vacias / (self.N ** 3)
        print(
            f"🌍 Entorno generado ({self.N}³): "
            f"{total_vacias} Zonas Vacías ({porcentaje:.1%}), "
            f"{100 - porcentaje * 100:.1f}% Zonas Libres."
        )

    # -------------------------------------------------------------------------
    # CONSULTA DE CELDAS
    # -------------------------------------------------------------------------
    def obtener_tipo_celda(self, x: int, y: int, z: int) -> int:
        """
        Devuelve el tipo de zona correspondiente a una coordenada (x, y, z).

        Args:
            x, y, z (int): Coordenadas dentro del entorno energético.

        Returns:
            int:
                - 0 → **Zona Libre** (transitable)
                - 1 → **Zona Vacía** (bloqueada o fuera de límites)

        Si las coordenadas están fuera del cubo N³, se considera automáticamente
        una Zona Vacía.
        """
        if 0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N:
            return int(self.grid[x, y, z])
        return self.ZONA_VACIA  # fuera del entorno → bloqueada

    # -------------------------------------------------------------------------
    # REGISTRO DE ENTIDADES
    # -------------------------------------------------------------------------
    def registrar_robot(self, robot: Any) -> bool:
        """
        Registra un **Robot Racional** en el entorno si su celda es una Zona Libre.

        Reglas de registro (según los requisitos):
          • No puede colocarse en una Zona Vacía.
          • No puede compartir celda con otro robot.
          • Puede coexistir con un Monstruo Reflejo en la misma celda.

        Args:
            robot (AgenteRacionalRobot): instancia del agente a registrar.

        Returns:
            bool: True si el registro fue exitoso, False si se rechazó por conflicto.
        """
        if self.obtener_tipo_celda(robot.x, robot.y, robot.z) == self.ZONA_VACIA:
            print(f"⚠️ Robot {robot.id} en Zona Vacía ({robot.x}, {robot.y}, {robot.z}).")
            return False

        if any((r.x, r.y, r.z) == (robot.x, robot.y, robot.z) for r in self.robots):
            print(f"⚠️ Zona ocupada por otro Robot en ({robot.x}, {robot.y}, {robot.z}).")
            return False

        self.robots.append(robot)
        return True

    def registrar_monstruo(self, monstruo: Any) -> bool:
        """
        Registra un **Monstruo Reflejo** en el entorno si su celda es una Zona Libre.

        Reglas de registro (según los requisitos):
          • No puede colocarse en una Zona Vacía.
          • No puede compartir celda con otro monstruo.
          • Puede coexistir con robots racionales.

        Args:
            monstruo (AgenteReflejoMonstruo): instancia del agente reflejo simple.

        Returns:
            bool: True si se registró correctamente, False si hubo conflicto.
        """
        if self.obtener_tipo_celda(monstruo.x, monstruo.y, monstruo.z) == self.ZONA_VACIA:
            print(f"⚠️ Monstruo {monstruo.id} en Zona Vacía ({monstruo.x}, {monstruo.y}, {monstruo.z}).")
            return False

        if any((m.x, m.y, m.z) == (monstruo.x, monstruo.y, monstruo.z) for m in self.monstruos):
            print(f"⚠️ Zona ocupada por otro Monstruo en ({monstruo.x}, {monstruo.y}, {monstruo.z}).")
            return False

        self.monstruos.append(monstruo)
        return True

    # -------------------------------------------------------------------------
    # GESTIÓN DE ENTIDADES DURANTE LA SIMULACIÓN
    # -------------------------------------------------------------------------
    def eliminar_robot(self, robot_id: int) -> None:
        """
        Elimina un **Robot Racional** del entorno (por destrucción, salida o evento Vacuumator).

        Args:
            robot_id (int): Identificador del robot a eliminar.
        """
        self.robots = [r for r in self.robots if r.id != robot_id]

    def eliminar_monstruo(self, monstruo_id: int) -> None:
        """
        Elimina un **Monstruo Reflejo** del entorno (por destrucción energética).

        Args:
            monstruo_id (int): Identificador del monstruo a eliminar.
        """
        self.monstruos = [m for m in self.monstruos if m.id != monstruo_id]

    # -------------------------------------------------------------------------
    # VISUALIZACIÓN DEL ENTORNO
    # -------------------------------------------------------------------------
    def visualizar_capa(self, z: int) -> None:
        """
        Muestra una representación bidimensional de una **capa energética** (Z fija).

        Representación simbólica:
            [ ] → Zona Libre
            [#] → Zona Vacía
            [R] → Robot Racional
            [M] → Monstruo Reflejo

        Args:
            z (int): Índice de capa (0 ≤ z < N).
        """
        if not (0 <= z < self.N):
            print(f"Capa {z} fuera de rango.")
            return

        print(f"\n--- Capa Energética Z={z} ---")
        for y in range(self.N):
            fila = ""
            for x in range(self.N):
                if any((r.x, r.y, r.z) == (x, y, z) for r in self.robots):
                    fila += "[R]"
                elif any((m.x, m.y, m.z) == (x, y, z) for m in self.monstruos):
                    fila += "[M]"
                elif self.grid[x, y, z] == self.ZONA_VACIA:
                    fila += "[#]"
                else:
                    fila += "[ ]"
            print(fila)
