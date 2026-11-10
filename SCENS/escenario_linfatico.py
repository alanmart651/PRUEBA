import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import visual as v

_lista = None   # paredes y piso fijos (se compilan una sola vez)
_quad = None
_rng = random.Random(23)

# Folículos linfoides (nódulos dorados) pegados a las paredes: x, y, z, rotación
_foliculos = []
for _x in (-7.0, -3.5, 0.0, 3.5, 7.0):
    for _y in (1.7, 4.2):
        _foliculos.append((_x, _y, -9.55, 0.0))
for _z in (-6.5, -2.2, 2.2, 6.5):
    for _y in (1.7, 4.2):
        _foliculos.append((-9.55, _y, _z, 90.0))
        _foliculos.append((9.55, _y, _z, 90.0))

# Moléculas de ATP brillantes que flotan: x, z, desfase, velocidad
_atp = [(_rng.uniform(-9.0, 9.0), _rng.uniform(-9.0, 7.0), _rng.uniform(0.0, 8.0), _rng.uniform(0.35, 0.8))
        for _ in range(22)]
# Polvo dorado en suspensión: x, z, desfase, velocidad
_polvo = [(_rng.uniform(-9.8, 9.8), _rng.uniform(-9.8, 9.8), _rng.uniform(0.0, 8.0), _rng.uniform(0.2, 0.6))
          for _ in range(130)]


def _quadric():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
    return _quad


# Inicia: relieve nodular de las paredes (el desplazamiento es 0 en las orillas)
def _relieve(a, b):
    d = 0.30 * max(0.0, math.sin(a * 22.0)) * max(0.0, math.sin(b * 9.0 + 0.4)) + 0.10 * math.sin(a * 5.0 + b * 3.0)
    return d * min(1.0, a * 8.0, (1.0 - a) * 8.0, b * 5.0)


# Inicia: color verde-oliva con brillos dorados en los nódulos
def _color(a, b, d):
    k = 0.80 + 0.20 * math.sin(a * 31.0 + b * 7.0)
    oro = max(0.0, d) * 1.6
    return (0.34 * k + 0.55 * oro, 0.46 * k + 0.40 * oro, 0.17 * k + 0.05 * oro)


# Inicia: geometría fija de la sala
def _construir():
    lista = glGenLists(1)
    glNewList(lista, GL_COMPILE)
    v.pared_relieve((-10, 0, -10), (20, 0, 0), (0, 6, 0), (0, 0, 1), 40, 14, _relieve, _color)
    v.pared_relieve((-10, 0, -10), (0, 0, 20), (0, 6, 0), (1, 0, 0), 40, 14, _relieve, _color)
    v.pared_relieve((10, 0, -10), (0, 0, 20), (0, 6, 0), (-1, 0, 0), 40, 14, _relieve, _color)

    # Piso: mosaico verde con celdas doradas (senos del ganglio)
    glNormal3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    n = 22
    for i in range(n):
        for j in range(n):
            x0, x1 = -10 + 20.0 * i / n, -10 + 20.0 * (i + 1) / n
            z0, z1 = -10 + 20.0 * j / n, -10 + 20.0 * (j + 1) / n
            k = 0.78 + 0.22 * math.sin(i * 1.7) * math.cos(j * 1.5)
            if (i * 3 + j * 5) % 7 == 0:
                glColor3f(0.62 * k, 0.52 * k, 0.16 * k)
            else:
                glColor3f(0.30 * k, 0.42 * k, 0.15 * k)
            glVertex3f(x0, 0.0, z0)
            glVertex3f(x1, 0.0, z0)
            glVertex3f(x1, 0.0, z1)
            glVertex3f(x0, 0.0, z1)
    glEnd()
    glEndList()
    return lista


# Inicia: folículos linfoides que respiran con una emisión dorada
def _dibujar_foliculos(t):
    for i, (x, y, z, rot) in enumerate(_foliculos):
        k = 0.5 + 0.5 * math.sin(t * 1.5 + i * 0.7)
        v.material(90.0, 0.7, (0.20 * k, 0.14 * k, 0.02 * k))
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(rot, 0, 1, 0)
        glScalef(1.0, 1.0, 0.45)
        glColor3f(0.92, 0.78, 0.30)
        glutSolidSphere(1.0, 14, 12)
        glScalef(0.45, 0.45, 1.1)
        glColor3f(1.0, 0.92, 0.55)
        glutSolidSphere(1.0, 10, 8)
        glPopMatrix()


# Inicia: trabéculas (columnas de tejido) en las esquinas
def _dibujar_columnas():
    v.material(50.0, 0.5)
    glColor3f(0.55, 0.62, 0.22)
    for x, z in ((-9.3, -9.3), (9.3, -9.3), (-9.3, 0.0), (9.3, 0.0)):
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(_quadric(), 0.6, 0.45, 6.0, 14, 1)
        glutSolidSphere(0.65, 12, 10)
        glPopMatrix()


# Inicia: moléculas de ATP doradas que suben lentamente (adornos altos que no se recogen;
# los ATP verdes del piso son los que sí se recogen)
def _dibujar_atp(t):
    pos = []
    v.material(90.0, 0.9, (0.30, 0.28, 0.02))
    for x, z, f, vel in _atp[:16]:
        y = 3.2 + ((f + t * vel) % 5.0)
        px, pz = x + math.sin(t * 0.6 + f) * 0.6, z + math.cos(t * 0.5 + f) * 0.6
        pos.append((px, y, pz))
        glPushMatrix()
        glTranslatef(px, y, pz)
        glRotatef((t * 50.0 + f * 40.0) % 360.0, 0, 1, 0)
        glColor3f(1.0, 0.95, 0.6)
        glutSolidSphere(0.16, 8, 8)
        for i in range(3):
            glPushMatrix()
            glTranslatef(-0.30 - i * 0.22, 0.02 * i, 0.0)
            glColor3f(1.0, 0.72, 0.15)
            glutSolidSphere(0.08, 6, 6)
            glPopMatrix()
        glPopMatrix()
    v.material(48.0, 0.35)

    # Resplandor aditivo de todas las moléculas a la vez
    v.iniciar_aditivo()
    for px, y, pz in pos:
        glPushMatrix()
        glTranslatef(px, y, pz)
        glColor4f(1.0, 0.85, 0.4, 0.13)
        glutSolidSphere(0.45, 10, 10)
        glPopMatrix()
    v.terminar_transparencia()


# Inicia: polvo dorado que flota (niebla de partículas)
def _dibujar_polvo(t):
    v.iniciar_aditivo()
    glEnable(GL_POINT_SMOOTH)
    glPointSize(2.5)
    glBegin(GL_POINTS)
    for x, z, f, vel in _polvo:
        y = ((f + t * vel) % 8.0) + 0.2
        glColor4f(1.0, 0.9, 0.45, 0.55)
        glVertex3f(x + math.sin(t * 0.4 + f) * 0.5, y, z + math.cos(t * 0.35 + f) * 0.5)
    glEnd()
    v.terminar_transparencia()


# Inicia: dibujo del ganglio linfático (centro inmunológico)
def draw_lymph_room(t):
    global _lista
    if _lista is None:
        _lista = _construir()
    respira = math.sin(t * 1.5) ** 2

    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    # Paredes y piso húmedos y brillantes; la sala respira despacio
    glPushMatrix()
    s = 1.0 + 0.012 * respira
    glScalef(s, 1.0, s)
    v.material(65.0, 0.6, (0.02 + 0.04 * respira, 0.04 + 0.05 * respira, 0.0))
    glCallList(_lista)
    glPopMatrix()
    v.material(48.0, 0.35)

    _dibujar_foliculos(t)
    _dibujar_columnas()
    v.material(48.0, 0.35)
    _dibujar_atp(t)
    _dibujar_polvo(t)

    glPopMatrix()
