import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

_quad = None


def _get_quad():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
    return _quad


def _plano(origen, u, v, nu, nv, normal):
    ox, oy, oz = origen
    glNormal3f(*normal)
    glBegin(GL_QUADS)
    for i in range(nu):
        for j in range(nv):
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                a = (i + di) / nu
                b = (j + dj) / nv
                glVertex3f(ox + u[0] * a + v[0] * b,
                           oy + u[1] * a + v[1] * b,
                           oz + u[2] * a + v[2] * b)
    glEnd()


def draw_moms_heart_room():
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    t = time.time()
    quad = _get_quad()

    #THE WOMB
    color_carne = (0.6, 0.1, 0.15)

    # Piso
    glColor3f(*color_carne)
    _plano((-10, 0, -10), (20, 0, 0), (0, 0, 20), 16, 16, (0, 1, 0))

    # Pared Trasera
    glColor3f(color_carne[0]*0.7, color_carne[1]*0.7, color_carne[2]*0.7)
    _plano((-10, 0, -10), (20, 0, 0), (0, 6, 0), 16, 5, (0, 0, 1))

    # Paredes Laterales
    glColor3f(color_carne[0]*0.5, color_carne[1]*0.5, color_carne[2]*0.5)
    _plano((-10, 0, -10), (0, 0, 20), (0, 6, 0), 16, 5, (1, 0, 0))
    _plano((10, 0, -10), (0, 0, 20), (0, 6, 0), 16, 5, (-1, 0, 0))

    # Puntos del piso
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.05, 0.05)
    glPointSize(5.0)
    glBegin(GL_POINTS)
    for x in range(-8, 9, 3):
        for z in range(-8, 9, 3):
            px = x + math.sin(x*z) * 1.5
            pz = z + math.cos(x*z) * 1.5
            glVertex3f(px, 0.02, pz)
    glEnd()
    if con_luz:
        glEnable(GL_LIGHTING)

    #CORAZÓN CENTRAL
    glPushMatrix()
    latido = 1.0 + abs(math.sin(t * 4.0)) * 0.15

    glTranslatef(0.0, 4.0, 0.0)
    #VENAS
    glColor3f(0.4, 0.1, 0.3)
    glPushMatrix()
    glTranslatef(0.0, 2.0, 0.0)
    glRotatef(90, 1, 0, 0)
    gluCylinder(quad, 0.6, 0.6, 2.5, 15, 5)
    glPushMatrix(); glTranslatef(0.8, 0.3, 0.0); gluCylinder(quad, 0.2, 0.2, 2.5, 10, 2); glPopMatrix()
    glPushMatrix(); glTranslatef(-0.7, -0.4, 0.0); gluCylinder(quad, 0.15, 0.15, 2.5, 10, 2); glPopMatrix()
    glPushMatrix(); glTranslatef(0.0, -0.8, 0.0); gluCylinder(quad, 0.25, 0.25, 2.5, 10, 2); glPopMatrix()
    glPopMatrix()

    glScalef(latido, latido, latido)
    glColor3f(0.8, 0.2, 0.3)
    # El corazón brilla un poco por sí mismo
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.30, 0.03, 0.05, 1.0))

    # Lóbulo Izquierdo
    glPushMatrix()
    glTranslatef(-0.8, 0.0, 0.0)
    glScalef(1.2, 1.5, 1.2)
    glutSolidSphere(1.0, 20, 20)
    glPopMatrix()

    # Lóbulo Derecho
    glPushMatrix()
    glTranslatef(0.8, 0.0, 0.0)
    glScalef(1.2, 1.5, 1.2)
    glutSolidSphere(1.0, 20, 20)
    glPopMatrix()

    # Punta
    glPushMatrix()
    glTranslatef(0.0, -1.0, 0.0)
    glRotatef(90, 1, 0, 0)
    glutSolidCone(1.6, 2.5, 20, 10)
    glPopMatrix()

    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, (0.0, 0.0, 0.0, 1.0))
    glPopMatrix()

    #LAGRIMAS FLOTANTES
    posiciones_sangre = [
        (-4.0, 1.0, -2.0), (3.0, 1.5, -3.0), (-6.0, 0.8, 2.0),
        (4.0, 1.2, 4.0), (-2.0, 0.5, 4.0), (6.0, 2.0, 0.0),
        (2.5, 1.8, 5.0), (-3.0, 2.5, -5.0), (5.0, 0.5, -6.0)
    ]

    glColor3f(0.9, 0.1, 0.1)
    for i, (px, py, pz) in enumerate(posiciones_sangre):
        glPushMatrix()
        flote = math.sin(t * 2.0 + i) * 0.2
        glTranslatef(px, py + flote, pz)
        glutSolidSphere(0.4, 15, 15)

        glColor3f(1.0, 1.0, 1.0)
        glPushMatrix()
        glTranslatef(-0.15, 0.15, 0.3)
        glutSolidSphere(0.1, 10, 10)
        glPopMatrix()
        glColor3f(0.9, 0.1, 0.1)

        glPopMatrix()

    glPopMatrix()
