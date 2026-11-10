import math
import random
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import iluminacion as luz
from RESOURCES import visual as v

_quad = None
_lista = None   # paredes y piso fijos (se compilan una sola vez)
_rng = random.Random(11)

# Eritrocitos en suspensión: base x, y, z, tamaño y fase (decorativos, no se recogen)
_suspension = [(_rng.choice((-1, 1)) * _rng.uniform(4.5, 9.0), _rng.uniform(1.2, 5.0), _rng.uniform(-9.0, 3.0),
                _rng.uniform(0.9, 1.5), _rng.uniform(0.0, 6.28)) for _ in range(26)]


def _get_quad():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
    return _quad


# Inicia: relieve muscular de las paredes (desplazamiento hacia adentro, 0 en las orillas)
def _relieve(a, b):
    d = 0.28 * math.sin(a * 19.0 + 1.3) * math.sin(b * 9.0 + 0.5) + 0.18 * math.sin(a * 7.0 + b * 5.0)
    return d * min(1.0, a * 8.0, (1.0 - a) * 8.0, b * 5.0)


# Inicia: color de las paredes: fibras musculares y venas
def _color(a, b, d):
    fibra = 0.80 + 0.20 * math.sin(a * 60.0 + math.sin(b * 4.0) * 2.0)
    vena = 1.0 if abs(math.sin(a * 9.0 + b * 2.0)) > 0.07 else 0.55
    return (0.64 * fibra * vena + 0.06 * d, 0.11 * fibra * vena, 0.15 * fibra + (0.10 if vena < 1.0 else 0.0))


def _pared(origen, u, vv, n, nu, nv):
    v.pared_relieve(origen, u, vv, n, nu, nv, _relieve, _color)


# Inicia: geometría fija de la sala
def _construir():
    lista = glGenLists(1)
    glNewList(lista, GL_COMPILE)
    _pared((-10, 0, -10), (20, 0, 0), (0, 6, 0), (0, 0, 1), 28, 12)
    _pared((-10, 0, -10), (0, 0, 20), (0, 6, 0), (1, 0, 0), 28, 12)
    _pared((10, 0, -10), (0, 0, 20), (0, 6, 0), (-1, 0, 0), 28, 12)

    # Piso: tejido con manchas de color
    glNormal3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    n = 20
    for i in range(n):
        for j in range(n):
            x0, x1 = -10 + 20.0 * i / n, -10 + 20.0 * (i + 1) / n
            z0, z1 = -10 + 20.0 * j / n, -10 + 20.0 * (j + 1) / n
            k = 0.80 + 0.20 * math.sin(i * 1.3 + 0.4) * math.sin(j * 1.1 + 1.0)
            glColor3f(0.58 * k, 0.10 * k, 0.14 * k)
            glVertex3f(x0, 0.0, z0)
            glVertex3f(x1, 0.0, z0)
            glVertex3f(x1, 0.0, z1)
            glVertex3f(x0, 0.0, z1)
    glEnd()
    glEndList()
    return lista


def draw_moms_heart_room():
    global _lista
    if _lista is None:
        _lista = _construir()
    t = time.time()
    quad = _get_quad()
    pulso = luz.pulso_latido(t)

    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    # Paredes y piso: húmedos y brillantes; las paredes laten con el corazón
    glPushMatrix()
    s = 1.0 + 0.022 * pulso
    glScalef(s, 1.0 + 0.008 * pulso, s)
    v.material(70.0, 0.55, (0.05 + 0.10 * pulso, 0.0, 0.01))
    glCallList(_lista)
    glPopMatrix()

    # Corazón central
    latido = 1.0 + pulso * 0.15
    glPushMatrix()
    glTranslatef(0.0, 4.0, 0.0)

    # Venas
    v.material(50.0, 0.4)
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
    # El corazón es muy brillante y emite un poco de luz propia al latir
    v.material(90.0, 0.8, (0.20 + 0.25 * pulso, 0.02, 0.04))

    # Lóbulo Izquierdo
    glPushMatrix()
    glTranslatef(-0.8, 0.0, 0.0)
    glScalef(1.2, 1.5, 1.2)
    glutSolidSphere(1.0, 24, 24)
    glPopMatrix()

    # Lóbulo Derecho
    glPushMatrix()
    glTranslatef(0.8, 0.0, 0.0)
    glScalef(1.2, 1.5, 1.2)
    glutSolidSphere(1.0, 24, 24)
    glPopMatrix()

    # Punta
    glPushMatrix()
    glTranslatef(0.0, -1.0, 0.0)
    glRotatef(90, 1, 0, 0)
    glutSolidCone(1.6, 2.5, 24, 10)
    glPopMatrix()
    glPopMatrix()
    v.material(48.0, 0.35)

    # Eritrocitos en suspensión: translúcidos y a media altura para no tapar el juego
    for x, y, z, tam, f in _suspension:
        px = x + math.sin(t * 0.5 + f) * 0.8
        py = y + math.sin(t * 0.7 + f * 2.0) * 0.4
        pz = z + math.cos(t * 0.45 + f) * 0.8
        v.eritrocito((px, py, pz), tam, f, t, 0.55)

    glPopMatrix()
