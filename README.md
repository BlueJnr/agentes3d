# ⚡ Simulación Energética 3D de Agentes Inteligentes

Este proyecto implementa una **Simulación Energética Tridimensional (N³)** donde interactúan **agentes inteligentes
heterogéneos** dentro de un entorno dinámico.  
El objetivo es modelar la **cooperación, racionalidad y reactividad energética** en un sistema de multiagentes.

---

## 🧩 Arquitectura del Sistema

### 🌍 Entorno de Operación Energético

El entorno define un **espacio tridimensional discreto (N×N×N)** compuesto por:

| Tipo de Zona              | Código | Descripción                                      |
|---------------------------|--------|--------------------------------------------------|
| 🟩 **Zona Libre (Pfree)** | `0`    | Espacio transitable y accesible por los agentes. |
| ⬛ **Zona Vacía (Psoft)**  | `1`    | Barrera energética o límite del entorno.         |

**Características clave:**

- Borde exterior compuesto exclusivamente por Zonas Vacías.
- Generación probabilística del entorno (`Pfree`, `Psoft`) controlada por semilla (`seed`).
- Administración centralizada del registro y posición de agentes.
- Validación topológica de colisiones y movimientos.

---

### 🤖 Agente Racional – *Robot Material*

Agente racional simbólico que utiliza **memoria**, **percepción** y **razonamiento jerárquico** para actuar en su
entorno.

#### 🔍 Sensores implementados

| Sensor                | Función                                           |
|-----------------------|---------------------------------------------------|
| 🧭 **Giroscopio**     | Indica la orientación actual.                     |
| 👁️ **Monstroscopio** | Detecta monstruos en los cinco costados visibles. |
| ⚡ **Energómetro**     | Detecta monstruos en la misma celda.              |
| 🚧 **Vacuscopio**     | Señala colisiones con zonas vacías.               |
| 🤝 **Roboscanner**    | Detecta otro robot directamente al frente.        |

#### ⚙️ Efectores implementados

| Efector                      | Acción                                                                |
|------------------------------|-----------------------------------------------------------------------|
| 🛞 **Propulsor Direccional** | Avanza hacia adelante si la celda está libre.                         |
| 🔄 **Reorientador**          | Rota 90° o se alinea con dirección específica.                        |
| 💥 **Vacuumator**            | Destruye monstruos, convierte celda en vacía y autodestruye al robot. |

#### 🧠 Inteligencia simbólica

- Basada en reglas deterministas **P0–P4**.
- Estructura de decisión:
  ```
  P0 → Energómetro
  P1 → Vacuscopio
  P2 → Roboscanner
  P3 → Monstroscopio
  P4 → Tabla base de comportamiento
  ```
- Almacenamiento de historial y orientación previa.
- Detección y evasión automática de bucles conductuales.

---

### 👾 Agente Reflejo – *Monstruo Energético*

Agente sin memoria ni razonamiento. Opera de forma aleatoria y periódica, reaccionando únicamente a su entorno
inmediato.

- Se activa cada `K` ciclos energéticos.
- Posee una **probabilidad de movimiento** `p_movimiento`.
- Solo se mueve a **Zonas Libres** y nunca atraviesa bordes ni zonas vacías.
- Modelo canónico de **agente reflejo simple** según Russell & Norvig.

---

### 🔄 Motor de Simulación Energética (`simulation.py`)

Coordina la **dinámica energética global** del sistema.

#### Ciclo principal:

1. Activación de **monstruos reflejos** cada `K` ciclos.
2. Ejecución de **robots racionales** en orden secuencial (1 acción/ciclo).
3. Actualización del entorno y visualización de la capa central.
4. Registro y trazabilidad de eventos (percepción, acción, resultado).

**Modos de ejecución:**

- ⏱️ **Automático:** iteraciones temporizadas (`delay`).
- 🧊 **Manual 3D:** avance paso a paso (controlado por el usuario).

---

### 🧊 Visualizador 3D Interactivo (`visual_3d_manual.py`)

Renderizado en tiempo real con **PyOpenGL + GLUT**.

#### 🎮 Controles principales

| Acción        | Tecla / Control     |
|---------------|---------------------|
| Avanzar tick  | `ESPACIO`           |
| Zoom in / out | `W / S`             |
| Rotar entorno | Arrastrar con mouse |
| Salir         | `ESC`               |

#### 🧱 Representación visual

| Elemento            | Color             | Descripción                 |
|---------------------|-------------------|-----------------------------|
| 🤖 Robot racional   | 🟥 Rojo           | Agente racional activo      |
| 👾 Monstruo reflejo | 🟦 Azul           | Agente energético aleatorio |
| ⬜ Zona Libre        | Verde translúcida | Espacio accesible           |
| ⬛ Zona Vacía        | Gris opaco        | Barrera o límite energético |

---

## 🚀 Ejecución del Sistema

### 1️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2️⃣ Ejecutar simulación automática

```bash
python main.py
```

Configuración por defecto:
| Parámetro | Valor | Descripción |
|------------|--------|-------------|
| `N` | 6 | Dimensión cúbica (6×6×6) |
| `Nrobots` | 2 | Robots racionales |
| `Nmonstruos` | 2 | Monstruos reflejos |
| `ticks` | 10 | Ciclos energéticos |
| `K_monstruo` | 3 | Frecuencia de activación |
| `seed` | 42 | Reproducibilidad experimental |

### 3️⃣ Modo 3D Manual (interactivo)

En `main.py` descomenta:

```python
# simulacion.ejecutar(delay=0.2)
simulacion.ejecutar_manual_3d()
```

---

## 📁 Estructura del Proyecto

```
agentes3d/
│
├── agentes/
│   ├── agent_monster.py       # Agente reflejo simple (Monstruo)
│   ├── agent_robot.py         # Agente racional (Robot)
│   ├── environment.py         # Entorno energético tridimensional
│   ├── simulation.py          # Motor de simulación energética
│   ├── visual_3d_manual.py    # Visualización 3D interactiva
│
├── main.py                    # Punto de entrada del sistema
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📊 Métricas y Extensibilidad

El sistema está diseñado para **investigación experimental en inteligencia artificial distribuida**, con soporte para
métricas y extensiones:

| Categoría                       | Descripción                                                            |
|---------------------------------|------------------------------------------------------------------------|
| 🔁 **Reproducibilidad**         | Control mediante `seed` y logging estructurado.                        |
| 📈 **Métricas de racionalidad** | Tasa de éxito de reglas, colisiones, uso de Vacuumator.                |
| 🧩 **Extensibilidad modular**   | Permite incorporar nuevos tipos de sensores o reglas.                  |
| ⚡ **Integración futura**        | Compatible con frameworks de IA simbólica o redes neuronales híbridas. |

---

## 🧪 Tecnologías Utilizadas

- 🐍 **Python 3.10+**
- 🔢 **NumPy** – modelado espacial 3D
- 💻 **PyOpenGL + GLUT** – visualización tridimensional
- 🧠 **Arquitectura de Agentes Inteligentes**
- 🧩 **Diseño basado en reglas deterministas y memoria simbólica**

---

## 👥 Autores

**Proyecto académico desarrollado por:**

- **Jhunior Cuadros** — Arquitectura, desarrollo y refactorización del sistema completo.
- **Andrés Flores** y **John Baldeon** — Implementación de módulos base de agentes.
- **Ronald Ticona** y **Guillermo Colchado** — Análisis de requisitos y validación funcional.

---

## 📜 Licencia

Este software se distribuye bajo la **Licencia MIT** con fines educativos, de investigación y demostración académica.  
Las referencias teóricas provienen del marco de agentes inteligentes propuesto por *Russell & Norvig (AI: A Modern
Approach)* y adaptado al contexto energético tridimensional.
