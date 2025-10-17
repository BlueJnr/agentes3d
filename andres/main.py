# main.py

"""
Punto de partida para iniciar la simulación.
Gestiona las entradas del usuario y la configuración inicial del mundo.
"""
from entorno import Mundo
from entidades import Robot, Monstruo

def obtener_entero_positivo(prompt: str) -> int:
    """Solicita un número entero positivo al usuario de forma segura."""
    while True:
        try:
            valor = int(input(prompt))
            if valor > 0:
                return valor
            print("Error: El número debe ser positivo.")
        except ValueError:
            print("Error: Debes ingresar un número entero válido.")

def obtener_coordenadas(prompt: str, n_mundo: int) -> (int, int, int):
    """Solicita coordenadas 'x,y,z' al usuario y las valida."""
    while True:
        try:
            texto = input(prompt)
            partes = texto.replace(" ", "").split(',')
            if len(partes) != 3:
                print("Error: Debes ingresar 3 valores separados por comas (ej: 2,3,1).")
                continue
            
            x, y, z = map(int, partes)
            
            # La validación completa se hará en la clase Mundo,
            # pero una comprobación rápida de límites aquí mejora la experiencia.
            if not (1 <= x <= n_mundo and 1 <= y <= n_mundo and 1 <= z <= n_mundo):
                 print(f"Aviso: Las coordenadas deben estar entre 1 y {n_mundo}.")
            
            return x, y, z
        except ValueError:
            print("Error: Las coordenadas deben ser números enteros.")

def main():
    """Función principal que ejecuta el programa."""
    print("--- ¡Bienvenido al Simulador de Agentes en un mundo 3D! ---")
    
    # 1. Crear el mundo
    n = obtener_entero_positivo("Ingresa el tamaño N para el mundo cúbico (NxNxN): ")
    mundo = Mundo(n)
    mundo.generar_mundo()
    
    # Para que el usuario vea dónde puede colocar entidades, mostramos una capa
    capa_a_ver = n // 2
    mundo.visualizar_capa(capa_a_ver)
    print(f"\nSe muestra la capa {capa_a_ver} como referencia. [ ]=Libre, [#]=Vacío.")
    
    # 2. Solicitar número de entidades
    num_robots = obtener_entero_positivo("\nIngresa el número de Robots a crear: ")
    num_monstruos = obtener_entero_positivo("Ingresa el número de Monstruos a crear: ")

    # 3. Colocar Robots
    print("\n--- Colocación de Robots ---")
    for i in range(num_robots):
        robot = Robot(id_robot=i + 1)
        while True:
            coords = obtener_coordenadas(f"Posición inicial para el Robot {robot.id} (x,y,z): ", n)
            if mundo.agregar_entidad(robot, *coords):
                print(f"Robot {robot.id} agregado en la posición {coords}.")
                break # Sale del bucle si se agregó con éxito

    # 4. Colocar Monstruos
    print("\n--- Colocación de Monstruos ---")
    for i in range(num_monstruos):
        monstruo = Monstruo(id_monstruo=i + 1)
        while True:
            coords = obtener_coordenadas(f"Posición inicial para el Monstruo {monstruo.id} (x,y,z): ", n)
            if mundo.agregar_entidad(monstruo, *coords):
                print(f"Monstruo {monstruo.id} agregado en la posición {coords}.")
                break
    
    # 5. Finalización y visualización
    print("\n--- Configuración Inicial Completa ---")
    for i in range(n):
        mundo.visualizar_capa(i)

if __name__ == "__main__":
    main()