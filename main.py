from agentes.simulation import SimulacionEnergetica

if __name__ == "__main__":
    """Punto de entrada principal del sistema de simulación energética 3D."""

    simulacionE2 = SimulacionEnergetica(
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

    simulacionE1 = SimulacionEnergetica(
        N=6,  # mismo tamaño
        Nrobots=2,  # igual que el intermedio
        Nmonstruos=2,  # igual que el intermedio
        ticks=100,  # un poco menos: entorno más simple
        K_monstruo=999,  # monstruos prácticamente inmóviles
        seed=42,  # misma semilla para comparabilidad
        Pfree=0.95,  # + espacios libres → menos colisiones
        Psoft=0.05,  # - obstáculos
        p_movimiento=0.05  # ~0: elimina el azar en los adversarios
    )

    simulacionE3 = SimulacionEnergetica(
        N=6,  # mismo tamaño
        Nrobots=2,  # igual que el intermedio
        Nmonstruos=2,  # igual que el intermedio
        ticks=200,  # más largo: más interacción dinámica
        K_monstruo=2,  # monstruos actúan con mayor frecuencia
        seed=42,  # misma semilla para comparabilidad
        Pfree=0.7,  # un poco menos de libres que el intermedio
        Psoft=0.3,  # un poco más de obstáculos (sin ser extremo)
        p_movimiento=0.9  # alta movilidad adversaria
    )

    # Ejecución de la simulación
    simulacionE2.ejecutar(delay=0.2)
    #simulacion.ejecutar_manual_3d()
