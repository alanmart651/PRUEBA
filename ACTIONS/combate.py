import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound
from CHARACTERS import chispa
from RESOURCES import visual as v
from SCENS import objetos_biologicos as bio
from SCENS import efectos as fx

proyectiles = []   # anticuerpos de Mapi (persiguen)
lagrimas = []      # lágrimas de Isaac (en línea recta)
rayos = []         # rayo de sangre de Azazel y rayo de lisis de Perno
destello = 0.0     # el HUD lo usa para el flash de Chispa

_quad = None


# Inicia: quadric para los rayos cilíndricos (se crea una sola vez)
def _quadric():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
        gluQuadricNormals(_quad, GLU_SMOOTH)
    return _quad


# Inicia: limpiar proyectiles y rayos
def limpiar():
    global destello
    proyectiles.clear()
    lagrimas.clear()
    rayos.clear()
    destello = 0.0
    chispa.brillo_extra = 0.0


# Inicia: ataque del personaje (consume energía y respeta el enfriamiento)
def atacar(j, st, personaje):
    if j["cd"] > 0.0:
        return False
    if j["energia"] < st["costo"]:
        j["aviso"] = "Sin energía: recoge ATP"
        j["aviso_t"] = 1.2
        return False
    objetivo = bio.mas_cercano(j["x"], j["z"], 12.0)
    if objetivo is not None:
        j["ang"] = math.degrees(math.atan2(objetivo["x"] - j["x"], objetivo["z"] - j["z"]))
    j["energia"] -= st["costo"]
    j["cd"] = st["cooldown"]
    j["ataque_t"] = 0.35
    ATAQUES[personaje](j, st)
    play_sound("arriba")
    return True


def _frente(j):
    a = math.radians(j["ang"])
    return math.sin(a), math.cos(a)


# Isaac: dispara una lágrima esférica hacia donde mira
def _lagrima(j, st):
    fx_, fz_ = _frente(j)
    x, z = j["x"] + fx_ * 1.3, j["z"] + fz_ * 1.3
    lagrimas.append({"x": x, "y": 2.3, "z": z, "dx": fx_, "dz": fz_, "vida": 1.1, "dano": st["dano"]})
    fx.explosion((x, 2.3, z), (0.6, 0.8, 1.0), 5, 3.0, 0.25, 5.0, 0.0)


# Azazel: rayo de sangre (brimstone) que sale al frente y quema todo lo que cruza
def _brimstone(j, st):
    fx_, fz_ = _frente(j)
    rayos.append({"tipo": "brimstone", "x": j["x"], "z": j["z"], "ang": j["ang"], "largo": 9.5,
                  "vida": 0.5, "max": 0.5, "tick": 0.0, "dano": st["dano"] / 5.0})
    fx.explosion((j["x"] + fx_ * 1.2, 2.2, j["z"] + fz_ * 1.2), (1.0, 0.1, 0.05), 14, 5.0, 0.35, 8.0, 0.0)


# Chispa (célula dendrítica): destello que aturde
def _destello(j, st):
    global destello
    radio = 9.0
    for e in bio.patogenos_vivos():
        if math.hypot(e["x"] - j["x"], e["z"] - j["z"]) <= radio + e["radio"]:
            bio.aturdir(e, 3.0)
            bio.danar(e, st["dano"])
    destello = 1.0
    chispa.brillo_extra = 1.0
    fx.anillo(j["x"], j["z"], 1.0, radio, 0.55, (0.85, 0.6, 1.0))
    fx.explosion((j["x"], 3.8, j["z"]), (0.9, 0.7, 1.0), 40, 9.0, 0.7, 9.0, 0.0)


# Mapi (linfocito B de memoria): anticuerpo que marca y persigue con suavidad
def _anticuerpo(j, st):
    fx_, fz_ = _frente(j)
    proyectiles.append({"x": j["x"] + fx_ * 1.2, "y": 2.0, "z": j["z"] + fz_ * 1.2,
                        "dx": fx_, "dz": fz_, "vida": 2.4, "dano": st["dano"], "giro": 0.0})
    fx.explosion((j["x"] + fx_ * 1.2, 2.0, j["z"] + fz_ * 1.2), (1.0, 0.5, 0.95), 8, 4.0, 0.3, 6.0, 0.0)


# Brote (fibroblasto cardiaco): lisis débil y polen reparador
def _lisis_debil(j, st):
    radio = 3.4
    for e in bio.patogenos_vivos():
        if math.hypot(e["x"] - j["x"], e["z"] - j["z"]) <= radio + e["radio"]:
            bio.danar(e, st["dano"])
    fx.anillo(j["x"], j["z"], 0.6, radio, 0.4, (0.6, 1.0, 0.4))
    fx.flotar((j["x"], 1.5, j["z"]), (1.0, 0.9, 0.3), 14, 1.2, 6.0)


# Perno (nanobot): rayo frontal de lisis instantánea
def _rayo(j, st):
    largo, medio = 11.0, 1.1
    fx_, fz_ = _frente(j)
    for e in bio.patogenos_vivos():
        dx, dz = e["x"] - j["x"], e["z"] - j["z"]
        a = dx * fx_ + dz * fz_
        p = abs(dx * fz_ - dz * fx_)
        if 0.0 < a < largo + e["radio"] and p < medio + e["radio"]:
            bio.danar(e, 130 if e["tipo"] == "jefe" else 9999)
    rayos.append({"tipo": "perno", "x": j["x"], "z": j["z"], "ang": j["ang"], "largo": largo, "vida": 0.3})
    for i in range(16):
        d = largo * i / 15.0
        fx.particula((j["x"] + fx_ * d, 2.0, j["z"] + fz_ * d), (0.0, 0.5, 0.0), (0.4, 1.0, 1.0), 0.4, 8.0)


ATAQUES = {"isaac": _lagrima, "azazel": _brimstone, "chispa": _destello,
           "mapi": _anticuerpo, "brote": _lisis_debil, "perno": _rayo}


# Inicia: daño de un tick del rayo de sangre a todo lo que cruza su línea
def _quemar(r):
    a = math.radians(r["ang"])
    fx_, fz_ = math.sin(a), math.cos(a)
    medio = 1.0
    for e in bio.patogenos_vivos():
        dx, dz = e["x"] - r["x"], e["z"] - r["z"]
        largo_e = dx * fx_ + dz * fz_
        ancho_e = abs(dx * fz_ - dz * fx_)
        if 0.0 < largo_e < r["largo"] + e["radio"] and ancho_e < medio + e["radio"]:
            bio.danar(e, r["dano"])
    d = r["largo"] * (0.2 + 0.8 * ((r["max"] - r["vida"]) * 7.0 % 1.0))
    fx.particula((r["x"] + fx_ * d, 2.2, r["z"] + fz_ * d), (fz_ * 2.0, 1.5, -fx_ * 2.0), (1.0, 0.2, 0.1), 0.35, 8.0)


# Inicia: avanzar proyectiles, rayos y destellos
def actualizar(dt, j=None):
    global destello
    destello = max(0.0, destello - dt * 2.5)
    chispa.brillo_extra = max(0.0, chispa.brillo_extra - dt * 1.5)

    for r in rayos[:]:
        r["vida"] -= dt
        if r["tipo"] == "brimstone" and r["vida"] > 0.0:
            if j is not None:
                # el rayo sigue al personaje mientras dura
                r["x"], r["z"] = j["x"], j["z"]
            r["tick"] -= dt
            if r["tick"] <= 0.0:
                r["tick"] = 0.1
                _quemar(r)
        if r["vida"] <= 0.0:
            rayos.remove(r)

    for p in lagrimas[:]:
        p["vida"] -= dt
        p["x"] += p["dx"] * 22.0 * dt
        p["z"] += p["dz"] * 22.0 * dt
        # al final de su alcance la lágrima cae un poco
        p["y"] -= max(0.0, 0.5 - p["vida"]) * 3.0 * dt
        fx.particula((p["x"], p["y"], p["z"]), (0.0, 0.2, 0.0), (0.5, 0.75, 1.0), 0.25, 5.0)
        golpe = None
        for e in bio.patogenos_vivos():
            if math.hypot(e["x"] - p["x"], e["z"] - p["z"]) <= e["radio"] + 0.35 and abs(e["y"] - p["y"]) <= e["radio"] + 1.2:
                golpe = e
                break
        nx, nz = bio.resolver(p["x"], p["z"], 0.2)
        choca = abs(nx - p["x"]) > 1e-3 or abs(nz - p["z"]) > 1e-3
        if golpe is not None:
            bio.danar(golpe, p["dano"])
        if golpe is not None or choca or p["vida"] <= 0.0:
            fx.explosion((p["x"], p["y"], p["z"]), (0.55, 0.78, 1.0), 9, 4.5, 0.4, 6.0)
            lagrimas.remove(p)

    for p in proyectiles[:]:
        p["vida"] -= dt
        objetivo = bio.mas_cercano(p["x"], p["z"], 15.0)
        if objetivo is not None:
            ox, oz = objetivo["x"] - p["x"], objetivo["z"] - p["z"]
            d = max(0.01, math.hypot(ox, oz))
            k = min(1.0, 3.5 * dt)
            p["dx"] += (ox / d - p["dx"]) * k
            p["dz"] += (oz / d - p["dz"]) * k
            n = max(0.01, math.hypot(p["dx"], p["dz"]))
            p["dx"], p["dz"] = p["dx"] / n, p["dz"] / n
            p["y"] += (objetivo["y"] - p["y"]) * min(1.0, 4.0 * dt)
        p["x"] += p["dx"] * 19.0 * dt
        p["z"] += p["dz"] * 19.0 * dt
        p["giro"] += 400.0 * dt
        fx.particula((p["x"], p["y"], p["z"]), (0.0, 0.3, 0.0), (1.0, 0.45, 0.9), 0.3, 6.0)
        golpe = None
        for e in bio.patogenos_vivos():
            if math.hypot(e["x"] - p["x"], e["z"] - p["z"]) <= e["radio"] + 0.6 and abs(e["y"] - p["y"]) <= e["radio"] + 1.2:
                golpe = e
                break
        if golpe is not None:
            bio.danar(golpe, p["dano"], marca=4.0)
            fx.explosion((p["x"], p["y"], p["z"]), (1.0, 0.5, 0.95), 14, 6.0, 0.5, 7.0)
            proyectiles.remove(p)
        elif p["vida"] <= 0.0 or abs(p["x"]) > 22.0 or abs(p["z"]) > 22.0:
            proyectiles.remove(p)


# Inicia: dibujo del rayo de sangre (núcleo con emisión roja y resplandor aditivo)
def _dibujar_brimstone(r, t):
    k = r["vida"] / r["max"]
    g = 0.30 + 0.25 * min(1.0, k * 3.0) + 0.04 * math.sin(t * 60.0)
    largo = r["largo"]
    glPushMatrix()
    glTranslatef(r["x"], 2.2, r["z"])
    glRotatef(r["ang"], 0, 1, 0)
    glTranslatef(0.0, 0.0, 1.0)
    v.material(10.0, 0.0, (1.0, 0.08, 0.02))
    glColor3f(0.95, 0.06, 0.02)
    gluCylinder(_quadric(), g, g * 0.85, largo, 18, 1)
    glutSolidSphere(g * 1.3, 14, 14)
    glTranslatef(0.0, 0.0, largo)
    glutSolidSphere(g * 1.1, 14, 14)
    glPopMatrix()
    v.material(48.0, 0.35)

    v.iniciar_aditivo()
    glPushMatrix()
    glTranslatef(r["x"], 2.2, r["z"])
    glRotatef(r["ang"], 0, 1, 0)
    glTranslatef(0.0, 0.0, 1.0)
    for escala, alfa in ((1.8, 0.30), (2.8, 0.14)):
        glColor4f(1.0, 0.15, 0.05, alfa * k)
        gluCylinder(_quadric(), g * escala, g * escala * 0.9, largo, 16, 1)
    glColor4f(1.0, 0.8, 0.6, 0.8 * k)
    gluCylinder(_quadric(), g * 0.4, g * 0.35, largo, 10, 1)
    glPopMatrix()
    v.terminar_transparencia()


# Inicia: dibujo de lágrimas, proyectiles y rayos
def dibujar(t):
    for p in lagrimas:
        glPushMatrix()
        glTranslatef(p["x"], p["y"], p["z"])
        v.material(100.0, 0.9, (0.1, 0.2, 0.4))
        glColor3f(0.55, 0.78, 1.0)
        glutSolidSphere(0.35, 14, 14)
        glPopMatrix()
        v.material(48.0, 0.35)
        v.halo((p["x"], p["y"], p["z"]), 0.9, (0.5, 0.75, 1.0), 0.25, 3)
    for p in proyectiles:
        glPushMatrix()
        glTranslatef(p["x"], p["y"], p["z"])
        glRotatef(p["giro"], 0, 1, 0)
        v.material(70.0, 0.7, (0.4, 0.1, 0.35))
        glColor3f(0.85, 0.4, 1.0)
        glutSolidSphere(0.22, 10, 10)
        for ang in (-40, 40):
            glPushMatrix()
            glRotatef(ang, 0, 0, 1)
            glTranslatef(0.0, 0.25, 0.0)
            glScalef(0.09, 0.4, 0.09)
            glColor3f(1.0, 0.55, 0.95)
            glutSolidCube(1.0)
            glPopMatrix()
        glPopMatrix()
        v.material(48.0, 0.35)
        v.halo((p["x"], p["y"], p["z"]), 0.9, (1.0, 0.4, 0.9), 0.3, 3)
    for r in rayos:
        if r["tipo"] == "brimstone":
            _dibujar_brimstone(r, t)
            continue
        k = r["vida"] / 0.3
        v.iniciar_aditivo()
        glPushMatrix()
        glTranslatef(r["x"], 2.0, r["z"])
        glRotatef(r["ang"], 0, 1, 0)
        glTranslatef(0.0, 0.0, r["largo"] / 2.0)
        glColor4f(0.3, 0.95, 1.0, 0.55 * k)
        glScalef(0.35 * k + 0.1, 0.35 * k + 0.1, r["largo"])
        glutSolidCube(1.0)
        glColor4f(1.0, 1.0, 1.0, 0.7 * k)
        glScalef(0.4, 0.4, 1.0)
        glutSolidCube(1.0)
        glPopMatrix()
        v.terminar_transparencia()
