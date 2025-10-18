# environment.py
import random
from typing import List, Any, Optional

import numpy as np


class EntornoOperacion:
    """
    Representa el entorno energético tridimensional donde interactúan los agentes.

    Este entorno es un hexaedro regular de N³ cubos (espacio energético),
    conformado por dos tipos de zonas:
      - Zona Libre (Pfree): regiones transitables donde pueden ubicarse entidades materiales o energéticas.
      - Zona Vacía (Psoft): regiones no transitables o bloqueadas.
        El entorno está rodeado externamente por una capa de Zonas Vacías.

    El entorno gestiona la creación aleatoria del espacio, la validación de límites
    y el registro de entidades activas (robots racionales y monstruos reflejo).
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
        Inicializa el entorno energético tridimensional.

        Args:
            N: Tamaño del lado del cubo (N×N×N).
            Pfree: Porcentaje esperado de Zonas Libres.
            Psoft: Porcentaje esperado de Zonas Vacías (no transitables).
            seed: Semilla opcional para reproducibilidad.
        """
        self.N = N
        self.Pfree = Pfree
        self.Psoft = Psoft

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Malla cúbica de zonas energéticas
        self.grid = np.zeros((N, N, N), dtype=int)
        self._generar_entorno_aleatorio()

        # Entidades activas
        self.robots: List[Any] = []
        self.monstruos: List[Any] = []

    # -------------------------------------------------------------------------
    # GENERACIÓN DEL ESPACIO ENERGÉTICO
    # -------------------------------------------------------------------------
    def _generar_entorno_aleatorio(self) -> None:
        """Genera el entorno N³ asignando Zonas Libres y Vacías según Psoft."""
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    # Psoft determina la probabilidad de una Zona Vacía
                    if random.random() < self.Psoft:
                        self.grid[x, y, z] = self.ZONA_VACIA
                    else:
                        self.grid[x, y, z] = self.ZONA_LIBRE

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
        Devuelve el tipo de zona en las coordenadas dadas.

        Returns:
            int:
                - 0 → Zona Libre
                - 1 → Zona Vacía (fuera de límites o bloqueada)
        """
        if 0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N:
            return self.grid[x, y, z]
        return self.ZONA_VACIA  # fuera del entorno → bloqueada

    # -------------------------------------------------------------------------
    # REGISTRO DE ENTIDADES
    # -------------------------------------------------------------------------
    def registrar_robot(self, robot: Any) -> bool:
        """
        Registra un robot racional si la zona es libre y no hay otro robot en ella.
        Puede coexistir con un monstruo reflejo, pero no con otro robot.
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
        Registra un monstruo reflejo si la zona es libre y no hay otro monstruo en ella.
        Puede coexistir con robots racionales, pero no con otros monstruos.
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
    # VISUALIZACIÓN DEL ENTORNO
    # -------------------------------------------------------------------------
    def visualizar_capa(self, z: int) -> None:
        """
        Muestra una vista 2D del entorno para una capa Z específica.

        Representación:
            [ ] → Zona Libre
            [#] → Zona Vacía
            [R] → Robot Racional
            [M] → Monstruo Reflejo
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
