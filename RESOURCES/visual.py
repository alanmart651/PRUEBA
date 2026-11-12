import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

_quadric = None


# ---------- quadric ----------
def quadric():
    global _quadric
    if _quadric is None:
        _quadric = gluNewQuadric()
        gluQuadricNormals(_quadric, GLU_SMOOTH)
    return _quadric


def mezclar(a, b, k):
    return tuple(a[i] + (b[i] - a[i]) * k for i in range(3))


# ---------- material ----------
def material(brillo=30.0, especular=0.4, emision=(0.0, 0.0, 0.0)):
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [especular, especular, especular, 1.0])
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, brillo)
    glMaterialfv(GL_FRONT_AND_BACK, GL_EMISSION, [emision[0], emision[1], emision[2], 1.0])


# ---------- primitivas ----------
def esfera(pos, escala, color, det=16):
    glPushMatrix()
    glTranslatef(*pos)
    glScalef(*escala)
    glColor3fv(color)
    glutSolidSphere(1.0, det, det)
    glPopMatrix()


def caja(pos, escala, color, rot=(0.0, 0.0, 1.0, 0.0)):
    glPushMatrix()
    glTranslatef(*pos)
    if rot[3] != 0.0:
        glRotatef(rot[3], rot[0], rot[1], rot[2])
    glScalef(*escala)
    glColor3fv(color)
    glutSolidCube(1.0)
    glPopMatrix()


def cilindro(pos, radio, alto, color, radio_sup=None, det=16, tapa=True):
    if radio_sup is None:
        radio_sup = radio
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(-90, 1, 0, 0)
    glColor3fv(color)
    gluCylinder(quadric(), radio, radio_sup, alto, det, 1)
    if tapa:
        glTranslatef(0, 0, alto)
        gluDisk(quadric(), 0, radio_sup, det, 1)
    glPopMatrix()


def cono(pos, radio, alto, color, det=12):
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(-90, 1, 0, 0)
    glColor3fv(color)
    glutSolidCone(radio, alto, det, 2)
    glPopMatrix()


# ---------- transparencias ----------
def iniciar_aditivo():
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glDepthMask(GL_FALSE)


def terminar_transparencia():
    glPopAttrib()


# ---------- eritrocito decorativo (disco bicóncavo que flota en la escena) ----------
def eritrocito(pos, escala, fase, t, alfa=1.0):
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef((t * 40.0 + fase * 57.0) % 360.0, 0.3, 1.0, 0.2)
    glScalef(escala, escala, escala)
    glColor4f(0.82, 0.07, 0.11, alfa)
    glutSolidTorus(0.16, 0.34, 8, 14)
    glScalef(1.0, 1.0, 0.45)
    glColor4f(0.64, 0.04, 0.09, alfa)
    glutSolidSphere(0.4, 10, 8)
    glPopMatrix()


# ---------- pared con relieve ----------
# origen, ejes u y v de la pared, normal hacia adentro, divisiones, función de relieve
# relieve(a, b) -> desplazamiento y color(a, b, d) -> (r, g, b). Las normales se calculan del relieve.
def pared_relieve(origen, u, vv, n, nu, nv, relieve, color):
    lu = math.sqrt(sum(c * c for c in u))
    lv = math.sqrt(sum(c * c for c in vv))
    eps = 0.002

    def punto(a, b):
        d = relieve(a, b)
        da = (relieve(a + eps, b) - relieve(a - eps, b)) / (2 * eps * lu)
        db = (relieve(a, b + eps) - relieve(a, b - eps)) / (2 * eps * lv)
        pos = [origen[i] + u[i] * a + vv[i] * b + n[i] * d for i in range(3)]
        nor = [n[i] - da * u[i] / lu - db * vv[i] / lv for i in range(3)]
        return pos, nor, color(a, b, d)

    glBegin(GL_QUADS)
    for i in range(nu):
        for j in range(nv):
            for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
                pos, nor, col = punto((i + di) / nu, (j + dj) / nv)
                glColor3f(*col)
                glNormal3f(*nor)
                glVertex3f(*pos)
    glEnd()


# ---------- niebla ----------
def niebla(color, densidad):
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogfv(GL_FOG_COLOR, [color[0], color[1], color[2], 1.0])
    glFogf(GL_FOG_DENSITY, densidad)


def sin_niebla():
    glDisable(GL_FOG)


# ---------- halo ----------
def halo(pos, radio, color, alpha=0.35, capas=4, det=16):
    iniciar_aditivo()
    glPushMatrix()
    glTranslatef(*pos)
    for i in range(capas):
        k = (i + 1) / capas
        glColor4f(color[0], color[1], color[2], alpha * (1.0 - k * 0.8))
        glutSolidSphere(radio * (0.45 + k * 0.55), det, det)
    glPopMatrix()
    terminar_transparencia()


# ---------- aura ----------
def aura(alto, radio, color, t, intensidad=1.0):
    iniciar_aditivo()
    for i in range(12):
        ang = i * 30.0 + t * 40.0
        flama = 0.75 + 0.25 * math.sin(t * 9.0 + i * 1.7)
        glPushMatrix()
        glRotatef(ang, 0, 1, 0)
        glTranslatef(radio * 0.55, alto * 0.45, 0)
        glScalef(radio * 0.45, alto * 0.55 * flama, radio * 0.45)
        glColor4f(color[0], color[1], color[2], 0.10 * intensidad)
        glutSolidSphere(1.0, 10, 10)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0, alto * 0.5, 0)
    glScalef(radio, alto * 0.62, radio)
    glColor4f(color[0], color[1], color[2], 0.12 * intensidad)
    glutSolidSphere(1.0, 16, 16)
    glPopMatrix()
    terminar_transparencia()
