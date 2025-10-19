# ⚡ Simulación Energética 3D de Agentes Inteligentes

Este proyecto implementa una **Simulación Energética Tridimensional (N³)** donde interactúan dos tipos de entidades:

- 🤖 **Robots Racionales** (agentes materiales con memoria y razonamiento simbólico).
- 👾 **Monstruos Reflejos** (agentes energéticos sin memoria, de comportamiento aleatorio).

Ambos operan dentro de un **Entorno de Operación Energético** que cumple los principios del documento  
📘 *Diseño e Implementación de Agentes* y los **Requisitos del Agente**, priorizando un comportamiento realista,
jerárquico y determinista.

---

## 🧠 Descripción General

### 🤖 Agente Racional – Robot (`agent_robot.py`)

Agente racional con **memoria individual**, **sensores energéticos** y **efectores direccionales**.  
Actúa mediante una jerarquía de reglas deterministas y una tabla simbólica percepción–acción.

**Sensores implementados:**

- 🧭 **Giroscopio** → orientación actual del robot.
- 👁️ **Monstroscopio** → detecta monstruos en los cinco costados visibles (excepto el posterior).
- ⚡ **Energómetro** → detecta un monstruo en la misma celda.
- 🚧 **Vacuscopio** → se activa al chocar contra una Zona Vacía.
- 🤝 **Roboscanner** → detecta otro robot directamente al frente.

**Efectores implementados:**

- 🛞 **Propulsor Direccional** → avanza hacia adelante si la celda es libre.
- 🔄 **Reorientador** → rota 90° o se alinea con una dirección específica.
- 💥 **Vacuumator** → destruye el monstruo y convierte la celda en Zona Vacía, eliminando también al robot (
  autodestrucción).

**Características adicionales:**

- Jerarquía de reglas P0–P4 (Energómetro, Vacuscopio, Roboscanner, Monstroscopio, Tabla Base).
- Memoria con historial, paredes conocidas y posición anterior.
- Comunicación determinista entre robots (prioridad por ID).
- Sin aleatoriedad excepto en encuentros, según especificación.

---

### 👾 Agente Reflejo Simple – Monstruo (`agent_monster.py`)

Agente reflejo sin memoria ni aprendizaje.  
Opera con una frecuencia `K` y probabilidad de movimiento `p_movimiento`.

**Comportamiento:**

- Cada `K` ciclos energéticos, con probabilidad `p_movimiento`, intenta moverse hacia una de las **6 direcciones válidas
  ** (+X, -X, +Y, -Y, +Z, -Z).
- Solo puede desplazarse a **Zonas Libres**, nunca atraviesa **Zonas Vacías** ni bordes del entorno.
- Su acción es completamente reactiva (agente reflejo simple).

---

### 🌍 Entorno de Operación Energético (`environment.py`)

Espacio cúbico tridimensional de tamaño `N³`, conformado por:

- `0` → **Zona Libre (Pfree)** — transitable.
- `1` → **Zona Vacía (Psoft)** — bloqueada o fuera de límites.

**Características clave:**

- Borde exterior compuesto enteramente por Zonas Vacías (barrera energética).
- Generación aleatoria del entorno con parámetros `Pfree`, `Psoft` y `seed`.
- Registro, eliminación y visualización de entidades.
- Métodos para validar movimientos y detectar colisiones energéticas.

---

### 🧩 Motor de Simulación (`simulation.py`)

Coordina el ciclo de vida completo:

1. Percepción → Decisión → Acción.
2. Activación periódica de monstruos (cada `K` ciclos con `p_movimiento`).
3. Ejecución secuencial de robots racionales (1 acción por segundo).
4. Destrucción energética de monstruos y robots mediante el Vacuumator.
5. Visualización textual y gráfica por capas energéticas.

También puede exportar logs de acciones y resultados para análisis o métricas de racionalidad.

---

### 🧊 Visualizador 3D Manual (`visual_3d_manual.py`)

Interfaz **PyOpenGL** para visualizar el entorno energético tridimensional.  
Permite avanzar manualmente los ciclos con la barra espaciadora.

**Controles principales:**

- `ESPACIO` → Avanza un tick de simulación.
- `W / S` → Zoom in / out.
- Arrastrar con el mouse → rotar el entorno.
- `ESC` → salir de la simulación.

Representación visual:

- 🟥 Robots racionales.
- 🟦 Monstruos reflejos.
- ⬜ Zonas Libres (translúcidas).
- ⬛ Zonas Vacías (bloqueadas).

---

## 🚀 Ejecución

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Ejecutar la simulación automática

```bash
python main.py
```

Por defecto, ejecuta la simulación con:

- N = 6
- 2 Robots
- 2 Monstruos
- 10 ciclos energéticos (`ticks`)
- Frecuencia de monstruo `K = 3`
- Semilla reproducible `seed = 42`

### 3️⃣ (Opcional) Modo manual 3D

Descomenta en `main.py`:

```python
# simulacion.ejecutar(delay=0.2)
simulacion.ejecutar_manual_3d()
```

y visualiza el entorno en 3D interactivo.

---

## 📁 Estructura del Proyecto

```
agentes3d/
│
├── agentes/
│   ├── __init__.py
│   ├── agent_monster.py        # Agente reflejo simple (Monstruo)
│   ├── agent_robot.py          # Agente racional (Robot)
│   ├── environment.py          # Entorno energético 3D
│   ├── simulation.py           # Motor de simulación
│   ├── visual_3d_manual.py     # Visualización 3D manual con PyOpenGL
│
├── main.py                     # Punto de entrada del sistema
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 🧪 Tecnologías utilizadas

- 🐍 **Python 3.10+**
- 🔢 **NumPy** – modelado del entorno 3D
- 🧠 **Programación orientada a agentes**
- 💻 **PyOpenGL + GLUT** – visualización 3D manual
- 🧩 **Estructuras simbólicas y reglas deterministas**

---

## 👥 Autores

Proyecto académico desarrollado por:

- **Jhunior Cuadros** — Desarrollo, integración y refactorización del sistema de agentes.  
- **Andrés Flores** y **John Baldeon** — Contribuciones en módulos base de los agentes.  
- **Ronald Ticona** y **Guillermo Colchado** — Apoyo en requisitos y validación funcional.

---

## 📜 Licencia

Este proyecto tiene fines **académicos** y se distribuye bajo la **licencia MIT**.
