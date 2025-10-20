# environment.py
import random
from typing import List, Any, Optional

import numpy as np


class EntornoOperacion:
    """Entorno tridimensional N³ donde interactúan robots y monstruos."""

    ZONA_LIBRE = 0
    ZONA_VACIA = 1

    def __init__(self, N: int = 5, Pfree: float = 0.8, Psoft: float = 0.2, seed: Optional[int] = None) -> None:
        """Inicializa el cubo energético con distribución aleatoria de zonas libres y vacías."""
        self.N = N
        self.Pfree = Pfree
        self.Psoft = Psoft

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        self.grid = np.zeros((N, N, N), dtype=int)
        self._generar_entorno_aleatorio()
        self.robots: List[Any] = []
        self.monstruos: List[Any] = []

    # -------------------------------------------------------------------------
    # GENERACIÓN
    # -------------------------------------------------------------------------
    def _generar_entorno_aleatorio(self) -> None:
        """Genera el entorno asignando Zonas Libres o Vacías según la proporción definida."""
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    self.grid[x, y, z] = self.ZONA_VACIA if random.random() < self.Psoft else self.ZONA_LIBRE

        centro = self.N // 2
        self.grid[centro, centro, centro] = self.ZONA_LIBRE

        total_vacias = int(np.sum(self.grid == self.ZONA_VACIA))
        porcentaje = total_vacias / (self.N ** 3)
        print(
            f"🌍 Entorno generado ({self.N}³): {total_vacias} Zonas Vacías ({porcentaje:.1%}), "
            f"{100 - porcentaje * 100:.1f}% Zonas Libres."
        )

    # -------------------------------------------------------------------------
    # CONSULTA
    # -------------------------------------------------------------------------
    def obtener_tipo_celda(self, x: int, y: int, z: int) -> int:
        """Devuelve el tipo de zona (Libre o Vacía) en las coordenadas dadas."""
        if 0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N:
            return int(self.grid[x, y, z])
        return self.ZONA_VACIA

    # -------------------------------------------------------------------------
    # REGISTRO DE ENTIDADES
    # -------------------------------------------------------------------------
    def registrar_robot(self, robot: Any) -> bool:
        """Registra un robot si la celda es libre y no está ocupada por otro robot."""
        if self.obtener_tipo_celda(robot.x, robot.y, robot.z) == self.ZONA_VACIA:
            print(f"⚠️ Robot {robot.id} en Zona Vacía ({robot.x}, {robot.y}, {robot.z}).")
            return False
        if any((r.x, r.y, r.z) == (robot.x, robot.y, robot.z) for r in self.robots):
            print(f"⚠️ Zona ocupada por otro Robot en ({robot.x}, {robot.y}, {robot.z}).")
            return False
        self.robots.append(robot)
        return True

    def registrar_monstruo(self, monstruo: Any) -> bool:
        """Registra un monstruo si la celda es libre y no está ocupada por otro monstruo."""
        if self.obtener_tipo_celda(monstruo.x, monstruo.y, monstruo.z) == self.ZONA_VACIA:
            print(f"⚠️ Monstruo {monstruo.id} en Zona Vacía ({monstruo.x}, {monstruo.y}, {monstruo.z}).")
            return False
        if any((m.x, m.y, m.z) == (monstruo.x, monstruo.y, monstruo.z) for m in self.monstruos):
            print(f"⚠️ Zona ocupada por otro Monstruo en ({monstruo.x}, {monstruo.y}, {monstruo.z}).")
            return False
        self.monstruos.append(monstruo)
        return True

    # -------------------------------------------------------------------------
    # GESTIÓN
    # -------------------------------------------------------------------------
    def eliminar_robot(self, robot_id: int) -> None:
        """Desactiva un robot por su ID."""
        for r in self.robots:
            if r.id == robot_id and r.activo:
                r.activo = False
                break

    def eliminar_monstruo(self, monstruo_id: int) -> None:
        """Desactiva un monstruo por su ID."""
        for m in self.monstruos:
            if m.id == monstruo_id and m.activo:
                m.activo = False
                break

    # -------------------------------------------------------------------------
    # VISUALIZACIÓN
    # -------------------------------------------------------------------------
    def visualizar_capa(self, z: int) -> None:
        """Imprime una capa bidimensional del entorno (Z fija)."""
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
