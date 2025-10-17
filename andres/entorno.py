"""
Define la clase Mundo, que gestiona el entorno de operación 3D,
la generación de celdas y la ubicación de las entidades.
"""
import numpy as np
from entidades import Robot, Monstruo # Importamos las clases del otro fichero

class Mundo:
    """Gestiona el espacio cúbico, las celdas y las entidades."""

    ZONA_LIBRE = 0
    ZONA_VACIA = 1

    def __init__(self, n: int):
        if n < 1:
            raise ValueError("El tamaño N del mundo debe ser al menos una celda.")
        self.n = n
        self.prob_vacia = 0.75
        # Creamos el grid 3D inicializado con Zonas Libres, agregando los bordes
        self.grid = np.full((n+2, n+2, n+2), self.ZONA_LIBRE, dtype=int)
        # Diccionario para rastrear la posición de cada entidad: {(x, y, z): entidad_obj}
        self.entidades = {}

    def generar_mundo(self):
        """
        Genera el mundo aleatoriamente y lo rodea con una capa de Zonas Vacías.
        """
        # 1. Crear el borde de Zonas Vacías
        self.grid[0, :, :] = self.ZONA_VACIA
        self.grid[self.n+1, :, :] = self.ZONA_VACIA
        self.grid[:, 0, :] = self.ZONA_VACIA
        self.grid[:, self.n+1, :] = self.ZONA_VACIA
        self.grid[:, :, 0] = self.ZONA_VACIA
        self.grid[:, :, self.n+1] = self.ZONA_VACIA

        # 2. Rellenar el interior aleatoriamente
        for x in range(1, self.n):
            for y in range(1, self.n):
                for z in range(1, self.n):
                    if np.random.rand() < self.prob_vacia:
                        self.grid[x, y, z] = self.ZONA_VACIA
        
        print("Mundo generado exitosamente.")

    def validar_posicion_para_spawn(self, x: int, y: int, z: int) -> (bool, str):
        """
        Verifica si una entidad puede ser colocada en una coordenada específica.
        Devuelve un booleano y un mensaje descriptivo.
        """
        # Comprobar si está dentro de los límites
        if not (1 <= x <= self.n and 1 <= y <= self.n and 1 <= z <= self.n):
            return False, f"Error: La posición ({x},{y},{z}) está fuera de los límites del mundo (1 a {self.n})."
        
        # Comprobar si es una Zona Vacía (obstáculo)
        if self.grid[x, y, z] == self.ZONA_VACIA:
            return False, f"Error: La posición ({x},{y},{z}) es una Zona Vacía (obstáculo)."
            
        # Comprobar si ya está ocupada por otra entidad
        if (x, y, z) in self.entidades:
            entidad_existente = self.entidades[(x, y, z)]
            return False, f"Error: La posición ({x},{y},{z}) ya está ocupada por {entidad_existente}."
        
        return True, "Posición válida."

    def agregar_entidad(self, entidad, x: int, y: int, z: int) -> bool:
        """Intenta agregar una entidad al mundo en la posición dada."""
        es_valida, mensaje = self.validar_posicion_para_spawn(x, y, z)
        if not es_valida:
            print(mensaje) # Muestra el error específico
            return False
            
        entidad.posicion = (x, y, z)
        self.entidades[(x, y, z)] = entidad
        return True
    
    def eliminar_entidad(self, entidad) -> bool:
        """Elimina una entidad del mundo"""
        posicion = entidad.posicion
        if posicion in self.entidades:
            entidad_eliminada = self.entidades.pop(posicion)
            print(f"Éxito: Se ha eliminado {entidad_eliminada} de la posición {posicion}.")
            return True
        else:
            print(f"Aviso: No se encontró ninguna entidad en la posición {posicion} para eliminar.")
            return False
    
    def visualizar_capa(self, z: int):
        """Muestra una representación 2D de una capa (eje Z) del mundo."""
        if not (0 <= z <= self.n+1):
            print(f"Capa {z} fuera de los límites.")
            return

        print(f"\n--- Visualizando Capa Z={z} ---")
        for y in range(self.n+2):
            fila = ""
            for x in range(self.n+2):
                pos = (x, y, z)
                if pos in self.entidades:
                    entidad = self.entidades[pos]
                    if isinstance(entidad, Robot):
                        fila += "[R]" # Robot
                    else:
                        fila += "[M]" # Monstruo
                elif self.grid[x, y, z] == self.ZONA_VACIA:
                    fila += "[#]" # Zona Vacía
                else:
                    fila += "[ ]" # Zona Libre
            print(fila)