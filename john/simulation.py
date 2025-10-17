# TEST UNITARIO - Validación T5 (Frecuencias)
def test_monstruo_frecuencias():
    """
    Test para validar que el monstruo solo se activa cada K ticks.
    Cumple con validación T5 de la Fase 0.
    """
    from environment import Entorno3D  # Asumiendo implementación base
    
    # Configuración de prueba
    entorno = Entorno3D(N=5, Pfree=0.8, seed=42)
    monstruo = AgenteMonstruo(id=0, x=2, y=2, z=2, p_move=1.0)  # p_move=1 para testing
    K = 3
    
    resultados = []
    for tick in range(10):
        accion, pos = monstruo.decidir_accion(entorno, tick, K)
        resultados.append((tick, accion))
        
        if accion == 'move' and pos:
            monstruo.ejecutar_accion(accion, pos)
    
    # Verificar que solo se activa en ticks múltiplos de K
    activaciones = [tick for tick, accion in resultados if accion == 'move']
    print("Ticks de activación:", activaciones)
    
    # Todos los ticks de activación deben ser múltiplos de K
    assert all(tick % K == 0 for tick in activaciones), "Violación T5: Monstruo se activa en ticks incorrectos"
    print("Test T5 pasado: Monstruo respeta frecuencia K")

# Ejecutar test
if __name__ == "__main__":
    test_monstruo_frecuencias()