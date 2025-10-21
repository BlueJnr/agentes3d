from agentes.simulation import SimulacionEnergetica

if __name__ == "__main__":
    """Punto de entrada principal del sistema de simulación energética 3D."""

    simulacion = SimulacionEnergetica(
        N=6,  # Tamaño del entorno cúbico (6³)
        Nrobots=2,  # Robots racionales
        Nmonstruos=2,  # Monstruos reflejo
        ticks=150,  # Ciclos energéticos totales
        K_monstruo=3,  # Frecuencia de activación de monstruos
        seed=42  # Semilla para reproducibilidad
    )

    # Ejecución de la simulación
    # simulacion.ejecutar(delay=0.2)
    simulacion.ejecutar_manual_3d()
