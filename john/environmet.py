# environment.py
import numpy as np
import random
from typing import List, Tuple, Optional, Dict, Any

class Entorno3D:
    """
    Entorno operativo 3D que gestiona el espacio, entidades y sus interacciones.
    Coordina la conexión entre agentes y el mundo simulado.
    """
    
    def __init__(self, N: int = 5, Pfree: float = 0.8, Psoft: float = 0.2, seed: Optional[int] = None):
        """
        Inicializa el entorno 3D con configuración especificada.
        
        Args:
            N: Tamaño del cubo (N×N×N)
            Pfree: Proporción de Zonas Libres
            Psoft: Proporción de Zonas Vacías (debe cumplir Pfree + Psoft = 1.0)
            seed: Semilla para reproducibilidad
        """
        self.N = N
        self.Pfree = Pfree
        self.Psoft = Psoft
        self.seed = seed
        
        # Inicializar generadores aleatorios
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        # Grid 3D: 0 = Zona Libre, 1 = Zona Vacía
        self.grid = np.zeros((N, N, N), dtype=int)
        self._generar_entorno()
        
        # Registro de entidades
        self.robots = []
        self.monstruos = []
        self.entidades_activas = set()
        
        # Estadísticas de interacción
        self.estadisticas = {
            'choques_registrados': 0,
            'destrucciones_conjuntas': 0,
            'movimientos_validos': 0,
            'movimientos_invalidos': 0
        }
    
    def _generar_entorno(self):
        """Genera la malla 3D con Zonas Libres y Vacías según probabilidades."""
        print(f"🔧 Generando entorno {self.N}x{self.N}x{self.N} (Pfree={self.Pfree}, Psoft={self.Psoft})")
        
        for x in range(self.N):
            for y in range(self.N):
                for z in range(self.N):
                    # Distribución basada en Pfree/Psoft
                    if random.random() < self.Psoft:
                        self.grid[x, y, z] = 1  # Zona Vacía
                    else:
                        self.grid[x, y, z] = 0  # Zona Libre
        
        # Contar estadísticas de generación
        zonas_libres = np.sum(self.grid == 0)
        zonas_vacias = np.sum(self.grid == 1)
        total_celdas = self.N ** 3
        
        print(f"   • Zonas Libres: {zonas_libres}/{total_celdas} ({zonas_libres/total_celdas:.1%})")
        print(f"   • Zonas Vacías: {zonas_vacias}/{total_celdas} ({zonas_vacias/total_celdas:.1%})")
    
    def registrar_robot(self, robot) -> bool:
        """
        Registra un robot en el entorno y valida su posición inicial.
        
        Args:
            robot: Instancia de AgenteRobot
            
        Returns:
            bool: True si registro exitoso
        """
        if not self._es_posicion_valida(robot.x, robot.y, robot.z):
            print(f" Robot {robot.id} en posición inválida: ({robot.x}, {robot.y}, {robot.z})")
            return False
            
        if not self._es_celda_libre(robot.x, robot.y, robot.z):
            print(f" Robot {robot.id} en Zona Vacía: ({robot.x}, {robot.y}, {robot.z})")
            return False
            
        self.robots.append(robot)
        self.entidades_activas.add(f"robot_{robot.id}")
        print(f" Robot {robot.id} registrado en ({robot.x}, {robot.y}, {robot.z})")
        return True
    
    def registrar_monstruo(self, monstruo) -> bool:
        """
        Registra un monstruo en el entorno y valida su posición inicial.
        
        Args:
            monstruo: Instancia de AgenteMonstruo
            
        Returns:
            bool: True si registro exitoso
        """
        if not self._es_posicion_valida(monstruo.x, monstruo.y, monstruo.z):
            print(f" Monstruo {monstruo.id} en posición inválida: ({monstruo.x}, {monstruo.y}, {monstruo.z})")
            return False
            
        if not self._es_celda_libre(monstruo.x, monstruo.y, monstruo.z):
            print(f" Monstruo {monstruo.id} en Zona Vacía: ({monstruo.x}, {monstruo.y}, {monstruo.z})")
            return False
            
        self.monstruos.append(monstruo)
        self.entidades_activas.add(f"monster_{monstruo.id}")
        print(f" Monstruo {monstruo.id} registrado en ({monstruo.x}, {monstruo.y}, {monstruo.z})")
        return True
    
    def _es_posicion_valida(self, x: int, y: int, z: int) -> bool:
        """Verifica si posición está dentro de los límites del entorno."""
        return (0 <= x < self.N and 0 <= y < self.N and 0 <= z < self.N)
    
    def _es_celda_libre(self, x: int, y: int, z: int) -> bool:
        """Verifica si celda es Zona Libre (transitable)."""
        return self.grid[x, y, z] == 0
    
    def validar_movimiento_robot(self, robot, dx: int, dy: int, dz: int) -> Dict[str, Any]:
        """
        Valida un movimiento propuesto por un robot.
        
        Args:
            robot: Instancia de AgenteRobot
            dx, dy, dz: Dirección de movimiento
            
        Returns:
            Dict: Resultado de validación con detalles
        """
        nueva_x, nueva_y, nueva_z = robot.x + dx, robot.y + dy, robot.z + dz
        
        # Verificar límites
        if not self._es_posicion_valida(nueva_x, nueva_y, nueva_z):
            self.estadisticas['movimientos_invalidos'] += 1
            return {
                'valido': False,
                'razon': 'fuera_limites',
                'tipo_celda': 'exterior',
                'activar_vacuscopio': True
            }
        
        # Verificar tipo de celda
        tipo_celda = self.grid[nueva_x, nueva_y, nueva_z]
        if tipo_celda == 1:  # Zona Vacía
            self.estadisticas['movimientos_invalidos'] += 1
            self.estadisticas['choques_registrados'] += 1
            return {
                'valido': False,
                'razon': 'zona_vacia',
                'tipo_celda': 'vacuum',
                'activar_vacuscopio': True
            }
        
        # Verificar colisión con otro robot
        for otro_robot in self.robots:
            if (otro_robot.id != robot.id and 
                otro_robot.x == nueva_x and otro_robot.y == nueva_y and otro_robot.z == nueva_z):
                self.estadisticas['movimientos_invalidos'] += 1
                return {
                    'valido': False,
                    'razon': 'robot_en_celda',
                    'tipo_celda': 'ocupada',
                    'activar_vacuscopio': False,
                    'robot_bloqueador': otro_robot.id
                }
        
        # Movimiento válido
        self.estadisticas['movimientos_validos'] += 1
        return {
            'valido': True,
            'razon': 'movimiento_valido',
            'tipo_celda': 'libre',
            'activar_vacuscopio': False,
            'nueva_posicion': (nueva_x, nueva_y, nueva_z)
        }
    
    def validar_movimiento_monstruo(self, monstruo, dx: int, dy: int, dz: int) -> Dict[str, Any]:
        """
        Valida un movimiento propuesto por un monstruo.
        
        Args:
            monstruo: Instancia de AgenteMonstruo
            dx, dy, dz: Dirección de movimiento
            
        Returns:
            Dict: Resultado de validación
        """
        nueva_x, nueva_y, nueva_z = monstruo.x + dx, monstruo.y + dy, monstruo.z + dz
        
        # Verificar límites
        if not self._es_posicion_valida(nueva_x, nueva_y, nueva_z):
            return {
                'valido': False,
                'razon': 'fuera_limites'
            }
        
        # Verificar Zona Vacía
        if self.grid[nueva_x, nueva_y, nueva_z] == 1:
            return {
                'valido': False,
                'razon': 'zona_vacia'
            }
        
        # Los monstruos pueden compartir celdas entre sí, pero no con robots
        for robot in self.robots:
            if (robot.x == nueva_x and robot.y == nueva_y and robot.z == nueva_z):
                return {
                    'valido': False,
                    'razon': 'robot_en_celda'
                }
        
        return {
            'valido': True,
            'razon': 'movimiento_valido',
            'nueva_posicion': (nueva_x, nueva_y, nueva_z)
        }
    
    def ejecutar_movimiento_robot(self, robot, nueva_posicion: Tuple[int, int, int]):
        """
        Ejecuta el movimiento de un robot a nueva posición.
        
        Args:
            robot: Instancia de AgenteRobot
            nueva_posicion: Tuple (x, y, z) destino
        """
        vieja_x, vieja_y, vieja_z = robot.x, robot.y, robot.z
        nueva_x, nueva_y, nueva_z = nueva_posicion
        
        # Actualizar posición del robot
        robot.x, robot.y, robot.z = nueva_x, nueva_y, nueva_z
        
        # Verificar destrucción conjunta (robot entra en celda con monstruo)
        monstruo_en_celda = self._obtener_monstruo_en_posicion(nueva_x, nueva_y, nueva_z)
        if monstruo_en_celda:
            return self._ejecutar_destruccion_conjunta(robot, monstruo_en_celda)
        
        return {'evento': 'movimiento_exitoso', 'destruccion': False}
    
    def _obtener_monstruo_en_posicion(self, x: int, y: int, z: int):
        """Encuentra monstruo en posición específica."""
        for monstruo in self.monstruos:
            if monstruo.x == x and monstruo.y == y and monstruo.z == z:
                return monstruo
        return None
    
    def _ejecutar_destruccion_conjunta(self, robot, monstruo):
        """
        Ejecuta la destrucción conjunta robot-monstruo.
        
        Args:
            robot: Robot involucrado
            monstruo: Monstruo involucrado
            
        Returns:
            Dict: Resultado del evento
        """
        print(f" DESTRUCCIÓN CONJUNTA: Robot {robot.id} + Monstruo {monstruo.id} en ({robot.x}, {robot.y}, {robot.z})")
        
        # Convertir celda a Zona Vacía
        self.grid[robot.x, robot.y, robot.z] = 1
        
        # Remover entidades del entorno
        self.robots = [r for r in self.robots if r.id != robot.id]
        self.monstruos = [m for m in self.monstruos if m.id != monstruo.id]
        self.entidades_activas.discard(f"robot_{robot.id}")
        self.entidades_activas.discard(f"monster_{monstruo.id}")
        
        self.estadisticas['destrucciones_conjuntas'] += 1
        
        return {
            'evento': 'destruccion_conjunta',
            'destruccion': True,
            'robot_destruido': robot.id,
            'monstruo_destruido': monstruo.id,
            'posicion': (robot.x, robot.y, robot.z)
        }
    
    def obtener_estado_entorno(self) -> Dict[str, Any]:
        """
        Retorna estado completo del entorno para logging y análisis.
        
        Returns:
            Dict: Estado del entorno
        """
        return {
            'dimension': self.N,
            'robots_activos': len(self.robots),
            'monstruos_activos': len(self.monstruos),
            'entidades_totales': len(self.entidades_activas),
            'estadisticas': self.estadisticas.copy(),
            'grid_summary': {
                'zonas_libres': int(np.sum(self.grid == 0)),
                'zonas_vacias': int(np.sum(self.grid == 1)),
                'densidad_ocupacion': f"{np.sum(self.grid == 1) / (self.N**3):.1%}"
            }
        }
    
    def __str__(self) -> str:
        """Representación resumida del entorno."""
        estado = self.obtener_estado_entorno()
        return (f"Entorno3D({self.N}³) | :{estado['robots_activos']} "
                f":{estado['monstruos_activos']} | :{estado['estadisticas']['destrucciones_conjuntas']}")