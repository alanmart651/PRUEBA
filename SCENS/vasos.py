import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import iluminacion as luz
from RESOURCES import visual as v

# Túnel (vaso sanguíneo) a lo largo de Z: radio R con el eje a altura CY, medio largo LARGO
R = 10.4
CY = 2.0
LARGO = 10.0

_lista = None
_rng = random.Random(7)

# Células que fluyen por el vaso: x, y, desfase, velocidad, giro, tipo
_celulas = []
for _i in range(34):
    _x = _rng.uniform(-9.0, 9.0)
    _y = _rng.uniform(0.8, 5.0) if abs(_x) > 7.5 else _rng.uniform(3.2, 7.5)
    _celulas.append({"x": _x, "y": _y, "fase": _rng.uniform(0, 2 * LARGO), "vel": _rng.uniform(2.5, 5.5),
                     "giro": _rng.uniform(30, 90), "tipo": "eritro" if _i < 22 else "plaqueta"})
_plasma = [(_rng.uniform(-9.5, 9.5), _rng.uniform(0.5, 8.0), _rng.uniform(0, 2 * LARGO), _rng.uniform(4.0, 8.0))
           for _ in range(60)]
# Líneas de corriente sobre el piso: x, desfase, velocidad, largo, ancho
_corrientes = [(_rng.uniform(-9.5, 9.5), _rng.uniform(0, 2 * LARGO), _rng.uniform(5.0, 10.0),
                _rng.uniform(2.5, 5.0), _rng.uniform(0.12, 0.3)) for _ in range(44)]


# Inicia: geometría fija del túnel y del piso (se compila una sola vez)
def _construir():
    lista = glGenLists(1)
    glNewList(lista, GL_COMPILE)
    th0 = -math.asin(CY / R)
    th1 = math.pi - th0
    nt, nz = 36, 20

    # Pared del vaso (endotelio azulado con mosaico de células)
    for i in range(nt):
        glBegin(GL_QUAD_STRIP)
        for j in range(nz + 1):
            z = -LARGO + 2 * LARGO * j / nz
            for di in (0, 1):
                a = th0 + (th1 - th0) * (i + di) / nt
                k = 0.80 + 0.20 * math.sin((i + di) * 1.9 + j * 1.3) * math.sin(j * 0.7 + (i + di) * 0.5)
                glColor3f(0.30 * k, 0.36 * k, 0.66 * k)
                glNormal3f(-math.cos(a), -math.sin(a), 0.0)
                glVertex3f(R * math.cos(a), CY + R * math.sin(a), z)
        glEnd()

    # Piso (mosaico de células endoteliales)
    ancho = R * math.cos(th0)
    nx = 14
    glNormal3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    for i in range(nx):
        for j in range(nz):
            k = 0.78 + 0.22 * (((i + j) % 2) * 0.5 + 0.5 * math.sin(i * 1.7 + j * 2.3))
            glColor3f(0.20 * k, 0.30 * k, 0.56 * k)
            x0, x1 = -ancho + 2 * ancho * i / nx, -ancho + 2 * ancho * (i + 1) / nx
            z0, z1 = -LARGO + 2 * LARGO * j / nz, -LARGO + 2 * LARGO * (j + 1) / nz
            glVertex3f(x0, 0.0, z0)
            glVertex3f(x1, 0.0, z0)
            glVertex3f(x1, 0.0, z1)
            glVertex3f(x0, 0.0, z1)
    glEnd()

    # Fondo oscuro del vaso
    glColor3f(0.02, 0.03, 0.08)
    glNormal3f(0.0, 0.0, 1.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(0.0, CY, -LARGO)
    for i in range(41):
        a = i * 6.2832 / 40
        glVertex3f(R * math.cos(a), max(0.0, CY + R * math.sin(a)), -LARGO)
    glEnd()
    glEndList()
    return lista


# Inicia: eritrocito decorativo que flota en la corriente
def _eritrocito(t, c):
    z = ((c["fase"] + t * c["vel"]) % (2 * LARGO)) - LARGO
    glPushMatrix()
    glTranslatef(c["x"], c["y"] + math.sin(t * 1.3 + c["fase"]) * 0.25, z)
    glRotatef((t * c["giro"]) % 360.0, 0.3, 1.0, 0.2)
    glColor3f(0.82, 0.07, 0.11)
    glutSolidTorus(0.16, 0.34, 8, 14)
    glScalef(1.0, 1.0, 0.45)
    glColor3f(0.64, 0.04, 0.09)
    glutSolidSphere(0.4, 10, 8)
    glPopMatrix()


# Inicia: plaqueta decorativa
def _plaqueta(t, c):
    z = ((c["fase"] + t * c["vel"]) % (2 * LARGO)) - LARGO
    glPushMatrix()
    glTranslatef(c["x"], c["y"], z)
    glScalef(1.0, 0.55, 0.8)
    glColor3f(0.95, 0.85, 0.80)
    glutSolidSphere(0.16, 8, 8)
    glPopMatrix()


# Inicia: líneas de corriente que recorren el piso hacia la cámara
def _corriente(t):
    v.iniciar_aditivo()
    for x0, fase, vel, largo, ancho in _corrientes:
        cabeza = ((fase + t * vel) % (2 * LARGO)) - LARGO
        glBegin(GL_QUAD_STRIP)
        for i in range(7):
            z = cabeza - largo * (1.0 - i / 6.0) * 1.0
            x = x0 + 0.35 * math.sin(z * 0.7 + fase)
            alfa = 0.55 * (i / 6.0) ** 1.5
            glColor4f(0.45, 0.9, 1.0, alfa)
            glVertex3f(x - ancho, 0.04, z)
            glVertex3f(x + ancho, 0.04, z)
        glEnd()
    v.terminar_transparencia()


# Inicia: dibujo del escenario del vaso sanguíneo
def draw_vessel_room(t):
    global _lista
    if _lista is None:
        _lista = _construir()
    latido = luz.pulso_latido(t)

    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    # La pared "late" un poco con el corazón; aspecto húmedo con brillo especular alto
    glPushMatrix()
    s = 1.0 + 0.012 * latido
    glScalef(s, s, 1.0)
    v.material(80.0, 0.7, (0.0, 0.03 + 0.05 * latido, 0.08 + 0.06 * latido))
    glCallList(_lista)
    glPopMatrix()

    # Células en la corriente (el flujo va hacia la cámara)
    v.material(60.0, 0.6)
    for c in _celulas:
        if c["tipo"] == "eritro":
            _eritrocito(t, c)
        else:
            _plaqueta(t, c)
    v.material(48.0, 0.35)

    # Corriente en el piso
    _corriente(t)

    # Plasma: partículas brillantes que corren con la sangre
    v.iniciar_aditivo()
    glEnable(GL_POINT_SMOOTH)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    for x, y, f, vel in _plasma:
        z = ((f + t * vel) % (2 * LARGO)) - LARGO
        glColor4f(0.5, 0.9, 1.0, 0.6)
        glVertex3f(x, y, z)
    glEnd()
    v.terminar_transparencia()

    glPopMatrix()
