# main.py
from agentes.simulation import Simulacion

if __name__ == "__main__":
    sim = Simulacion(N=6, n_robots=2, n_monstruos=2, ticks=10, K_monstruo=3, seed=42)
    sim.ejecutar(delay=0.2)
