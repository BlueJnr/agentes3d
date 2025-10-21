from agentes.simulation import SimulacionEnergetica

if __name__ == "__main__":
    """Punto de entrada principal del sistema de simulación energética 3D."""

    simulacion = SimulacionEnergetica(
        N=6,  # Tamaño del entorno cúbico (N³)
        Nrobots=2,  # Número de robots racionales
        Nmonstruos=2,  # Número de monstruos reflejo
        ticks=150,  # Ciclos totales de ejecución de la simulación
        K_monstruo=3,  # Frecuencia de acción de los monstruos (cada K ciclos)
        seed=42,  # Semilla aleatoria para reproducibilidad
        Pfree=0.8,  # Proporción de zonas libres (transitables)
        Psoft=0.2,  # Proporción de zonas vacías (obstáculos)
        p_movimiento=0.7  # Probabilidad de movimiento de cada monstruo
    )

    # Ejecución de la simulación
    # simulacion.ejecutar(delay=0.2)
    simulacion.ejecutar_manual_3d()
