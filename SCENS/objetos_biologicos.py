import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Altura del centro del cuerpo del jugador (esfera de colisión)
ALTURA_CENTRO = 2.0

vesicula = {"pos": (4.0, 0.0, 3.0), "tamano": (1.5, 1.5, 1.5), "colisionando": False}
virus = {"pos_base": (-3.0, 1.5, 5.0), "pos_actual": [-3.0, 1.5, 5.0], "radio": 1.2, "colisionando": False}
atp = {"pos": (0.0, 1.0, 2.0), "umbral": 2.0, "colisionando": False}
globulo = {"pos_base": (-6.0, 1.2, -3.0), "pos_actual": [-6.0, 1.2, -3.0], "radio": 1.3, "alto": 0.9, "colisionando": False}
bacteria = {"pos": (7.0, 0.8, -4.0), "tamano": (3.0, 1.0, 1.2), "angulo": 0.0, "colisionando": False}
anticuerpo = {"base": (0.0, 0.0, -1.5), "pos_actual": [0.0, 0.0, -1.5], "alto": 2.0, "radio": 0.7, "amplitud": 8.0, "colisionando": False}

OBJETOS = {
    "vesicula": vesicula,
    "virus": virus,
    "atp": atp,
    "globulo": globulo,
    "bacteria": bacteria,
    "anticuerpo": anticuerpo,
}

NOMBRES = {
    "vesicula": "Vesícula",
    "virus": "Virus",
    "atp": "Molécula de ATP",
    "globulo": "Glóbulo rojo",
    "bacteria": "Bacteria",
    "anticuerpo": "Anticuerpo",
}

METODOS = {
    "vesicula": "AABB",
    "virus": "Esfera",
    "atp": "Manhattan",
    "globulo": "Cilindro",
    "bacteria": "OBB",
    "anticuerpo": "Cápsula",
}

_quad_alambre = None
_quad_solido = None


#quadric de alambre (se crea una sola vez)
def _quadric_alambre():
    global _quad_alambre
    if _quad_alambre is None:
        _quad_alambre = gluNewQuadric()
        gluQuadricDrawStyle(_quad_alambre, GLU_LINE)
    return _quad_alambre


#quadric sólido (se crea una sola vez)
def _quadric_solido():
    global _quad_solido
    if _quad_solido is None:
        _quad_solido = gluNewQuadric()
        gluQuadricDrawStyle(_quad_solido, GLU_FILL)
    return _quad_solido


#apagar luz para dibujar hitboxes
def _sin_luz():
    estaba_activa = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    return estaba_activa


#restaurar luz después de dibujar hitboxes
def _restaurar_luz(estaba_activa):
    if estaba_activa:
        glEnable(GL_LIGHTING)


#distancia al cuadrado de un punto a un segmento
def _dist2_punto_segmento(px, py, pz, ax, ay, az, bx, by, bz):
    abx, aby, abz = bx - ax, by - ay, bz - az
    apx, apy, apz = px - ax, py - ay, pz - az
    ab2 = abx * abx + aby * aby + abz * abz
    s = 0.0 if ab2 == 0 else max(0.0, min(1.0, (apx * abx + apy * aby + apz * abz) / ab2))
    cx, cy, cz = ax + abx * s, ay + aby * s, az + abz * s
    return (px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2


#objetos que están en colisión
def objetos_en_colision():
    return [nombre for nombre, obj in OBJETOS.items() if obj["colisionando"]]


#sombras (x, z, radio, altura) de los objetos que flotan o están sobre el piso
def sombras():
    return [
        (virus["pos_actual"][0], virus["pos_actual"][2], 1.1, virus["pos_actual"][1]),
        (atp["pos"][0], atp["pos"][2], 0.8, atp["pos"][1]),
        (globulo["pos_actual"][0], globulo["pos_actual"][2], 1.2, globulo["pos_actual"][1]),
        (bacteria["pos"][0], bacteria["pos"][2], 1.5, 0.0),
        (anticuerpo["pos_actual"][0], anticuerpo["pos_actual"][2], 0.7, 0.0),
    ]


#verificar vesícula (AABB en el plano XZ)
def verificar_vesicula(px, pz, radio):
    bx, by, bz = vesicula["pos"]
    bw, bh, bd = vesicula["tamano"]
    overlap_x = (px + radio >= bx - bw / 2) and (px - radio <= bx + bw / 2)
    overlap_z = (pz + radio >= bz - bd / 2) and (pz - radio <= bz + bd / 2)
    vesicula["colisionando"] = overlap_x and overlap_z


#dibujar vesícula
def draw_vesicula(mostrar_hitbox):
    glPushMatrix()
    glTranslatef(*vesicula["pos"])
    glColor3f(0.8, 0.4, 0.1) if vesicula["colisionando"] else glColor3f(0.8, 0.7, 0.2)
    glScalef(*vesicula["tamano"])
    glutSolidCube(1.0)

    if mostrar_hitbox:
        con_luz = _sin_luz()
        glColor3f(1.0, 1.0, 1.0)
        glutWireCube(1.01)
        _restaurar_luz(con_luz)
    glPopMatrix()


#verificar virus (esfera contra esfera)
def verificar_virus(px, py, pz, pradio, t):
    virus["pos_actual"][1] = virus["pos_base"][1] + math.sin(t * 5) * 0.5
    dx = px - virus["pos_actual"][0]
    dy = py - virus["pos_actual"][1]
    dz = pz - virus["pos_actual"][2]
    virus["colisionando"] = (dx * dx + dy * dy + dz * dz) <= ((pradio + virus["radio"]) ** 2)
    return virus["colisionando"]


#dibujar virus
def draw_virus(mostrar_hitbox):
    radio = virus["radio"]
    glPushMatrix()
    glTranslatef(*virus["pos_actual"])
    glColor3f(1.0, 0.0, 0.0) if virus["colisionando"] else glColor3f(0.2, 0.1, 0.2)
    glutSolidSphere(radio, 15, 15)

    glColor3f(0.9, 0.0, 0.0)
    for ang in range(0, 360, 45):
        glPushMatrix()
        glRotatef(ang, 0, 1, 0)
        glTranslatef(radio, 0, 0)
        glutSolidSphere(0.2, 10, 10)
        glPopMatrix()

    if mostrar_hitbox:
        con_luz = _sin_luz()
        glColor3f(1.0, 0.0, 0.0) if virus["colisionando"] else glColor3f(1.0, 1.0, 0.0)
        glutWireSphere(radio * 1.05, 10, 10)
        _restaurar_luz(con_luz)
    glPopMatrix()


#verificar ATP (distancia Manhattan)
def verificar_atp(px, pz):
    dist_manhattan = abs(px - atp["pos"][0]) + abs(pz - atp["pos"][2])
    atp["colisionando"] = dist_manhattan <= atp["umbral"]


#dibujar ATP
def draw_atp(mostrar_hitbox, t):
    glPushMatrix()
    glTranslatef(atp["pos"][0], atp["pos"][1] + math.sin(t * 3) * 0.2, atp["pos"][2])
    glRotatef(t * 50, 0, 1, 0)
    glRotatef(45, 1, 0, 1)
    glColor3f(0.2, 1.0, 0.2) if atp["colisionando"] else glColor3f(0.0, 0.8, 0.8)
    glutSolidOctahedron()

    if mostrar_hitbox:
        con_luz = _sin_luz()
        glColor3f(1.0, 0.0, 1.0)
        glRotatef(45, 0, 1, 0)
        glutWireCube(atp["umbral"] * 0.7)
        _restaurar_luz(con_luz)
    glPopMatrix()


#verificar glóbulo rojo (cilindro vertical: círculo en XZ y rango en Y)
def verificar_globulo(px, py, pz, pradio, t):
    bx, by, bz = globulo["pos_base"]
    globulo["pos_actual"][0] = bx + math.cos(t * 0.8) * 1.5
    globulo["pos_actual"][1] = by + math.sin(t * 2) * 0.15
    globulo["pos_actual"][2] = bz + math.sin(t * 0.8) * 1.5
    cx, cy, cz = globulo["pos_actual"]
    dx = px - cx
    dz = pz - cz
    en_plano = dx * dx + dz * dz <= (pradio + globulo["radio"]) ** 2
    en_altura = abs(py - cy) <= (globulo["alto"] / 2 + pradio)
    globulo["colisionando"] = en_plano and en_altura


#dibujar glóbulo rojo
def draw_globulo(mostrar_hitbox, t):
    cx, cy, cz = globulo["pos_actual"]
    glPushMatrix()
    glTranslatef(cx, cy, cz)
    glPushMatrix()
    glRotatef(90 + math.sin(t * 1.5) * 20, 1, 0, 0)
    glRotatef(t * 40, 0, 0, 1)
    glColor3f(1.0, 0.45, 0.2) if globulo["colisionando"] else glColor3f(0.75, 0.05, 0.10)
    glutSolidTorus(0.35, 0.95, 16, 24)
    glPopMatrix()

    if mostrar_hitbox:
        con_luz = _sin_luz()
        glColor3f(1.0, 0.5, 0.0)
        glTranslatef(0.0, -globulo["alto"] / 2, 0.0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(_quadric_alambre(), globulo["radio"], globulo["radio"], globulo["alto"], 16, 1)
        _restaurar_luz(con_luz)
    glPopMatrix()


#verificar bacteria (caja orientada OBB contra círculo)
def verificar_bacteria(px, pz, pradio, t):
    angulo = (t * 40.0) % 360.0
    bacteria["angulo"] = angulo
    bx, by, bz = bacteria["pos"]
    bw, bh, bd = bacteria["tamano"]
    rad = math.radians(angulo)
    c, s = math.cos(rad), math.sin(rad)
    dx = px - bx
    dz = pz - bz
    # Punto del jugador en el sistema local de la caja girada
    lx = dx * c - dz * s
    lz = dx * s + dz * c
    cercano_x = max(-bw / 2, min(bw / 2, lx))
    cercano_z = max(-bd / 2, min(bd / 2, lz))
    ddx = lx - cercano_x
    ddz = lz - cercano_z
    bacteria["colisionando"] = ddx * ddx + ddz * ddz <= pradio * pradio


#dibujar bacteria
def draw_bacteria(mostrar_hitbox, t):
    bw, bh, bd = bacteria["tamano"]
    glPushMatrix()
    glTranslatef(*bacteria["pos"])
    glRotatef(bacteria["angulo"], 0, 1, 0)

    glColor3f(0.9, 0.5, 0.1) if bacteria["colisionando"] else glColor3f(0.3, 0.7, 0.2)
    glPushMatrix()
    glScalef(bw, bh, bd)
    glutSolidSphere(0.5, 20, 20)
    glPopMatrix()

    # Flagelo ondulante
    con_luz = _sin_luz()
    glColor3f(0.3, 0.9, 0.3)
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    for i in range(21):
        u = i / 20.0
        glVertex3f(-bw / 2 - u * 1.2, 0.0, math.sin(t * 8 + u * 8) * 0.25 * u)
    glEnd()
    glLineWidth(1.0)
    _restaurar_luz(con_luz)

    if mostrar_hitbox:
        con_luz = _sin_luz()
        glColor3f(1.0, 1.0, 1.0)
        glScalef(bw, bh, bd)
        glutWireCube(1.0)
        _restaurar_luz(con_luz)
    glPopMatrix()


#verificar anticuerpo (cápsula vertical que patrulla)
def verificar_anticuerpo(px, py, pz, pradio, t):
    bx, by, bz = anticuerpo["base"]
    anticuerpo["pos_actual"][0] = bx + math.sin(t * 0.7) * anticuerpo["amplitud"]
    x, y, z = anticuerpo["pos_actual"]
    d2 = _dist2_punto_segmento(px, py, pz, x, y, z, x, y + anticuerpo["alto"], z)
    anticuerpo["colisionando"] = d2 <= (pradio + anticuerpo["radio"]) ** 2


#dibujar anticuerpo
def draw_anticuerpo(mostrar_hitbox):
    x, y, z = anticuerpo["pos_actual"]
    quad = _quadric_solido()
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1.0, 0.6, 0.9) if anticuerpo["colisionando"] else glColor3f(0.55, 0.30, 0.85)

    # Tallo
    glutSolidSphere(0.4, 12, 12)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.4, 0.3, 1.2, 12, 1)
    glPopMatrix()

    # Brazos en forma de Y
    glTranslatef(0.0, 1.2, 0.0)
    for ang in (-35, 35):
        glPushMatrix()
        glRotatef(ang, 0, 0, 1)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, 0.25, 0.25, 1.0, 10, 1)
        glTranslatef(0.0, 0.0, 1.0)
        glutSolidSphere(0.3, 10, 10)
        glPopMatrix()
    glPopMatrix()

    if mostrar_hitbox:
        con_luz = _sin_luz()
        glColor3f(1.0, 0.0, 1.0)
        glPushMatrix()
        glTranslatef(x, y, z)
        glutWireSphere(anticuerpo["radio"], 10, 10)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(_quadric_alambre(), anticuerpo["radio"], anticuerpo["radio"], anticuerpo["alto"], 12, 1)
        glTranslatef(0.0, 0.0, anticuerpo["alto"])
        glutWireSphere(anticuerpo["radio"], 10, 10)
        glPopMatrix()
        _restaurar_luz(con_luz)
