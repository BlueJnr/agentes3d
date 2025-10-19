# visual_3d_manual.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Visualizador3DManual:
    """
    Interfaz 3D manual con PyOpenGL para visualizar el entorno energético.
    Permite avanzar la simulación paso a paso con la barra espaciadora.
    """

    def __init__(self, simulacion):
        self.simulacion = simulacion
        self.tick_actual = 0
        self.rot_x, self.rot_y = 25, -45
        self.zoom = -25
        self.mouse_last = None

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------
    def iniciar(self):
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(900, 700)
        glutCreateWindow(b"Simulacion Energetica 3D - Modo Manual")

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.07, 0.07, 0.07, 1.0)

        # Mezcla de transparencias
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # --- Iluminación 3D básica ---
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.5, 1.0, 1.0, 0.0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.9, 0.9, 0.9, 1.0])

        glutDisplayFunc(self._dibujar)
        glutIdleFunc(self._loop)
        glutKeyboardFunc(self._teclas)
        glutMouseFunc(self._mouse)
        glutMotionFunc(self._rotar_mouse)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.3, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

        glutMainLoop()

    # ------------------------------------------------------------------
    # Dibujar escena completa
    # ------------------------------------------------------------------
    def _dibujar(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        glTranslatef(-self.simulacion.N / 2, -self.simulacion.N / 2, -self.simulacion.N / 2)

        # 1️⃣ Dibujar entorno (zonas)
        self._dibujar_entorno()

        # 2️⃣ Dibujar agentes (color plano)
        self._dibujar_agentes()

        # 3️⃣ Rejilla base
        self._dibujar_rejilla()

        glutSwapBuffers()

    # ------------------------------------------------------------------
    # Dibujar entorno
    # ------------------------------------------------------------------
    def _dibujar_entorno(self):
        """
        Dibuja el entorno 3D:
          - Zonas Vacías → gris opaco
          - Zonas Libres → verde translúcido (sin escribir en profundidad)
        """
        N = self.simulacion.N
        for x in range(N):
            for y in range(N):
                for z in range(N):
                    tipo = self.simulacion.entorno.grid[x, y, z]

                    if tipo == 1:  # ZONA_VACIA
                        glEnable(GL_LIGHTING)
                        glDepthMask(GL_TRUE)
                        glColor4f(0.55, 0.55, 0.55, 1.0)
                        self._cubo(x, y, z, solid=True)

                    else:  # ZONA_LIBRE
                        glDisable(GL_LIGHTING)
                        glEnable(GL_BLEND)
                        glDepthMask(GL_FALSE)
                        glColor4f(0.2, 0.8, 0.2, 0.2)
                        self._cubo(x, y, z, solid=True)
                        glDepthMask(GL_TRUE)
                        glDisable(GL_BLEND)
                        glEnable(GL_LIGHTING)

    # ------------------------------------------------------------------
    # Dibujar agentes
    # ------------------------------------------------------------------
    def _dibujar_agentes(self):
        """Dibuja robots y monstruos con colores planos y siempre visibles."""
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)  # no escribe profundidad para que no se mezclen con cubos translúcidos

        # Robots → rojo brillante
        glColor4f(1.0, 0.2, 0.2, 1.0)
        for robot in self.simulacion.entorno.robots:
            glPushMatrix()
            glTranslatef(robot.x + 0.5, robot.y + 0.5, robot.z + 0.5)
            glScalef(0.92, 0.92, 0.92)
            glutSolidCube(1.0)
            glPopMatrix()

            # 🔸 Si el robot tiene orientación, dibujar flecha
            if hasattr(robot, "orientacion"):
                self._dibujar_orientacion(robot)

        # Monstruos → azul brillante
        glColor4f(0.2, 0.5, 1.0, 1.0)
        for m in self.simulacion.entorno.monstruos:
            glPushMatrix()
            glTranslatef(m.x + 0.5, m.y + 0.5, m.z + 0.5)
            glScalef(0.92, 0.92, 0.92)
            glutSolidSphere(0.6, 20, 20)
            glPopMatrix()

        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------------------
    # Dibujar orientación (flecha amarilla)
    # ------------------------------------------------------------------
    def _dibujar_orientacion(self, robot):
        """Dibuja una flecha amarilla indicando la orientación del robot (con punta rotada correctamente)."""
        orientaciones = {
            "+X": (1, 0, 0), "-X": (-1, 0, 0),
            "+Y": (0, 1, 0), "-Y": (0, -1, 0),
            "+Z": (0, 0, 1), "-Z": (0, 0, -1)
        }

        if robot.orientacion not in orientaciones:
            return

        dx, dy, dz = orientaciones[robot.orientacion]
        base = (robot.x + 0.5, robot.y + 0.5, robot.z + 0.5)
        punta = (base[0] + dx * 0.6, base[1] + dy * 0.6, base[2] + dz * 0.6)

        # Guardar estado
        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.0)
        glLineWidth(3.0)

        # Línea direccional
        glBegin(GL_LINES)
        glVertex3f(*base)
        glVertex3f(*punta)
        glEnd()

        # 🔺 Dibuja un cono orientado correctamente según (dx, dy, dz)
        glPushMatrix()
        glTranslatef(*punta)

        # Determinar rotación
        if dx == 1:  # +X
            glRotatef(90, 0, 1, 0)
        elif dx == -1:  # -X
            glRotatef(-90, 0, 1, 0)
        elif dy == 1:  # +Y
            glRotatef(-90, 1, 0, 0)
        elif dy == -1:  # -Y
            glRotatef(90, 1, 0, 0)
        elif dz == -1:  # -Z
            glRotatef(180, 0, 1, 0)

        glutSolidCone(0.08, 0.2, 8, 8)
        glPopMatrix()

        glPopAttrib()

    # ------------------------------------------------------------------
    # Dibujar cubo unitario
    # ------------------------------------------------------------------
    def _cubo(self, x, y, z, solid=False):
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, z + 0.5)

        if solid:
            glutSolidCube(1.0)
            glColor3f(0.15, 0.15, 0.15)
            glutWireCube(1.02)
        else:
            glutWireCube(1.0)
        glPopMatrix()

    # ------------------------------------------------------------------
    # Rejilla de referencia
    # ------------------------------------------------------------------
    def _dibujar_rejilla(self):
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        N = self.simulacion.N
        for i in range(N + 1):
            glVertex3f(i, 0, 0)
            glVertex3f(i, N, 0)
            glVertex3f(0, i, 0)
            glVertex3f(N, i, 0)
        glEnd()
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------------------
    # Render loop
    # ------------------------------------------------------------------
    def _loop(self):
        glutPostRedisplay()

    # ------------------------------------------------------------------
    # Controles
    # ------------------------------------------------------------------
    def _teclas(self, key, x, y):
        if key == b" ":
            self._tick()
        elif key == b"\x1b":  # ESC
            print("\n🚪 Saliendo de la simulación...")
            sys.exit(0)
        elif key == b"w":
            self.zoom += 1
        elif key == b"s":
            self.zoom -= 1

    def _mouse(self, button, state, x, y):
        if state == GLUT_DOWN:
            self.mouse_last = (x, y)
        else:
            self.mouse_last = None

    def _rotar_mouse(self, x, y):
        if self.mouse_last:
            dx = x - self.mouse_last[0]
            dy = y - self.mouse_last[1]
            self.rot_x += dy * 0.5
            self.rot_y += dx * 0.5
            self.mouse_last = (x, y)

    # ------------------------------------------------------------------
    # Tick manual
    # ------------------------------------------------------------------
    def _tick(self):
        print(f"\n=== Tick manual {self.tick_actual} ===")

        # Monstruos reflejo
        for monstruo in list(self.simulacion.entorno.monstruos):
            evento = monstruo.percibir_decidir_actuar(
                self.tick_actual, self.simulacion.entorno, self.simulacion.K_monstruo
            )
            if evento["exito"]:
                print(f"👾 Monstruo {monstruo.id} → {evento['accion']} → {evento['resultado']['nueva_pos']}")
            else:
                print(f"👾 Monstruo {monstruo.id} inactivo.")

        # Robots racionales
        for robot in list(self.simulacion.entorno.robots):
            evento = robot.percibir_decidir_actuar(
                self.tick_actual,
                self.simulacion.entorno,
                self.simulacion.entorno.robots,
                self.simulacion.entorno.monstruos,
            )
            print(f"🤖 Robot {robot.id} → {evento['accion']} ({evento['razon']})")

            if evento["accion"] == "VACUUMATOR" and evento["exito"]:
                print(f"💥 Robot {robot.id} destruido por Vacuumator.")
                self.simulacion.entorno.eliminar_robot(robot.id)

        self.tick_actual += 1
