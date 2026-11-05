import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from CHARACTERS import animacion as anim
from CHARACTERS import chibi as cb
from RESOURCES import visual as v

# Personaje 1: CHISPA, espiritu de llama violeta (estilo chibi)
active_movement = 0
active_expression = 0

PIEL = (1.0, 0.88, 0.78)
TUNICA = (0.12, 0.58, 0.62)
TUNICA_OSC = (0.08, 0.42, 0.46)
BUFANDA = (0.92, 0.38, 0.58)
LLAMA = (0.55, 0.32, 0.95)
LLAMA_PUNTA = (1.0, 0.62, 0.90)
OJOS = (0.13, 0.08, 0.22)
BOTAS = (0.35, 0.22, 0.45)
ORO = (0.95, 0.75, 0.25)
RUBOR = (1.0, 0.58, 0.65)
ENERGIA = (0.75, 0.35, 1.0)


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
        o.update(arm_r_rot=-85, arm_r_rot_z=0, arm_l_rot=-55, arm_l_rot_z=-25, body_rot_x=6, head_nod=6)
    elif active_movement == 6:
        o.update(body_rot_x=28, arm_l_rot=55, arm_r_rot=55, arm_l_rot_z=-15, arm_r_rot_z=15)
        o["leg_l_rot"] = math.sin(t * 1.8) * 55
        o["leg_r_rot"] = math.sin(t * 1.8 + 3.14) * 55
        o["leg_l_bend"] = max(0.0, math.sin(t * 1.8)) * 70
        o["leg_r_bend"] = max(0.0, math.sin(t * 1.8 + 3.14)) * 70
        o["body_y"] = abs(math.sin(t * 1.8)) * 0.15
        o["head_nod"] = -18
    elif active_movement == 7:
        o.update(arm_l_rot_z=-150, arm_r_rot_z=150, head_nod=-12)
        o["body_y"] = 0.35 + math.sin(t * 5) * 0.04
    e = cb.expresion_base(active_expression)
    if active_expression == 7:
        e.update(brow_l=20, brow_r=-5, brow_y=0.05, mouth_rot=15, mouth_curv=-0.2, mouth_w=0.8)
    o.update(e)
    return o


# ---------- llamas de la cabeza ----------
def _llamas(t, sombra):
    piezas = [(-0.38, 0.95, 0.15, -28, 0.8), (0.38, 0.95, 0.15, 28, 0.8),
              (0.0, 1.0, -0.25, 0, 0.9), (0.0, 1.05, 0.12, 0, 1.0)]
    for i, (x, y, z, giro, tam) in enumerate(piezas):
        f = 1.0 + 0.08 * math.sin(t * 6.0 + i * 1.3)
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(giro + math.sin(t * 3 + i) * 4, 0, 0, 1)
        v.esfera((0, 0.12, 0), (0.33 * tam, 0.3 * tam, 0.33 * tam), LLAMA, 14)
        v.cono((0, 0.15, 0), 0.3 * tam, 0.75 * tam * f, v.mezclar(LLAMA, LLAMA_PUNTA, 0.6), 14)
        v.esfera((0, 0.15 + 0.72 * tam * f, 0), (0.06, 0.06, 0.06), LLAMA_PUNTA, 8)
        glPopMatrix()
    if not sombra:
        v.halo((0, 1.35, 0), 1.1, LLAMA, 0.16, 3)


# ---------- cabeza ----------
def _cabeza(p, t, blink, sombra):
    glPushMatrix()
    glTranslatef(0.0, 2.3, 0.0)
    glRotatef(p["head_tilt"], 0, 0, 1)
    glRotatef(p["head_nod"], 1, 0, 0)
    glTranslatef(0.0, 1.15, 0.0)
    v.material(25.0, 0.35)
    v.esfera((0, 0, 0), (1.25, 1.15, 1.15), PIEL, 28)

    for lado in (-1, 1):
        abierto = (p["eye_l"] if lado == -1 else p["eye_r"]) * blink
        tam = p["eye_ls"] if lado == -1 else p["eye_rs"]
        cb.ojo((lado * 0.42, 0.0, 1.02), p["eye_sx"] * tam, p["eye_sy"] * tam, abierto, p["brillo"], OJOS)
        rot = p["brow_l"] if lado == -1 else p["brow_r"]
        cb.ceja((lado * 0.42, 0.42 + p["brow_y"], 0.98), rot, (0.40, 0.22, 0.55))
        r = p["rubor"]
        v.esfera((lado * 0.76, -0.3, 0.86), (0.2 * r, 0.11 * r, 0.06), RUBOR, 12)

    cb.boca((0, -0.48, 1.03), p["mouth_curv"], p["mouth_open"], p["mouth_w"], p["mouth_rot"], OJOS)
    _llamas(t, sombra)
    glPopMatrix()


# ---------- esfera de energia en la mano ----------
def _esfera_energia(t):
    glPushMatrix()
    glTranslatef(0.6, 2.0, 0.0)
    glRotatef(-85, 1, 0, 0)
    glTranslatef(0.0, -0.95, 0.0)
    r = 0.32 + math.sin(t * 10) * 0.03
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    v.esfera((0, 0, 0), (r * 0.6, r * 0.6, r * 0.6), (1.0, 0.85, 1.0), 16)
    if con_luz:
        glEnable(GL_LIGHTING)
    v.iniciar_aditivo()
    for i in range(3):
        glPushMatrix()
        glRotatef(t * 120 + i * 60, 1, 1, 0)
        glRotatef(i * 60, 0, 1, 0)
        glColor4f(ENERGIA[0], ENERGIA[1], ENERGIA[2], 0.4)
        glutSolidTorus(0.03, r * 0.9, 8, 28)
        glPopMatrix()
    v.terminar_transparencia()
    v.halo((0, 0, 0), r * 2.4, ENERGIA, 0.45, 4)
    glPopMatrix()


# ---------- dibujo ----------
def draw_chispa(expresion="normal", movimiento="reposo", t=0.0, sombra=False):
    set_expression(cb.EXPRESIONES.get(expresion, 0))
    set_movement(cb.MOVIMIENTOS.get(movimiento, 0))
    t = t * 5.0
    # el salto no se suaviza para que coincida con la sombra y el hitbox
    directos = ("body_y",) if active_movement == 2 else ()
    p = anim.suavizar("chispa", _objetivo(t), directos=directos)
    blink = 1.0 if active_expression in (5, 6) else anim.parpadeo(3.8)
    aliento = anim.respiracion() if active_movement in (0, 3, 4, 7) else 1.0

    glPushAttrib(GL_ALL_ATTRIB_BITS)
    v.material(25.0, 0.35)

    glPushMatrix()
    # main.py y el menú dibujan al personaje en z - 7 (ver modelo de Isaac)
    glTranslatef(0.0, p["body_y"], 7.0)
    glRotatef(p["body_rot_x"], 1, 0, 0)
    glScalef(1.0, p["body_scale_y"], 1.0)

    # Piernas
    for lado in (-1, 1):
        cb.pierna(lado, p, (0.3, 1.09), TUNICA_OSC, BOTAS)

    # Torso con tunica, cinturon y bufanda
    v.cilindro((0, 0.95, 0), 0.66, 0.5, TUNICA_OSC, 0.55, 20)
    v.esfera((0, 1.62, 0), (0.62 * aliento, 0.7, 0.52 * aliento), TUNICA, 22)
    glPushMatrix()
    glTranslatef(0, 1.32, 0)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.0, 0.85, 1.0)
    glColor3fv(ORO)
    glutSolidTorus(0.06, 0.57, 8, 28)
    glPopMatrix()
    v.esfera((0, 1.32, 0.5), (0.1, 0.1, 0.05), ORO, 10)
    glPushMatrix()
    glTranslatef(0, 2.22, 0)
    glRotatef(-90, 1, 0, 0)
    glColor3fv(BUFANDA)
    glutSolidTorus(0.14, 0.4, 10, 24)
    glPopMatrix()
    ondea = math.sin(t * 0.8) * 10 + (25 if active_movement == 6 else 0)
    for i, dx in enumerate((-0.12, 0.14)):
        glPushMatrix()
        glTranslatef(dx, 2.15, -0.42)
        glRotatef(ondea + i * 8, 1, 0, 0)
        v.caja((0, -0.35, 0), (0.2, 0.7, 0.06), BUFANDA)
        glPopMatrix()

    # Brazos
    for lado in (-1, 1):
        cb.brazo(lado, p, (0.6, 2.0), TUNICA, PIEL)

    _cabeza(p, t, blink, sombra)

    if not sombra:
        if active_movement == 4:
            _esfera_energia(t)
        elif active_movement == 7:
            v.aura(5.2, 1.7, ENERGIA, t * 0.2, 1.3)
    glPopMatrix()
    glPopAttrib()