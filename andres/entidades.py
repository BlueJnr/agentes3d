"""
Define las clases para las entidades que habitan en el mundo,
Robots y Monstruos.
"""

class Robot:
    """Representa a un agente Robot."""
    def __init__(self, id_robot: int):
        self.id = id_robot
        self.posicion = None  # Se asignará posterior a la creación

    def __repr__(self) -> str:
        # identificar el objeto al imprimirlo
        return f"Robot(ID={self.id}, Pos={self.posicion})"


class Monstruo:
    """Representa a un agente Monstruo de reflejo simple."""
    def __init__(self, id_monstruo: int):
        self.id = id_monstruo
        self.posicion = None  # Se asignará posterior a la creación

    def __repr__(self) -> str:
        return f"Monstruo(ID={self.id}, Pos={self.posicion})"