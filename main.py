# main.py
from agentes.simulation import SimulacionEnergetica

if __name__ == "__main__":
    """
    Punto de entrada principal del sistema de simulación energética.

    Este módulo inicializa el Entorno de Operación Energético y
    lanza la simulación donde interactúan:
      - Robots racionales: agentes con percepción y decisión simbólica.
      - Monstruos reflejo: agentes reactivos de movimiento aleatorio.

    Cada ciclo energético representa un paso temporal en la evolución
    del sistema tridimensional.
    """

    simulacion = SimulacionEnergetica(
        N=6,  # Dimensión del entorno (N³)
        Nrobots=2,  # Número de robots racionales
        Nmonstruos=2,  # Número de monstruos reflejo
        ticks=10,  # Número de ciclos energéticos
        K_monstruo=3,  # Frecuencia de activación de monstruos
        seed=42  # Semilla para reproducibilidad
    )

    simulacion.ejecutar(delay=0.2)
