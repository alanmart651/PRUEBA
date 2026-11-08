import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound
from CHARACTERS import chispa
from RESOURCES import visual as v
from SCENS import objetos_biologicos as bio
from SCENS import efectos as fx

proyectiles = []   # anticuerpos de Mapi
rayos = []         # rayos de lisis de Perno
destello = 0.0     # el HUD lo usa para el flash de Chispa


# Inicia: limpiar proyectiles y rayos
def limpiar():
    global destello
    proyectiles.clear()
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


# Isaac (macrófago): fagocitosis, atrae y engloba a los patógenos cercanos
def _fagocitosis(j, st):
    radio = 4.8
    for e in bio.patogenos_vivos():
        if math.hypot(e["x"] - j["x"], e["z"] - j["z"]) <= radio + e["radio"]:
            e["x"] += (j["x"] - e["x"]) * 0.35
            e["z"] += (j["z"] - e["z"]) * 0.35
            bio.danar(e, st["dano"])
    fx.anillo(j["x"], j["z"], radio, 1.0, 0.5, (1.0, 0.75, 0.65))
    for i in range(18):
        a = i * 0.349
        fx.particula((j["x"] + math.cos(a) * radio, 1.4, j["z"] + math.sin(a) * radio),
                     (-math.cos(a) * 9.0, 0.5, -math.sin(a) * 9.0), (1.0, 0.8, 0.7), 0.45, 8.0)


# Azazel (linfocito T citotóxico): lisis citolítica en un cono corto
def _citolisis(j, st):
    rango, mitad = 4.6, 60.0
    fx_, fz_ = _frente(j)
    for e in bio.patogenos_vivos():
        dx, dz = e["x"] - j["x"], e["z"] - j["z"]
        d = math.hypot(dx, dz)
        if d > rango + e["radio"]:
            continue
        if d < e["radio"] + 0.8 or (dx * fx_ + dz * fz_) / max(d, 0.01) > math.cos(math.radians(mitad)):
            bio.danar(e, st["dano"])
    fx.arco(j["x"], j["z"], j["ang"], rango, mitad, (1.0, 0.2, 0.25))
    fx.anillo(j["x"] + fx_ * 2.0, j["z"] + fz_ * 2.0, 0.5, 2.4, 0.3, (1.0, 0.25, 0.3))


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
    rayos.append({"x": j["x"], "z": j["z"], "ang": j["ang"], "largo": largo, "vida": 0.3})
    for i in range(16):
        d = largo * i / 15.0
        fx.particula((j["x"] + fx_ * d, 2.0, j["z"] + fz_ * d), (0.0, 0.5, 0.0), (0.4, 1.0, 1.0), 0.4, 8.0)


ATAQUES = {"isaac": _fagocitosis, "azazel": _citolisis, "chispa": _destello,
           "mapi": _anticuerpo, "brote": _lisis_debil, "perno": _rayo}


# Inicia: avanzar proyectiles, rayos y destellos
def actualizar(dt):
    global destello
    destello = max(0.0, destello - dt * 2.5)
    chispa.brillo_extra = max(0.0, chispa.brillo_extra - dt * 1.5)
    for r in rayos[:]:
        r["vida"] -= dt
        if r["vida"] <= 0.0:
            rayos.remove(r)
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


# Inicia: dibujo de proyectiles y rayos
def dibujar(t):
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
