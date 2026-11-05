import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from CHARACTERS import animacion as anim
from CHARACTERS import chibi as cb
from RESOURCES import visual as v

# Personaje 2: MAPI, mapache explorador (estilo chibi)
active_movement = 0
active_expression = 0

PELO = (0.62, 0.62, 0.66)
OSCURO = (0.22, 0.22, 0.26)
BLANCO = (0.96, 0.96, 0.94)
CAMISA = (0.86, 0.76, 0.52)
SOMBRERO = (0.42, 0.50, 0.28)
CINTA = (0.40, 0.25, 0.15)
MOCHILA = (0.62, 0.32, 0.20)
BOTAS = (0.42, 0.27, 0.16)
IRIS = (0.32, 0.19, 0.07)
RUBOR = (1.0, 0.62, 0.66)


def set_movement(mov_id):
    global active_movement
    active_movement = mov_id


def set_expression(exp_id):
    global active_expression
    active_expression = exp_id


# ---------- pose objetivo ----------
def _objetivo(t):
    o = cb.pose_base(active_movement, t)
    if active_movement == 4:
        o.update(arm_l_rot_z=-85, arm_r_rot_z=85, head_nod=-5)
        o["body_rot_y"] = (t * 200) % 360.0
    elif active_movement == 6:
        o["body_y"] = abs(math.sin(t * 2)) * 0.3
        o["arm_l_rot"] = math.sin(t) * 90
        o["arm_r_rot"] = math.cos(t) * 90
        o["body_rot_y"] = math.sin(t) * 35
        o["head_tilt"] = math.sin(t * 2) * 10
    elif active_movement == 7:
        o.update(body_scale_y=0.3, arm_l_rot_z=-80, arm_r_rot_z=80)
    e = cb.expresion_base(active_expression)
    if active_expression == 7:
        e.update(eye_ls=0.8, eye_rs=1.2, mouth_curv=-0.3, mouth_rot=-10, brow_l=15, brow_r=15)
    o.update(e)
    return o


# ---------- cola anillada ----------
def _cola(t):
    mueve = math.sin(t * 0.9) * (0.25 if active_movement != 6 else 0.5)
    for i in range(7):
        k = i / 6.0
        color = OSCURO if i % 2 else PELO
        if i == 6:
            color = OSCURO
        r = 0.24 - 0.02 * i
        v.esfera((mueve * k * k, 0.95 + i * 0.16 + k * k * 0.3, -0.45 - i * 0.17), (r, r, r * 1.1), color, 12)


# ---------- mochila ----------
def _mochila():
    v.caja((0, 1.72, -0.58), (0.85, 0.95, 0.4), MOCHILA)
    v.caja((0, 2.08, -0.55), (0.9, 0.32, 0.46), v.mezclar(MOCHILA, (0, 0, 0), 0.2))
    v.caja((0, 1.45, -0.8), (0.5, 0.3, 0.06), v.mezclar(MOCHILA, (1, 1, 1), 0.15))
    glPushMatrix()
    glTranslatef(-0.55, 2.38, -0.58)
    glRotatef(90, 0, 1, 0)
    glColor3f(0.75, 0.25, 0.22)
    gluCylinder(v.quadric(), 0.17, 0.17, 1.1, 14, 1)
    glPopMatrix()
    for lado in (-1, 1):
        v.caja((lado * 0.28, 1.78, 0.47), (0.1, 0.85, 0.05), CINTA)


# ---------- sombrero ----------
def _sombrero():
    glPushMatrix()
    glTranslatef(0.0, 0.88, -0.05)
    glRotatef(-8, 1, 0, 0)
    glRotatef(5, 0, 0, 1)
    v.cilindro((0, 0, 0), 1.38, 0.06, SOMBRERO, det=32)
    v.cilindro((0, 0.06, 0), 0.84, 0.58, SOMBRERO, 0.72, 28)
    v.cilindro((0, 0.08, 0), 0.86, 0.16, CINTA, 0.83, 28, False)
    glPopMatrix()


# ---------- cabeza ----------
def _cabeza(p, t, blink):
    glPushMatrix()
    glTranslatef(0.0, 2.25, 0.0)
    glRotatef(p["head_tilt"], 0, 0, 1)
    glRotatef(p["head_nod"], 1, 0, 0)
    glTranslatef(0.0, 1.12, 0.0)
    v.material(15.0, 0.2)
    v.esfera((0, 0, 0), (1.25, 1.1, 1.15), PELO, 28)

    giro = t * 1.5 if active_expression == 7 else None
    for lado in (-1, 1):
        glPushMatrix()
        glTranslatef(lado * 0.85, 1.1, -0.1)
        glRotatef(-lado * 18, 0, 0, 1)
        v.esfera((0, 0, 0), (0.3, 0.32, 0.12), PELO, 14)
        v.esfera((0, -0.02, 0.07), (0.17, 0.19, 0.06), OSCURO, 12)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(lado * 0.4, 0.04, 0.95)
        glRotatef(-lado * 12, 0, 0, 1)
        v.esfera((0, 0, 0), (0.37, 0.27, 0.16), OSCURO, 16)
        glPopMatrix()

        abierto = (p["eye_l"] if lado == -1 else p["eye_r"]) * blink
        tam = p["eye_ls"] if lado == -1 else p["eye_rs"]
        cb.ojo((lado * 0.4, 0.06, 1.06), p["eye_sx"] * tam, p["eye_sy"] * tam, abierto,
               p["brillo"], IRIS, True, giro)
        rot = p["brow_l"] if lado == -1 else p["brow_r"]
        cb.ceja((lado * 0.42, 0.42 + p["brow_y"], 0.98), rot, BLANCO)
        v.esfera((lado * 1.1, -0.3, 0.3), (0.24, 0.16, 0.22), BLANCO, 12)
        r = p["rubor"]
        v.esfera((lado * 0.7, -0.42, 0.85), (0.15 * r, 0.09 * r, 0.05), RUBOR, 10)

    v.esfera((0, -0.38, 0.9), (0.48, 0.32, 0.35), BLANCO, 20)
    v.material(60.0, 0.7)
    v.esfera((0, -0.24, 1.23), (0.12, 0.09, 0.08), OSCURO, 12)
    v.material(15.0, 0.2)
    cb.boca((0, -0.5, 1.19), p["mouth_curv"], p["mouth_open"], p["mouth_w"] * 0.85, p["mouth_rot"], OSCURO)
    _sombrero()
    glPopMatrix()


# ---------- dibujo ----------
def draw_mapi(expresion="normal", movimiento="reposo", t=0.0, sombra=False):
    set_expression(cb.EXPRESIONES.get(expresion, 0))
    set_movement(cb.MOVIMIENTOS.get(movimiento, 0))
    t = t * 5.0
    # el salto no se suaviza para que coincida con la sombra y el hitbox
    directos = {2: ("body_y",), 4: ("body_rot_y",)}.get(active_movement, ())
    p = anim.suavizar("mapi", _objetivo(t), directos=directos)
    blink = 1.0 if active_expression in (5, 6, 7) else anim.parpadeo(3.3, 1.1)
    aliento = anim.respiracion(2.6) if active_movement in (0, 3) else 1.0

    glPushAttrib(GL_ALL_ATTRIB_BITS)
    v.material(15.0, 0.2)

    glPushMatrix()
    # main.py y el menú dibujan al personaje en z - 7 (ver modelo de Isaac)
    glTranslatef(0.0, p["body_y"], 7.0)
    glRotatef(p["body_rot_x"], 1, 0, 0)
    glRotatef(p["body_rot_y"], 0, 1, 0)
    if not sombra:
        if active_movement == 4:
            v.iniciar_aditivo()
            for i in range(5):
                glPushMatrix()
                glTranslatef(0, 0.3 + i * 0.85, 0)
                glRotatef(-t * 300 + i * 40, 0, 1, 0)
                glRotatef(90, 1, 0, 0)
                glColor4f(0.85, 0.95, 0.65, 0.22)
                glutSolidTorus(0.06, 1.4 + i * 0.12, 6, 28)
                glPopMatrix()
            v.terminar_transparencia()
        if active_expression == 7 or active_movement == 7:
            cb.estrellas(5.3 if active_movement != 7 else 1.9, t)
    glScalef(1.0, p["body_scale_y"], 1.0)

    # Piernas y cola
    for lado in (-1, 1):
        cb.pierna(lado, p, (0.3, 1.09), PELO, BOTAS)
    _cola(t)

    # Torso con camisa de explorador
    v.esfera((0, 1.6, 0), (0.62 * aliento, 0.68, 0.52 * aliento), CAMISA, 22)
    v.esfera((0, 1.95, 0.42), (0.07, 0.07, 0.04), CINTA, 8)
    v.esfera((0, 1.0, 0), (0.58, 0.28, 0.48), (0.40, 0.33, 0.22), 18)
    _mochila()

    # Brazos
    for lado in (-1, 1):
        cb.brazo(lado, p, (0.6, 1.95), PELO, OSCURO, CAMISA)

    _cabeza(p, t, blink)
    glPopMatrix()
    glPopAttrib()