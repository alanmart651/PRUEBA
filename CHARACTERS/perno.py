import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from CHARACTERS import animacion as anim
from CHARACTERS import chibi as cb
from RESOURCES import visual as v

# Personaje 4: PERNO, robot de laton con cara de pantalla LED
LATON = (0.82, 0.63, 0.30)
LATON_OSC = (0.58, 0.42, 0.20)
ACERO = (0.55, 0.59, 0.65)
OSCURO = (0.10, 0.12, 0.16)
ACENTO = (0.86, 0.36, 0.18)
FUEGO = (1.0, 0.55, 0.15)
# Las caras planas casi no reciben la luz de las salas, que queda sobre el personaje
BRILLO_METAL = (0.17, 0.13, 0.07)

# Color de la pantalla segun la expresion
LED = {0: (0.25, 0.90, 1.00), 1: (0.35, 1.00, 0.45), 2: (1.00, 0.20, 0.15), 3: (0.30, 0.50, 1.00),
       4: (0.75, 0.45, 1.00), 5: (1.00, 0.85, 0.25), 6: (1.00, 1.00, 1.00)}


# ---------- pose objetivo ----------
def _objetivo(mov, exp, t):
    o = cb.pose_base(mov, t)
    o.update(cb.expresion_base(exp))
    o["led_r"], o["led_g"], o["led_b"] = LED[exp]
    return o


# ---------- material ----------
def _metal():
    v.material(35.0, 0.3, BRILLO_METAL)


# ---------- pieza oscura, sin el brillo del metal ----------
def _caja_oscura(pos, escala):
    v.material(35.0, 0.3)
    v.caja(pos, escala, OSCURO)
    _metal()


# ---------- pantalla con la expresion ----------
def _pantalla(p, led, blink, exp, t):
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    z = 0.85
    temblor = math.sin(t * 9.0) * 0.025 if exp == 4 else 0.0

    for lado in (-1, 1):
        abierto = (p["eye_l"] if lado == -1 else p["eye_r"]) * blink
        ancho = 0.34 * p["eye_sx"]
        alto = 0.36 * p["eye_sy"] * max(abierto, 0.12)
        v.caja((lado * 0.46 + temblor, 0.12, z), (ancho, alto, 0.03), led)
        rot = p["brow_l"] if lado == -1 else p["brow_r"]
        cb.ceja((lado * 0.46, 0.46 + p["brow_y"], z), rot, led)

    # Boca de segmentos
    ancho = p["mouth_w"]
    for i in range(7):
        u = -1.0 + i / 3.0
        y = -0.32 + p["mouth_curv"] * 0.08 * u * u
        v.caja((u * 0.34 * ancho, y, z), (0.09, 0.07, 0.03), led)
    if p["mouth_open"] > 0.05:
        v.caja((0, -0.4, z), (0.34 * ancho, 0.2 * p["mouth_open"], 0.03), led)

    if con_luz:
        glEnable(GL_LIGHTING)


# ---------- cabeza ----------
def _cabeza(p, led, t, blink, exp):
    glPushMatrix()
    glTranslatef(0.0, 2.25, 0.0)
    glRotatef(p["head_tilt"], 0, 0, 1)
    glRotatef(p["head_nod"], 1, 0, 0)
    v.cilindro((0, -0.05, 0), 0.22, 0.3, ACERO, det=14, tapa=False)
    glTranslatef(0.0, 1.0, 0.0)

    v.caja((0, 0, 0), (2.1, 1.6, 1.6), LATON)
    _caja_oscura((0, 0.0, 0.78), (1.8, 1.25, 0.1))
    v.caja((0, 0.82, 0), (1.3, 0.1, 1.1), LATON_OSC)

    # Pernos de las esquinas
    for x in (-0.97, 0.97):
        for y in (-0.7, 0.7):
            v.esfera((x, y, 0.8), (0.055, 0.055, 0.04), ACERO, 8)

    # Orejas de perno
    for lado in (-1, 1):
        glPushMatrix()
        glTranslatef(lado * 1.05, 0.05, 0.0)
        glRotatef(lado * 90, 0, 1, 0)
        glColor3fv(ACERO)
        glutSolidCylinder(0.26, 0.16, 6, 1)
        glPopMatrix()

    # Antena
    glPushMatrix()
    glTranslatef(0.0, 0.85, 0.0)
    glRotatef(math.sin(t * 0.9) * 8.0, 0, 0, 1)
    v.cilindro((0, 0, 0), 0.05, 0.62, ACERO, 0.03, 8, False)
    pulso = 0.5 + 0.5 * math.sin(t * 1.3)
    v.esfera((0, 0.72, 0), (0.13, 0.13, 0.13), v.mezclar(ACENTO, led, pulso), 12)
    v.halo((0, 0.72, 0), 0.26, led, 0.18 + 0.18 * pulso, 3, 10)
    glPopMatrix()

    _pantalla(p, led, blink, exp, t)
    glPopMatrix()


# ---------- brazo ----------
def _brazo(lado, p):
    s = "r" if lado == 1 else "l"
    glPushMatrix()
    glTranslatef(lado * 0.74, 2.0, 0.0)
    glRotatef(p["arm_%s_rot" % s], 1, 0, 0)
    glRotatef(p["arm_%s_rot_z" % s], 0, 0, 1)
    v.esfera((0, 0, 0), (0.2, 0.2, 0.2), ACERO, 12)
    v.caja((0, -0.3, 0), (0.22, 0.42, 0.22), LATON)
    v.esfera((0, -0.54, 0), (0.12, 0.12, 0.12), ACERO, 10)
    for dx in (-0.09, 0.09):
        v.caja((dx, -0.7, 0), (0.07, 0.24, 0.16), ACENTO)
    glPopMatrix()


# ---------- propulsor bajo el pie ----------
def _propulsor(t, lado):
    largo = 0.5 + 0.15 * math.sin(t * 6.0 + lado)
    v.iniciar_aditivo()
    glPushMatrix()
    glTranslatef(0.0, -0.6, 0.08)
    glRotatef(180, 1, 0, 0)
    v.cono((0, 0, 0), 0.15, largo, FUEGO, 10)
    glPopMatrix()
    v.terminar_transparencia()


# ---------- pierna ----------
def _pierna(lado, p, t, propulsor):
    s = "r" if lado == 1 else "l"
    glPushMatrix()
    glTranslatef(lado * 0.3, 1.09, 0.0)
    glRotatef(p["leg_%s_rot" % s], 1, 0, 0)
    v.caja((0, -0.22, 0), (0.26, 0.44, 0.28), LATON)
    glTranslatef(0, -0.48, 0)
    glRotatef(p["leg_%s_bend" % s], 1, 0, 0)
    v.esfera((0, 0, 0), (0.15, 0.15, 0.15), ACERO, 10)
    v.caja((0, -0.2, 0), (0.24, 0.36, 0.26), LATON)
    _caja_oscura((0, -0.5, 0.08), (0.34, 0.22, 0.52))
    if propulsor:
        _propulsor(t, lado)
    glPopMatrix()


# ---------- torso ----------
def _torso(led, t, aliento):
    v.caja((0, 1.65, 0), (1.15, 1.15 * aliento, 0.8), LATON)
    _caja_oscura((0, 1.72, 0.39), (0.66, 0.46, 0.04))
    v.caja((0, 1.12, 0), (0.86, 0.14, 0.62), ACERO)
    v.caja((0, 2.26, 0), (0.7, 0.1, 0.5), LATON_OSC)

    # Luces del pecho
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    for i in range(3):
        encendida = math.sin(t * 0.8 + i * 2.1) > -0.2
        color = led if encendida else v.mezclar(led, OSCURO, 0.8)
        v.caja(((i - 1) * 0.19, 1.72, 0.42), (0.13, 0.26, 0.02), color)
    if con_luz:
        glEnable(GL_LIGHTING)


# ---------- dibujo ----------
def draw_perno(expresion="normal", movimiento="reposo", t=0.0):
    mov = cb.MOVIMIENTOS.get(movimiento, 0)
    exp = cb.EXPRESIONES.get(expresion, 0)
    t = t * 5.0
    # el salto no se suaviza para que coincida con la sombra y el hitbox
    directos = ("body_y",) if mov == 2 else ()
    p = anim.suavizar("perno", _objetivo(mov, exp, t), directos=directos)
    led = (p["led_r"], p["led_g"], p["led_b"])
    blink = 1.0 if exp in (5, 6) else anim.parpadeo(5.0, 1.7)
    aliento = anim.respiracion(3.0, 0.012) if mov in (0, 3) else 1.0

    glPushAttrib(GL_ALL_ATTRIB_BITS)
    _metal()

    glPushMatrix()
    # main.py y el menú dibujan al personaje en z - 7 (ver modelo de Isaac)
    glTranslatef(0.0, p["body_y"], 7.0)
    glRotatef(p["body_rot_x"], 1, 0, 0)

    # Propulsores encendidos al volar y al estar en el aire
    propulsor = mov == 11 or (mov == 2 and p["body_y"] > 0.3)
    for lado in (-1, 1):
        _pierna(lado, p, t, propulsor)

    _torso(led, t, aliento)
    for lado in (-1, 1):
        _brazo(lado, p)

    _cabeza(p, led, t, blink, exp)
    glPopMatrix()
    glPopAttrib()
