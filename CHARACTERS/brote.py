import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from CHARACTERS import animacion as anim
from CHARACTERS import chibi as cb
from RESOURCES import visual as v

# Personaje 3: BROTE, espiritu vegetal con capucha de hoja (estilo chibi)
CARA = (0.95, 0.93, 0.72)
HOJA = (0.30, 0.66, 0.26)
HOJA_OSC = (0.18, 0.47, 0.20)
NERVIO = (0.62, 0.84, 0.42)
SEMILLA = (0.58, 0.38, 0.20)
TALLO = (0.42, 0.62, 0.26)
RAIZ = (0.36, 0.24, 0.14)
OJOS = (0.10, 0.16, 0.08)
RUBOR = (1.0, 0.60, 0.55)
PETALO = (1.0, 0.55, 0.72)
POLEN = (1.0, 0.86, 0.30)

# Apertura de las hojas de la cabeza segun la expresion (0 = rectas, 90 = horizontales)
APERTURA_HOJAS = {0: 34.0, 1: 48.0, 2: 10.0, 3: 108.0, 4: 8.0, 5: 34.0, 6: 14.0}


# ---------- pose objetivo ----------
def _objetivo(mov, exp, t):
    o = cb.pose_base(mov, t)
    o.update(cb.expresion_base(exp))
    o["hoja"] = APERTURA_HOJAS[exp]
    if exp == 4:
        o["hoja"] += math.sin(t * 7.0) * 7.0
    o["flor"] = 1.0 if exp == 1 else 0.0
    return o


# ---------- hoja de la cabeza ----------
def _hoja(lado, apertura, color):
    glPushMatrix()
    glRotatef(-lado * apertura, 0, 0, 1)
    v.esfera((0, 0.52, 0), (0.25, 0.55, 0.06), color, 16)
    v.caja((0, 0.5, 0.05), (0.025, 0.85, 0.02), NERVIO)
    glPopMatrix()


# ---------- flor que se abre al estar feliz ----------
def _flor(escala, t):
    if escala < 0.05:
        return
    glPushMatrix()
    glTranslatef(0.0, 1.78, 0.14)
    glScalef(escala * 1.5, escala * 1.5, escala * 1.5)
    v.cilindro((0, -0.34, -0.03), 0.03, 0.34, TALLO, det=8, tapa=False)
    for i in range(6):
        glPushMatrix()
        # glRotatef usa float de 32 bits: sin el módulo, t es tan grande que se pierde i * 60
        glRotatef((i * 60.0 + t * 0.6) % 360.0, 0, 0, 1)
        v.esfera((0, 0.2, 0), (0.1, 0.16, 0.04), PETALO, 10)
        glPopMatrix()
    v.esfera((0, 0, 0.03), (0.1, 0.1, 0.05), POLEN, 10)
    glPopMatrix()


# ---------- cabeza ----------
def _cabeza(p, t, blink):
    glPushMatrix()
    glTranslatef(0.0, 2.3, 0.0)
    glRotatef(p["head_tilt"], 0, 0, 1)
    glRotatef(p["head_nod"], 1, 0, 0)
    glTranslatef(0.0, 1.12, 0.0)
    v.material(20.0, 0.25)

    # Cara y capucha de hoja
    v.esfera((0, 0, 0), (1.2, 1.1, 1.12), CARA, 28)
    v.esfera((0, 0.26, -0.2), (1.27, 1.0, 1.1), HOJA, 28)
    for i in range(5):
        x = (i - 2) * 0.42
        v.esfera((x, 0.82 - abs(x) * 0.26, 0.62 - abs(x) * 0.2), (0.27, 0.22, 0.2), HOJA_OSC, 12)

    for lado in (-1, 1):
        abierto = (p["eye_l"] if lado == -1 else p["eye_r"]) * blink
        tam = p["eye_ls"] if lado == -1 else p["eye_rs"]
        cb.ojo((lado * 0.42, -0.08, 1.0), p["eye_sx"] * tam, p["eye_sy"] * tam, abierto, p["brillo"], OJOS)
        rot = p["brow_l"] if lado == -1 else p["brow_r"]
        cb.ceja((lado * 0.42, 0.32 + p["brow_y"], 1.0), rot, HOJA_OSC)
        r = p["rubor"]
        v.esfera((lado * 0.74, -0.34, 0.84), (0.19 * r, 0.1 * r, 0.06), RUBOR, 12)

    cb.boca((0, -0.52, 1.0), p["mouth_curv"], p["mouth_open"], p["mouth_w"], p["mouth_rot"], OJOS)

    # Brote: tallo con dos hojas
    v.cilindro((0, 1.0, 0), 0.08, 0.34, TALLO, 0.06, 10)
    glPushMatrix()
    glTranslatef(0.0, 1.3, 0.0)
    balanceo = math.sin(t * 0.7) * 5.0
    _hoja(-1, p["hoja"] + balanceo, HOJA)
    _hoja(1, p["hoja"] - balanceo, HOJA_OSC)
    glPopMatrix()
    _flor(p["flor"], t)
    glPopMatrix()


# ---------- falda de hojas ----------
def _falda():
    for i in range(10):
        glPushMatrix()
        glRotatef(i * 36.0, 0, 1, 0)
        glTranslatef(0.0, 1.2, 0.5)
        glRotatef(28, 1, 0, 0)
        v.esfera((0, -0.12, 0), (0.2, 0.28, 0.06), HOJA if i % 2 else HOJA_OSC, 10)
        glPopMatrix()


# ---------- polen flotando alrededor ----------
def _polen(t):
    v.iniciar_aditivo()
    for i in range(8):
        f = (t * 0.06 + i / 8.0) % 1.0
        a = i * 2.4 + t * 0.25
        r = 1.5 + 0.3 * math.sin(i * 1.7)
        glColor4f(POLEN[0], POLEN[1], POLEN[2], 0.6 * math.sin(f * math.pi))
        glPushMatrix()
        glTranslatef(math.cos(a) * r, 0.4 + f * 4.4, math.sin(a) * r)
        glutSolidSphere(0.05, 6, 6)
        glPopMatrix()
    v.terminar_transparencia()


# ---------- dibujo ----------
def draw_brote(expresion="normal", movimiento="reposo", t=0.0):
    mov = cb.MOVIMIENTOS.get(movimiento, 0)
    exp = cb.EXPRESIONES.get(expresion, 0)
    t = t * 5.0
    # el salto no se suaviza para que coincida con la sombra y el hitbox
    directos = ("body_y",) if mov == 2 else ()
    p = anim.suavizar("brote", _objetivo(mov, exp, t), directos=directos)
    blink = 1.0 if exp in (5, 6) else anim.parpadeo(4.2, 0.6)
    aliento = anim.respiracion(1.9) if mov in (0, 3) else 1.0

    glPushAttrib(GL_ALL_ATTRIB_BITS)
    v.material(20.0, 0.25)

    glPushMatrix()
    # main.py y el menú dibujan al personaje en z - 7 (ver modelo de Isaac)
    glTranslatef(0.0, p["body_y"], 7.0)
    glRotatef(p["body_rot_x"], 1, 0, 0)

    # Piernas de tallo con pies de raiz
    for lado in (-1, 1):
        cb.pierna(lado, p, (0.3, 1.09), TALLO, RAIZ)

    # Torso de semilla, falda y cuello de hojas
    v.esfera((0, 1.62, 0), (0.62 * aliento, 0.7, 0.52 * aliento), SEMILLA, 22)
    v.esfera((0, 1.68, 0.4), (0.3, 0.38, 0.14), v.mezclar(SEMILLA, (1, 1, 1), 0.25), 14)
    _falda()
    glPushMatrix()
    glTranslatef(0, 2.22, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3fv(HOJA)
    glutSolidTorus(0.11, 0.37, 8, 20)
    glPopMatrix()

    # Brazos de enredadera
    for lado in (-1, 1):
        cb.brazo(lado, p, (0.6, 2.0), TALLO, CARA)

    _cabeza(p, t, blink)
    _polen(t)
    glPopMatrix()
    glPopAttrib()
