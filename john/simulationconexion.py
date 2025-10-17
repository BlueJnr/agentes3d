# simulationconexion.py
import csv
import os
from typing import List, Dict, Any
from datetime import datetime

class Simulation:
    """
    Sistema de simulación que conecta agentes con el entorno.
    Coordina las interacciones y gestiona el ciclo de simulación.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa la simulación con configuración especificada.
        
        Args:
            config: Diccionario de configuración
        """
        self.config = config
        self.entorno = None
        self.logs = []
        self.corrida_id = None
        
        # Inicializar componentes
        self._inicializar_entorno()
        self._inicializar_agentes()
        
    def _inicializar_entorno(self):
        """Inicializa el entorno 3D con parámetros de configuración."""
        from environment import Entorno3D
        
        self.entorno = Entorno3D(
            N=self.config['N'],
            Pfree=self.config['Pfree'],
            Psoft=self.config['Psoft'],
            seed=self.config['seed']
        )
        
        print(f" ENTORNO INICIALIZADO: {self.entorno}")
    
    def _inicializar_agentes(self):
        """Inicializa y registra todos los agentes en el entorno."""
        from agent_robot import AgenteRobot
        from agent_monster import AgenteMonstruo
        
        # Inicializar robots
        self.robots = []
        for i in range(self.config['Nrobot']):
            pos_libre = self._obtener_posicion_libre()
            if pos_libre:
                robot = AgenteRobot(id=i, x=pos_libre[0], y=pos_libre[1], z=pos_libre[2])
                if self.entorno.registrar_robot(robot):
                    self.robots.append(robot)
        
        # Inicializar monstruos
        self.monstruos = []
        for i in range(self.config['Nmonstruos']):
            pos_libre = self._obtener_posicion_libre()
            if pos_libre:
                monstruo = AgenteMonstruo(
                    id=i, 
                    x=pos_libre[0], y=pos_libre[1], z=pos_libre[2],
                    p_move=self.config.get('p_move', 0.7)
                )
                if self.entorno.registrar_monstruo(monstruo):
                    self.monstruos.append(monstruo)
        
        print(f" AGENTES INICIALIZADOS: {len(self.robots)} robots, {len(self.monstruos)} monstruos")
    
    def _obtener_posicion_libre(self) -> Optional[Tuple[int, int, int]]:
        """Encuentra una posición libre aleatoria en el entorno."""
        intentos = 0
        while intentos < 100:  # Límite de intentos para evitar loop infinito
            x = random.randint(0, self.entorno.N - 1)
            y = random.randint(0, self.entorno.N - 1)
            z = random.randint(0, self.entorno.N - 1)
            
            # Verificar que sea Zona Libre
            if self.entorno.grid[x, y, z] == 0:
                # Verificar que no haya otra entidad en esa posición
                posicion_ocupada = any(
                    (entidad.x == x and entidad.y == y and entidad.z == z)
                    for entidad in self.robots + self.monstruos
                )
                if not posicion_ocupada:
                    return (x, y, z)
            
            intentos += 1
        
        print("  No se pudo encontrar posición libre después de 100 intentos")
        return None
    
    def ejecutar_ciclo_completo(self, tick_actual: int) -> List[Dict[str, Any]]:
        """
        Ejecuta un ciclo completo de simulación para el tick actual.
        
        Args:
            tick_actual: Número de tick actual
            
        Returns:
            List: Logs generados en este ciclo
        """
        logs_ciclo = []
        
        # FASE 1: Ejecución de robots (1 Hz)
        for robot in self.robots[:]:  # Copia para permitir remoción durante iteración
            if f"robot_{robot.id}" in self.entorno.entidades_activas:
                log_robot = self._ejecutar_ciclo_robot(robot, tick_actual)
                logs_ciclo.append(log_robot)
        
        # FASE 2: Ejecución de monstruos (cada K ticks)
        if tick_actual % self.config['K'] == 0:
            for monstruo in self.monstruos[:]:  # Copia para permitir remoción
                if f"monster_{monstruo.id}" in self.entorno.entidades_activas:
                    log_monstruo = self._ejecutar_ciclo_monstruo(monstruo, tick_actual)
                    logs_ciclo.append(log_monstruo)
        
        # Registrar estado del entorno
        log_entorno = {
            'tick': tick_actual,
            'agente': 'entorno',
            'id': -1,
            'x': -1, 'y': -1, 'z': -1,
            'orient': 'N/A',
            'dir': 'N/A',
            'perception': str(self.entorno.obtener_estado_entorno()),
            'action': 'update',
            'result': 'ciclo_completado'
        }
        logs_ciclo.append(log_entorno)
        
        return logs_ciclo
    
    def _ejecutar_ciclo_robot(self, robot, tick_actual: int) -> Dict[str, Any]:
        """
        Ejecuta ciclo completo de un robot.
        
        Args:
            robot: Instancia de AgenteRobot
            tick_actual: Tick actual
            
        Returns:
            Dict: Log del ciclo del robot
        """
        # El robot percibe y decide (esto se implementará en agent_robot.py)
        percepcion = robot.generar_percepcion(self.entorno, self.robots, self.monstruos)
        decision = robot.tomar_decision(percepcion)
        
        # Ejecutar acción a través del entorno
        resultado = self._ejecutar_accion_robot(robot, decision)
        
        # Actualizar memoria del robot
        robot.actualizar_memoria(tick_actual, percepcion, decision, resultado)
        
        # Generar log
        log_data = {
            'tick': tick_actual,
            'agente': 'robot',
            'id': robot.id,
            'x': robot.x,
            'y': robot.y,
            'z': robot.z,
            'orient': getattr(robot, 'orientacion_actual', 'N/A'),
            'dir': getattr(robot, 'direccion_actual', 'N/A'),
            'perception': str(percepcion),
            'action': decision.get('accion', 'unknown'),
            'result': resultado.get('estado', 'unknown')
        }
        
        return log_data
    
    def _ejecutar_ciclo_monstruo(self, monstruo, tick_actual: int) -> Dict[str, Any]:
        """
        Ejecuta ciclo completo de un monstruo.
        
        Args:
            monstruo: Instancia de AgenteMonstruo
            tick_actual: Tick actual
            
        Returns:
            Dict: Log del ciclo del monstruo
        """
        # Usar el método ya implementado en AgenteMonstruo
        log_data = monstruo.ciclo_reflejo_simple(self.entorno, tick_actual, self.config['K'])
        return log_data
    
    def _ejecutar_accion_robot(self, robot, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una acción de robot a través del entorno.
        
        Args:
            robot: Instancia de AgenteRobot
            decision: Decisión tomada por el robot
            
        Returns:
            Dict: Resultado de la ejecución
        """
        accion = decision.get('accion')
        
        if accion == 'move':
            # Validar y ejecutar movimiento
            dx, dy, dz = decision.get('direccion', (0, 0, 0))
            validacion = self.entorno.validar_movimiento_robot(robot, dx, dy, dz)
            
            if validacion['valido']:
                resultado = self.entorno.ejecutar_movimiento_robot(robot, validacion['nueva_posicion'])
                return {
                    'estado': 'move_ok' if not resultado.get('destruccion', False) else 'destroyed_both',
                    'detalles': validacion
                }
            else:
                return {
                    'estado': 'collision_logged',
                    'detalles': validacion
                }
        
        elif accion == 'rotate':
            # Rotación es siempre válida (no depende del entorno)
            return {'estado': 'rotate_ok', 'detalles': decision}
        
        elif accion == 'vacuum':
            # Verificar que el robot está en celda con monstruo
            monstruo = self.entorno._obtener_monstruo_en_posicion(robot.x, robot.y, robot.z)
            if monstruo:
                resultado = self.entorno._ejecutar_destruccion_conjunta(robot, monstruo)
                return {'estado': 'destroyed_both', 'detalles': resultado}
            else:
                return {'estado': 'vacuum_fail', 'detalles': 'no_monster_in_cell'}
        
        return {'estado': 'unknown_action', 'detalles': decision}
    
    def ejecutar_simulacion(self, duracion: int) -> str:
        """
        Ejecuta la simulación completa por la duración especificada.
        
        Args:
            duracion: Número de ticks a simular
            
        Returns:
            str: Ruta del archivo de log generado
        """
        print(f"\n INICIANDO SIMULACIÓN ({duracion} ticks)")
        print("=" * 60)
        
        self.corrida_id = f"corrida_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        for tick in range(duracion):
            logs_tick = self.ejecutar_ciclo_completo(tick)
            self.logs.extend(logs_tick)
            
            # Mostrar progreso cada 10 ticks
            if tick % 10 == 0 or tick == duracion - 1:
                estado = self.entorno.obtener_estado_entorno()
                print(f"⏱  Tick {tick:3d} | :{estado['robots_activos']:2d} "
                      f":{estado['monstruos_activos']:2d} | "
                      f":{estado['estadisticas']['destrucciones_conjuntas']:2d}")
        
        # Exportar logs
        return self._exportar_logs()
    
    def _exportar_logs(self) -> str:
        """Exporta todos los logs a archivo CSV."""
        if not self.logs:
            print("  No hay logs para exportar")
            return ""
        
        nombre_archivo = f"{self.corrida_id}.csv"
        os.makedirs('logs', exist_ok=True)
        ruta_completa = os.path.join('logs', nombre_archivo)
        
        with open(ruta_completa, 'w', newline='', encoding='utf-8') as csvfile:
            campos = ['tick', 'agente', 'id', 'x', 'y', 'z', 'orient', 'dir', 'perception', 'action', 'result']
            writer = csv.DictWriter(csvfile, fieldnames=campos)
            
            writer.writeheader()
            for log in self.logs:
                writer.writerow(log)
        
        print(f" Logs exportados: {ruta_completa} ({len(self.logs)} registros)")
        return ruta_completa
    
    def obtener_estadisticas_finales(self) -> Dict[str, Any]:
        """Retorna estadísticas finales de la simulación."""
        if not self.entorno:
            return {}
        
        estado = self.entorno.obtener_estado_entorno()
        return {
            'corrida_id': self.corrida_id,
            'duracion_simulacion': len(self.logs) // max(1, len(self.robots) + len(self.monstruos)),
            'estado_final_entorno': estado,
            'total_eventos_registrados': len(self.logs),
            'configuracion_usada': self.config
        }