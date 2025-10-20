# visual_3d_manual.py
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Visualizador3DManual:
    """Interfaz OpenGL para visualizar y avanzar la simulación 3D paso a paso."""

    def __init__(self, simulacion):
        """Inicializa parámetros de cámara, rotación y control manual."""
        self.simulacion = simulacion
        self.tick_actual = 0
        self.rot_x, self.rot_y = 25, -45
        self.zoom = -25
        self.mouse_last = None

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------
    def iniciar(self):
        """Configura la ventana, iluminación y bucle principal de OpenGL."""
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(900, 700)
        glutCreateWindow(b"Simulacion Energetica 3D - Modo Manual")

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.07, 0.07, 0.07, 1.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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
    # Render principal
    # ------------------------------------------------------------------
    def _dibujar(self):
        """Renderiza el entorno, los agentes y la rejilla base."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0, 0, self.zoom)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        glTranslatef(-self.simulacion.N / 2, -self.simulacion.N / 2, -self.simulacion.N / 2)

        self._dibujar_entorno()
        self._dibujar_agentes()
        self._dibujar_rejilla()

        glutSwapBuffers()

    # ------------------------------------------------------------------
    # Entorno
    # ------------------------------------------------------------------
    def _dibujar_entorno(self):
        """Dibuja las zonas libres (verde translúcido) y vacías (gris opaco)."""
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
    # Agentes
    # ------------------------------------------------------------------
    def _dibujar_agentes(self):
        """Dibuja robots (rojos) y monstruos (azules) activos en el entorno."""
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)

        # Robots
        glColor4f(1.0, 0.2, 0.2, 1.0)
        for robot in self.simulacion.entorno.robots:
            if not getattr(robot, "activo", True):
                continue
            glPushMatrix()
            glTranslatef(robot.x + 0.5, robot.y + 0.5, robot.z + 0.5)
            glScalef(0.92, 0.92, 0.92)
            glutSolidCube(1.0)
            glPopMatrix()
            if hasattr(robot, "orientacion"):
                self._dibujar_orientacion(robot)

        # Monstruos
        glColor4f(0.2, 0.5, 1.0, 1.0)
        for m in self.simulacion.entorno.monstruos:
            if not getattr(m, "activo", True):
                continue
            glPushMatrix()
            glTranslatef(m.x + 0.5, m.y + 0.5, m.z + 0.5)
            glScalef(0.92, 0.92, 0.92)
            glutSolidSphere(0.6, 20, 20)
            glPopMatrix()

        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_LIGHTING)

    def _dibujar_orientacion(self, robot):
        """Dibuja una flecha amarilla indicando la orientación actual del robot."""
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

        glPushAttrib(GL_ALL_ATTRIB_BITS)
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 1.0, 0.0)
        glLineWidth(3.0)

        glBegin(GL_LINES)
        glVertex3f(*base)
        glVertex3f(*punta)
        glEnd()

        glPushMatrix()
        glTranslatef(*punta)

        if dx == 1:
            glRotatef(90, 0, 1, 0)
        elif dx == -1:
            glRotatef(-90, 0, 1, 0)
        elif dy == 1:
            glRotatef(-90, 1, 0, 0)
        elif dy == -1:
            glRotatef(90, 1, 0, 0)
        elif dz == -1:
            glRotatef(180, 0, 1, 0)

        glutSolidCone(0.08, 0.2, 8, 8)
        glPopMatrix()
        glPopAttrib()

    # ------------------------------------------------------------------
    # Utilitarios de dibujo
    # ------------------------------------------------------------------
    def _cubo(self, x, y, z, solid=False):
        """Dibuja un cubo unitario en las coordenadas indicadas."""
        glPushMatrix()
        glTranslatef(x + 0.5, y + 0.5, z + 0.5)
        if solid:
            glutSolidCube(1.0)
            glColor3f(0.15, 0.15, 0.15)
            glutWireCube(1.02)
        else:
            glutWireCube(1.0)
        glPopMatrix()

    def _dibujar_rejilla(self):
        """Dibuja una rejilla plana de referencia sobre el plano XY."""
        glDisable(GL_LIGHTING)
        glColor3f(0.3, 0.3, 0.3)
        glBegin(GL_LINES)
        N = self.simulacion.N
        for i in range(N + 1):
            glVertex3f(i, 0, 0);
            glVertex3f(i, N, 0)
            glVertex3f(0, i, 0);
            glVertex3f(N, i, 0)
        glEnd()
        glEnable(GL_LIGHTING)

    # ------------------------------------------------------------------
    # Controles
    # ------------------------------------------------------------------
    def _loop(self):
        """Fuerza el redibujado continuo de la escena."""
        glutPostRedisplay()

    def _teclas(self, key, x, y):
        """Control de teclas: espacio=avanzar, W/S=zoom, ESC=salir."""
        if key == b" ":
            self._tick()
        elif key == b"\x1b":
            print("\n🚪 Saliendo de la simulación...")
            sys.exit(0)
        elif key == b"w":
            self.zoom += 1
        elif key == b"s":
            self.zoom -= 1

    def _mouse(self, button, state, x, y):
        """Captura el clic del mouse para rotación de cámara."""
        if state == GLUT_DOWN:
            self.mouse_last = (x, y)
        else:
            self.mouse_last = None

    def _rotar_mouse(self, x, y):
        """Permite rotar la cámara con el arrastre del mouse."""
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
        """Ejecuta un paso manual de simulación y actualiza el entorno."""
        print(f"\n{'=' * 60}")
        print(f"⚙️  [Tick {self.tick_actual}] Ejecución manual")
        print(f"{'=' * 60}")

        # Monstruos
        print("\n👾 MONSTRUOS REFLEJO:")
        for m in [m for m in self.simulacion.entorno.monstruos if getattr(m, "activo", True)]:
            evento = m.percibir_decidir_actuar(self.tick_actual, self.simulacion.entorno, self.simulacion.K_monstruo)
            if evento["exito"]:
                print(f"  👾 [Monstruo {m.id}] Acción: {evento['accion']:<12} → Nueva pos: ({m.x}, {m.y}, {m.z})")
            else:
                print(f"  💤 [Monstruo {m.id}] Inactivo → {evento.get('razon', 'sin movimiento')}")

        # Robots
        print("\n🤖 ROBOTS RACIONALES:")
        for r in [r for r in self.simulacion.entorno.robots if getattr(r, 'activo', True)]:
            evento = r.percibir_decidir_actuar(self.tick_actual, self.simulacion.entorno)
            razon = evento.get("razon", "sin motivo")
            exito = "✅" if evento.get("exito", False) else "❌"
            print(f"  🤖 [Robot {r.id}] Acción: {evento['accion']:<12} → {exito} | Regla: {razon}")
            print(f"     📍 Posición actual: ({r.x}, {r.y}, {r.z})")

            if evento["accion"] == "VACUUMATOR" and evento["exito"]:
                print(f"     ⚠️ [Robot {r.id}] se autodestruye con Vacuumator.")

        print(f"\n✅ [Tick {self.tick_actual}] Finalizado.\n")
        self.tick_actual += 1
