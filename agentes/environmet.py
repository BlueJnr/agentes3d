# environment.py
import random
from typing import List, Any, Optional

import numpy as np


class Entorno3D:
    """
    Representa el entorno tridimensional donde interactúan los agentes.

    El entorno se modela como una malla cúbica de dimensión N³,
    compuesta por celdas de dos tipos:
        - 0 → Zona Libre (transitable)
        - 1 → Zona Vacía (bloqueada o no transitable)

    Gestiona la generación aleatoria del espacio, la verificación de límites
    y el registro de los agentes activos (robots y monstruos).
    """

    ZONA_LIBRE = 0
    ZONA_VACIA = 1

    def __init__(self, N: int = 5, p_vacia: float = 0.2, seed: Optional[int] = None) -> None:
        """
        Inicializa el entorno tridimensional.

        Args:
            N: Dimensión del cubo (N×N×N).
            p_vacia: Probabilidad de generar una celda vacía (obstáculo).
            seed: Semilla aleatoria opcional para reproducibilidad.
        """
        self.N = N
        self.p_vacia = p_vacia

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Estructura cúbica del entorno
        self.grid = np.zeros((N, N, N), dtype=int)
        self._generar_aleatoriamente()

        # Registro de entidades activas
        self.robots: List[Any] = []
        self.monstruos: List[Any] = []

    # -------------------------------------------------------------------------
    # GENERACIÓN DEL ENTORNO
    # -------------------------------------------------------------------------
    def _generar_aleatoriamente(self) -> None:
        """
        Genera el entorno 3D asignando zonas vacías según la probabilidad definida.
        """
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    if random.random() < self.p_vacia:
                        self.grid[x, y, z] = self.ZONA_VACIA

        total_vacias = int(np.sum(self.grid == self.ZONA_VACIA))
        porcentaje = total_vacias / (self.N ** 3)
        print(f"🌍 Entorno 3D generado ({self.N}³) con {total_vacias} zonas vacías ({porcentaje:.1%}).")

    # -------------------------------------------------------------------------
    # CONSULTA DE CELDAS
    # -------------------------------------------------------------------------
    def get_cell_type(self, x: int, y: int, z: int) -> int:
        """
        Devuelve el tipo de celda en la posición indicada.

        Args:
            x, y, z: Coordenadas de la celda.

        Returns:
            int:
                - 0 si la celda es Zona Libre.
                - 1 si es Zona Vacía o está fuera de los límites.
        """
        if 0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N:
            return self.grid[x, y, z]
        return self.ZONA_VACIA

    # -------------------------------------------------------------------------
    # REGISTRO DE ENTIDADES
    # -------------------------------------------------------------------------
    def registrar_robot(self, robot: Any) -> bool:
        """
        Registra un robot en el entorno si la celda es válida.

        Args:
            robot: Instancia de AgenteRobot.

        Returns:
            bool: True si se registró correctamente, False si la celda estaba vacía.
        """
        if self.get_cell_type(robot.x, robot.y, robot.z) == self.ZONA_VACIA:
            print(f"⚠️ Robot {robot.id} en zona vacía ({robot.x}, {robot.y}, {robot.z}).")
            return False
        self.robots.append(robot)
        return True

    def registrar_monstruo(self, monstruo: Any) -> bool:
        """
        Registra un monstruo en el entorno si la celda es válida.

        Args:
            monstruo: Instancia de AgenteMonstruo.

        Returns:
            bool: True si se registró correctamente, False si la celda estaba vacía.
        """
        if self.get_cell_type(monstruo.x, monstruo.y, monstruo.z) == self.ZONA_VACIA:
            print(f"⚠️ Monstruo {monstruo.id} en zona vacía ({monstruo.x}, {monstruo.y}, {monstruo.z}).")
            return False
        self.monstruos.append(monstruo)
        return True

    # -------------------------------------------------------------------------
    # VISUALIZACIÓN
    # -------------------------------------------------------------------------
    def visualizar_capa(self, z: int) -> None:
        """
        Muestra una representación 2D de una capa fija (eje Z) del entorno.

        Cada celda se representa como:
            [ ] → Zona Libre
            [#] → Zona Vacía
            [R] → Robot
            [M] → Monstruo
        """
        if not (0 <= z < self.N):
            print(f"Capa {z} fuera de rango.")
            return

        print(f"\n--- Capa Z={z} ---")
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
