# TEST ESPECÍFICO - MOVIMIENTO ALEATORIO Y FRECUENCIA K
def test_movimiento_aleatorio_monstruo():
    """
    Test comprehensivo del movimiento aleatorio cada K segundos.
    Valida especificaciones estrictas de la Fase 0.
    """
    from environment import Entorno3D
    import random

    # Configurar semilla para reproducibilidad
    random.seed(42)
    entorno = Entorno3D(N=5, Pfree=0.9, seed=42)  # Alto Pfree para movilidad
    K = 3
    p_move = 0.8

    # Crear monstruo en posición central
    monstruo = AgenteMonstruo(id=1, x=2, y=2, z=2, p_move=p_move)

    print(" TEST: Movimiento Aleatorio Monstruo (K=3, p_move=0.8)")
    print("=" * 50)

    # Simular 12 ticks (4 ciclos completos de K=3)
    resultados = []
    for tick in range(12):
        log = monstruo.ciclo_reflejo_simple(entorno, tick, K)
        resultados.append(log)

        # Mostrar resultado del tick
        accion = log['action']
        resultado = log['result']
        pos = log['nueva_posicion']

        estado = f"Tick {tick:2d}: {accion:4s} -> {resultado:12s} Pos{pos}"
        if tick % K == 0:
            estado += " [TICK ACTIVACIÓN]"
        print(estado)

    print("\n" + "=" * 50)

    # ANÁLISIS DE RESULTADOS
    activaciones = [r for r in resultados if r['tick'] % K == 0]
    movimientos = [r for r in resultados if r['action'] == 'move']
    inactivos = [r for r in resultados if r['action'] == 'idle']

    print(f" ESTADÍSTICAS:")
    print(f"   • Ticks totales: {len(resultados)}")
    print(f"   • Ticks activación: {len(activaciones)} (cada K={K})")
    print(f"   • Movimientos realizados: {len(movimientos)}")
    print(f"   • Inactivos: {len(inactivos)}")
    print(f"   • Tasa movimiento: {len(movimientos) / len(activaciones):.1%}")

    # VALIDACIONES AUTOMÁTICAS
    print(f"\n VALIDACIONES:")

    # 1. Validar T5: Solo se activa en ticks múltiplos de K
    ticks_movimiento = [r['tick'] for r in movimientos]
    solo_ticks_K = all(tick % K == 0 for tick in ticks_movimiento)
    print(f"   • T5 - Solo activa en ticks K: {solo_ticks_K} {ticks_movimiento}")

    # 2. Validar que nunca sale de límites
    posiciones = [(r['x'], r['y'], r['z']) for r in resultados]
    dentro_limites = all(0 <= x < 5 and 0 <= y < 5 and 0 <= z < 5 for x, y, z in posiciones)
    print(f"   • T2 - Siempre en [0..4]³: {dentro_limites}")

    # 3. Validar que solo se mueve a celdas válidas
    movimientos_validos = all(r['result'] in ['move_ok', 'idle'] for r in resultados)
    print(f"   • Solo movimientos válidos: {movimientos_validos}")

    # 4. Mostrar distribución de movimientos
    print(f"\n DISTRIBUCIÓN ALEATORIA:")
    stats = monstruo.obtener_estadisticas()
    print(f"   • Movimientos: {stats['movimientos_realizados']}")
    print(f"   • Tasa activación real: {stats['tasa_activacion']:.1%}")
    print(f"   • Posición final: {stats['posicion_actual']}")

    assert solo_ticks_K, " FALLA T5: Monstruo se activó en tick incorrecto"
    assert dentro_limites, " FALLA T2: Monstruo salió de límites"
    print("\n TODAS LAS VALIDACIONES PASADAS")


# Ejecutar test de movimiento aleatorio
if __name__ == "__main__":
    test_movimiento_aleatorio_monstruo()
