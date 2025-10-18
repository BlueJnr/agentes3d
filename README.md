# 🤖 Simulación de Agentes Inteligentes en un Entorno 3D

Este proyecto implementa una simulación de **agentes inteligentes** —robots y monstruos— que interactúan dentro de un **entorno tridimensional (3D)**.  
El desarrollo se basa en los principios de **agentes reflexivos** y **agentes con memoria y aprendizaje simple**, descritos en el documento *Diseño e Implementación de Agentes*.

---

## 🧠 Descripción General

### 🦾 Agente Robot (`agent_robot.py`)
Agente racional con **memoria interna**, **cinco sensores** (giroscopio, monstroscopio, vacuscopio, energómetro y roboscanner)  
y **tres efectores** (propulsor, reorientador y vacuumator).  
Su decisión sigue una **jerarquía de prioridades** y utiliza una **tabla de mapeo percepción–acción**, la cual puede ajustarse mediante aprendizaje simbólico.

### 👾 Agente Monstruo (`agent_monster.py`)
Agente reflejo simple, **sin memoria ni aprendizaje**.  
Se **activa periódicamente** y se **mueve aleatoriamente** dentro del entorno, siguiendo una probabilidad de movimiento `p_move`.

### 🌍 Entorno 3D (`environment.py`)
Espacio cúbico donde los agentes se desplazan.  
Cada celda puede ser:
- `0` → Zona Libre (transitable)  
- `1` → Zona Vacía (bloqueada)  

El entorno administra las posiciones, colisiones y visualización de los agentes.

### 🧩 Simulación (`simulation.py`)
Coordina el ciclo completo de percepción–decisión–acción de los agentes y  
controla el avance del tiempo en *ticks* de simulación.

---

## 🚀 Ejecución

1. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la simulación:

   ```bash
   python main.py
   ```

   > Asegúrate de estar en la raíz del proyecto y de usar **Python 3.10 o superior**.

---

## 📁 Estructura del Proyecto

```
agentes3d/
│
├── agentes/
│   ├── __init__.py
│   ├── agent_monster.py
│   ├── agent_robot.py
│   ├── environment.py
│   ├── simulation.py
│
├── main.py
├── README.md
├── requirements.txt
└── .gitignore

```

---

## 👥 Autores

Proyecto desarrollado en colaboración por:

- **Jhunior Cuadros**  
- **Andrés Flores**  
- **John Baldeon**
- **Ronald Ticona**
- **Guillermo Colchado**

---

## 📜 Licencia

Este proyecto tiene fines **académicos** y se distribuye bajo la **licencia MIT**.
