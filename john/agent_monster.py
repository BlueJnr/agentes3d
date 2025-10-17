# agent_monster.py
import random
from typing import Tuple, Optional, List

class AgenteMonstruo:
    """
    Agente reflejo simple que representa un Monstruo en el entorno 3D.
    Implementa comportamiento puramente reactivo sin estado interno.
    """
    
    # Direcciones ortogonales posibles en espacio 3D
    DIRECCIONES = [
        (1, 0, 0),   # +X
        (-1, 0, 0),  # -X
        (0, 1, 0),   # +Y
        (0, -1, 0),  # -Y
        (0, 0, 1),   # +Z
        (0, 0, -1)   # -Z
    ]
    
    def __init__(self, id: int, x: int, y: int, z: int, p_move: float = 0.7):
        """
        Inicializa el agente monstruo.
        
        Args:
            id: Identificador único del monstruo
            x, y, z: Posición inicial en el entorno 3D
            p_move: Probabilidad de moverse cuando se activa (default: 0.7)
        """
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.p_move = p_move
        self.acciones_realizadas = 0
        
    def percepcion_actual(self, entorno) -> dict:
        """
        Simula la percepción mínima del monstruo.
        Solo percibe si puede moverse a celdas adyacentes.
        
        Args:
            entorno: Instancia de Entorno3D para validar movimientos
            
        Returns:
            dict: Percepciones disponibles para la toma de decisiones
        """
        percepcion = {
            'posicion_actual': (self.x, self.y, self.z),
            'movimientos_validos': self._obtener_movimientos_validos(entorno),
            'puede_moverse': len(self._obtener_movimientos_validos(entorno)) > 0
        }
        return percepcion
    
    def _obtener_movimientos_validos(self, entorno) -> List[Tuple[int, int, int]]:
        """
        Obtiene las direcciones de movimiento válidas desde la posición actual.
        
        Args:
            entorno: Instancia de Entorno3D para validar celdas
            
        Returns:
            List[Tuple]: Lista de direcciones (dx, dy, dz) válidas
        """
        movimientos_validos = []
        
        for dx, dy, dz in self.DIRECCIONES:
            nueva_x, nueva_y, nueva_z = self.x + dx, self.y + dy, self.z + dz
            
            # Validar si el movimiento es posible
            if self._es_movimiento_valido(entorno, nueva_x, nueva_y, nueva_z):
                movimientos_validos.append((dx, dy, dz))
                
        return movimientos_validos
    
    def _es_movimiento_valido(self, entorno, x: int, y: int, z: int) -> bool:
        """
        Verifica si un movimiento a la posición (x,y,z) es válido.
        
        Args:
            entorno: Instancia de Entorno3D
            x, y, z: Coordenadas destino
            
        Returns:
            bool: True si el movimiento es válido
        """
        # Verificar límites del entorno
        if not (0 <= x < entorno.N and 0 <= y < entorno.N and 0 <= z < entorno.N):
            return False
            
        # Verificar que no sea Zona Vacía
        if entorno.grid[x, y, z] == 1:  # 1 = Zona Vacía
            return False
            
        return True
    
    def decidir_accion(self, entorno, tick_actual: int, K: int) -> Tuple[str, Optional[Tuple[int, int, int]]]:
        """
        Implementa la lógica de reflejo simple del monstruo.
        Solo se activa cada K ticks y con probabilidad p_move.
        
        Args:
            entorno: Instancia de Entorno3D
            tick_actual: Tick actual de la simulación
            K: Frecuencia de activación del monstruo
            
        Returns:
            Tuple: (accion, nueva_posicion) 
                   accion: 'move' o 'idle'
                   nueva_posicion: None si idle, (x,y,z) si move
        """
        # Verificar frecuencia de activación (cada K ticks)
        if tick_actual % K != 0:
            return 'idle', None
            
        # Verificar probabilidad de movimiento
        if random.random() > self.p_move:
            return 'idle', None
            
        # Obtener movimientos válidos
        movimientos_validos = self._obtener_movimientos_validos(entorno)
        
        # Si no hay movimientos válidos, permanecer idle
        if not movimientos_validos:
            return 'idle', None
            
        # Seleccionar movimiento aleatorio (comportamiento reflejo simple)
        dx, dy, dz = random.choice(movimientos_validos)
        nueva_x, nueva_y, nueva_z = self.x + dx, self.y + dy, self.z + dz
        
        self.acciones_realizadas += 1
        return 'move', (nueva_x, nueva_y, nueva_z)
    
    def ejecutar_accion(self, accion: str, nueva_posicion: Optional[Tuple[int, int, int]]):
        """
        Ejecuta la acción decidida, actualizando la posición del monstruo.
        
        Args:
            accion: 'move' o 'idle'
            nueva_posicion: Nueva posición si la acción es 'move'
        """
        if accion == 'move' and nueva_posicion:
            self.x, self.y, self.z = nueva_posicion
    
    def obtener_estado_log(self) -> dict:
        """
        Retorna el estado actual para logging.
        
        Returns:
            dict: Estado actual del monstruo
        """
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'tipo': 'monster',
            'acciones_realizadas': self.acciones_realizadas
        }
    
    def __str__(self) -> str:
        """Representación string del monstruo."""
        return f"Monstruo(id={self.id}, pos=({self.x},{self.y},{self.z}), acciones={self.acciones_realizadas})"
    
    def __repr__(self) -> str:
        """Representación para debugging."""
        return self.__str__()