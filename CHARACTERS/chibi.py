import math
from OpenGL.GL import *
from OpenGL.GLUT import *
from RESOURCES import visual as v


# Traducción de los nombres de la aplicación a los IDs de pose. Los IDs 4, 6 y 7
# de movimiento y 7 de expresión son poses propias de cada personaje.
MOVIMIENTOS = {"reposo": 0, "caminar": 1, "saltar": 2, "saludar": 3, "agacharse": 5,
               "elevar_brazos": 8, "doblar_piernas": 9, "inclinarse": 10, "flotar": 11}
EXPRESIONES = {"normal": 0, "feliz": 1, "enojado": 2, "triste": 3, "miedo": 4,
               "guiño": 5, "asombro": 6}


# ---------- pose base (movimientos 0,1,2,3,5,8,9,10,11) ----------
def pose_base(mov, t):
    o = {"body_y": 0.0, "body_rot_x": 0.0, "body_rot_y": 0.0, "body_scale_y": 1.0,
         "head_tilt": 0.0, "head_nod": 0.0,
         "arm_l_rot": 0.0, "arm_r_rot": 0.0, "arm_l_rot_z": -12.0, "arm_r_rot_z": 12.0,
         "leg_l_rot": 0.0, "leg_r_rot": 0.0, "leg_l_bend": 0.0, "leg_r_bend": 0.0}
    if mov == 0:
        o["head_tilt"] = math.sin(t * 0.3) * 4.0
        o["arm_l_rot"] = math.sin(t * 0.4) * 4.0
        o["arm_r_rot"] = -o["arm_l_rot"]
    elif mov == 1:
        o["arm_l_rot"] = math.sin(t) * 38
        o["arm_r_rot"] = math.sin(t + 3.14) * 38
        o["leg_l_rot"] = math.sin(t + 3.14) * 35
        o["leg_r_rot"] = math.sin(t) * 35
        o["leg_l_bend"] = max(0.0, math.sin(t)) * 40
        o["leg_r_bend"] = max(0.0, math.sin(t + 3.14)) * 40
        o["body_y"] = abs(math.sin(t)) * 0.12
        o["head_tilt"] = math.sin(t) * 4.0
    elif mov == 2:
        # misma curva que altura_salto() en main.py (t llega multiplicado por 5)
        o["body_y"] = abs(math.sin(t * 1.6)) * 2.0
        o["arm_l_rot"], o["arm_r_rot"] = -160, -160
        o["arm_l_rot_z"], o["arm_r_rot_z"] = -25, 25
        o["leg_l_rot"], o["leg_r_rot"] = -20, -20
        o["leg_l_bend"], o["leg_r_bend"] = 55, 55
        o["head_nod"] = -10
    elif mov == 3:
        o["arm_l_rot_z"] = -140 + math.sin(t * 3) * 22
        o["head_tilt"] = 10
    elif mov == 5:
        o["body_y"] = -0.45
        o["leg_l_rot"], o["leg_r_rot"] = -55, -55
        o["leg_l_bend"], o["leg_r_bend"] = 95, 95
        o["arm_l_rot"], o["arm_r_rot"] = -40, -40
        o["head_nod"] = 8
    elif mov == 8:
        o["arm_l_rot"] = o["arm_r_rot"] = -90 + math.sin(t * 1.2) * 90
    elif mov == 9:
        k = 0.5 + 0.5 * math.sin(t * 1.2)
        o["body_y"] = -0.45 * k
        o["leg_l_rot"] = o["leg_r_rot"] = -55 * k
        o["leg_l_bend"] = o["leg_r_bend"] = 95 * k
    elif mov == 10:
        o["body_rot_x"] = math.sin(t) * 10.0
    elif mov == 11:
        o["body_y"] = 3.0 + math.sin(t * 0.8) * 0.5
        o["body_rot_x"] = -45.0
        o["arm_l_rot"], o["arm_r_rot"] = -180, 0
        o["leg_l_rot"], o["leg_r_rot"] = 20, 20
    return o


# ---------- expresion base (expresiones 0 a 6) ----------
def expresion_base(exp):
    o = {"eye_sx": 1.0, "eye_sy": 1.0, "eye_l": 1.0, "eye_r": 1.0, "eye_ls": 1.0, "eye_rs": 1.0,
         "brillo": 1.0, "brow_l": 0.0, "brow_r": 0.0, "brow_y": 0.0,
         "mouth_curv": 0.6, "mouth_open": 0.0, "mouth_w": 1.0, "mouth_rot": 0.0, "rubor": 1.0}
    if exp == 1:
        o.update(mouth_curv=1.4, mouth_open=0.5, mouth_w=1.3, eye_sy=0.85, brow_y=0.05, rubor=1.4)
    elif exp == 2:
        o.update(brow_l=-25, brow_r=25, brow_y=-0.06, mouth_curv=-0.9, eye_sy=0.75, rubor=0.6)
    elif exp == 3:
        o.update(brow_l=20, brow_r=-20, brow_y=0.03, mouth_curv=-1.0, eye_sy=0.9, brillo=0.8)
    elif exp == 4:
        o.update(eye_sx=0.85, eye_sy=1.15, brillo=0.55, mouth_open=0.6, mouth_curv=-0.4,
                 mouth_w=0.8, brow_l=15, brow_r=-15, brow_y=0.1, rubor=0.4)
    elif exp == 5:
        o.update(eye_l=0.06, mouth_curv=1.2, brow_l=-10, rubor=1.3)
    elif exp == 6:
        o.update(eye_sx=1.2, eye_sy=1.3, brillo=1.25, mouth_open=0.8, mouth_w=0.7, brow_y=0.12)
    return o


# ---------- ojo grande con brillos ----------
def ojo(pos, sx, sy, abierto, brillo, color, esclera=False, giro=None):
    alto = 0.27 * sy * max(abierto, 0.06)
    glPushMatrix()
    glTranslatef(*pos)
    if esclera:
        v.esfera((0, 0, 0), (0.2 * sx, alto, 0.08), (1.0, 1.0, 1.0), 16)
        iris = 0.14 * min(brillo, 1.1)
        v.esfera((0, 0, 0.04), (iris * sx, min(iris * 1.15 * sy, alto * 0.92), 0.06), color, 14)
    else:
        v.esfera((0, 0, 0), (0.2 * sx, alto, 0.09), color, 16)
    if abierto > 0.35:
        con_luz = glIsEnabled(GL_LIGHTING)
        hx, hy = 0.06 * sx, 0.1 * sy * abierto
        if giro is not None:
            hx, hy = math.cos(giro) * 0.07 * sx, math.sin(giro) * 0.09 * sy
        glDisable(GL_LIGHTING)
        v.esfera((hx, hy, 0.09), (0.055 * brillo, 0.055 * brillo, 0.03), (1.0, 1.0, 1.0), 8)
        v.esfera((-0.05 * sx, -0.08 * sy, 0.09), (0.028, 0.028, 0.02), (1.0, 1.0, 1.0), 8)
        if con_luz:
            glEnable(GL_LIGHTING)
    glPopMatrix()


# ---------- ceja ----------
def ceja(pos, rot, color):
    v.caja(pos, (0.26, 0.06, 0.05), color, (0, 0, 1, rot))


# ---------- boca curva ----------
def boca(pos, curv, abierta, ancho, rot, color):
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(rot, 0, 0, 1)
    if abierta > 0.05:
        v.esfera((0, -0.05, -0.01), (0.12 * ancho, 0.11 * abierta, 0.05), (0.45, 0.08, 0.12), 12)
    for i in range(9):
        u = -1.0 + i / 4.0
        v.esfera((u * 0.2 * ancho, curv * 0.07 * u * u, -0.03 * u * u), (0.035, 0.035, 0.035), color, 6)
    glPopMatrix()


# ---------- estrellas de mareo ----------
def estrellas(alto, t):
    for i in range(4):
        a = t * 2.0 + i * 1.5708
        v.material(60.0, 0.8, (0.5, 0.45, 0.0))
        glPushMatrix()
        glTranslatef(math.cos(a) * 1.0, alto + math.sin(t * 3 + i) * 0.1, math.sin(a) * 1.0)
        glRotatef(t * 90, 0, 1, 0)
        glColor3f(1.0, 0.9, 0.2)
        glScalef(0.15, 0.15, 0.15)
        glutSolidOctahedron()
        glPopMatrix()
    v.material()


# ---------- brazo ----------
def brazo(lado, p, hombro, color, color_mano, manga=None):
    s = "r" if lado == 1 else "l"
    glPushMatrix()
    glTranslatef(lado * hombro[0], hombro[1], 0.0)
    glRotatef(p["arm_%s_rot" % s], 1, 0, 0)
    glRotatef(p["arm_%s_rot_z" % s], 0, 0, 1)
    v.esfera((0, 0, 0), (0.19, 0.19, 0.19), manga or color, 12)
    v.esfera((0, -0.3, 0), (0.15, 0.32, 0.15), color, 14)
    v.esfera((0, -0.64, 0), (0.19, 0.19, 0.19), color_mano, 14)
    glPopMatrix()


# ---------- pierna ----------
def pierna(lado, p, cadera, color, color_bota):
    s = "r" if lado == 1 else "l"
    glPushMatrix()
    glTranslatef(lado * cadera[0], cadera[1], 0.0)
    glRotatef(p["leg_%s_rot" % s], 1, 0, 0)
    v.esfera((0, -0.24, 0), (0.2, 0.3, 0.2), color, 14)
    glTranslatef(0, -0.48, 0)
    glRotatef(p["leg_%s_bend" % s], 1, 0, 0)
    v.esfera((0, -0.18, 0), (0.17, 0.24, 0.17), color, 12)
    v.esfera((0, -0.44, 0.08), (0.25, 0.17, 0.33), color_bota, 14)
    glPopMatrix()