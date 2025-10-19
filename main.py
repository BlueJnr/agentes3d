# main.py
from agentes.simulation import SimulacionEnergetica

if __name__ == "__main__":
    """
    Punto de entrada principal del **Sistema de Simulación Energética**.

    Este módulo inicia la ejecución global del modelo de agentes inteligentes,
    estableciendo las condiciones iniciales del **Entorno de Operación Energético**
    y desplegando la simulación completa.

    Funciones principales:
      • Configurar la dimensión del espacio energético tridimensional (N³).
      • Definir la cantidad de agentes materiales (**robots racionales**).
      • Definir la cantidad de agentes energéticos (**monstruos reflejo**).
      • Establecer la duración del experimento en ciclos energéticos (`ticks`).
      • Fijar la frecuencia de activación de los monstruos (`K_monstruo`).
      • Controlar la semilla de aleatoriedad para reproducibilidad.

    Conceptualmente:
      Cada **Ciclo Energético** representa una transición discreta en la
      evolución del sistema tridimensional, donde los agentes perciben,
      razonan y actúan dentro del entorno energético.

    Este script constituye el **nivel de ejecución experimental** del modelo.
    """

    # Inicialización de la simulación energética principal
    simulacion = SimulacionEnergetica(
        N=6,  # Dimensión cúbica del entorno (6³)
        Nrobots=2,  # Número de Robots Racionales (agentes materiales)
        Nmonstruos=2,  # Número de Monstruos Reflejo (agentes energéticos)
        ticks=10,  # Duración total en ciclos energéticos
        K_monstruo=3,  # Frecuencia de activación de monstruos reflejo
        seed=42  # Semilla aleatoria para reproducibilidad experimental
    )

    # Ejecución del motor energético con retardo de visualización
    #simulacion.ejecutar(delay=0.2)
    # Ejecutar modo 3D manual
    simulacion.ejecutar_manual_3d()
