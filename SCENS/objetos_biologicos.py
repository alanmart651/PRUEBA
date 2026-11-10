import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import visual as v
from SCENS import efectos as fx

# Altura del centro del cuerpo del jugador (esfera de colisión)
ALTURA_CENTRO = 2.0
LIMITE = 16.5
DURACION_LISIS = 0.7

# Datos de cada tipo: método de colisión, vida, daño por contacto y ficha informativa
DATOS = {
    "virus_a": {"nombre": "Virus de influenza", "metodo": "Esfera", "hp": 30, "radio": 0.8, "dano": 8,
                "tam": "~100 nm", "info": "Infecta células respiratorias y se replica dentro de ellas."},
    "virus_b": {"nombre": "Coronavirus", "metodo": "Esfera", "hp": 40, "radio": 0.9, "dano": 10,
                "tam": "~100 nm", "info": "Usa sus espículas para entrar a la célula; se lanza en picada."},
    "bacilo": {"nombre": "Bacilo (E. coli)", "metodo": "OBB", "hp": 70, "radio": 1.0, "dano": 12,
               "tam": "2 a 3 um de largo", "info": "Bacteria en forma de bastón con flagelo para moverse."},
    "coco": {"nombre": "Estafilococo (coco)", "metodo": "Esfera", "hp": 90, "radio": 1.4, "dano": 10,
             "tam": "~1 um", "info": "Bacteria esférica que forma racimos y se divide al ser destruida."},
    "jefe": {"nombre": "Biopelícula bacteriana", "metodo": "Esfera", "hp": 450, "radio": 3.2, "dano": 20,
             "tam": "de um a mm", "info": "Comunidad de bacterias protegida por una matriz pegajosa."},
    "eritrocito": {"nombre": "Eritrocito", "metodo": "Cilindro", "radio": 0.9, "alto": 1.0,
                   "tam": "~7 um", "info": "Glóbulo rojo: transporta oxígeno con hemoglobina. Cura salud."},
    "atp": {"nombre": "Molécula de ATP", "metodo": "Manhattan", "umbral": 1.9,
            "tam": "~1 nm", "info": "Moneda de energía de la célula. Recarga tu energía."},
    "anticuerpo": {"nombre": "Anticuerpo", "metodo": "Cápsula", "radio": 0.7, "alto": 1.8,
                   "tam": "~10 nm", "info": "Proteína en Y que se une al antígeno y marca al patógeno."},
    "vesicula": {"nombre": "Vesícula", "metodo": "AABB", "tamano": (2.4, 2.4, 2.4),
                 "tam": "50 a 200 nm", "info": "Bolsa de membrana que transporta moléculas dentro de la célula."},
}
NOMBRES = {k: d["nombre"] for k, d in DATOS.items()}
METODOS = {k: d["metodo"] for k, d in DATOS.items()}
PATOGENOS = ("virus_a", "virus_b", "bacilo", "coco", "jefe")

entidades = []
eventos = []
circulos = []
config = {"prob_eri": 0.15}
total_inicial = 0

_quad = None


# Inicia: quadric sólido (se crea una sola vez)
def _quadric():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
        gluQuadricDrawStyle(_quad, GLU_FILL)
        gluQuadricNormals(_quad, GLU_SMOOTH)
    return _quad


# Inicia: direcciones de las espículas (vértices de un icosaedro)
def _calcular_espinas():
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    pts = []
    for a in (-1.0, 1.0):
        for b in (-phi, phi):
            pts += [(0.0, a, b), (a, b, 0.0), (b, 0.0, a)]
    out = []
    for x, y, z in pts:
        n = math.sqrt(x * x + y * y + z * z)
        x, y, z = x / n, y / n, z / n
        ax, ay = -y, x
        if math.hypot(ax, ay) < 1e-6:
            ax, ay = 1.0, 0.0
        out.append((math.degrees(math.acos(z)), ax, ay))
    return out


ESPINAS = _calcular_espinas()


# =====================================================================
# CREACIÓN DE ENTIDADES
# =====================================================================

# Inicia: crear una entidad
def _nueva(tipo, x, z, y=None, **extra):
    d = DATOS[tipo]
    base_y = y if y is not None else {"virus_a": 1.6, "virus_b": 1.7, "bacilo": 0.9, "eritrocito": 1.2,
                                      "atp": 1.3, "anticuerpo": 0.2, "vesicula": 1.2}.get(tipo, 1.0)
    e = {"tipo": tipo, "x": x, "z": z, "y": base_y, "y0": base_y,
         "hp": d.get("hp", 0), "hp_max": d.get("hp", 0), "estado": "vivo", "t_lisis": 0.0,
         "aturdido": 0.0, "marcado": 0.0, "golpe": 0.0, "retro": 0.0, "colisionando": False,
         "fase": random.uniform(0.0, 6.28), "ang": random.uniform(0.0, 360.0),
         "cd": random.uniform(1.0, 3.0), "dash": 0.0, "dx": 0.0, "dz": 0.0, "orb": random.uniform(0.0, 6.28),
         "nivel": 0, "radio": d.get("radio", 1.0), "tam": d.get("tamano", (3.3, 1.0, 1.2))}
    e.update(extra)
    if tipo in ("coco", "jefe"):
        e["y"] = e["y0"] = e["radio"]
    entidades.append(e)
    return e


# Inicia: preparar un nivel
def iniciar_nivel(escenario):
    global total_inicial
    entidades.clear()
    eventos.clear()
    circulos.clear()
    fx.limpiar()
    if escenario == 0:
        circulos.append((0.0, 0.0, 4.0))
        for tipo, x, z in (("virus_a", -10, -8), ("virus_a", 11, -6), ("virus_b", 8, -12),
                           ("bacilo", -11, 2), ("coco", 3, -11)):
            _nueva(tipo, x, z)
        for tipo, x, z in (("eritrocito", -7, 6), ("eritrocito", 9, 5), ("atp", -7, -2),
                           ("atp", 7, -2), ("anticuerpo", 0, -8), ("vesicula", 6, 3), ("vesicula", -8, -6)):
            _nueva(tipo, x, z)
    elif escenario == 1:
        # Vaso sanguíneo: dominan los virus
        for tipo, x, z in (("virus_a", -12, -6), ("virus_a", 12, -8), ("virus_a", -4, -10), ("virus_a", 6, -12),
                           ("virus_b", -9, -12), ("virus_b", 10, -2), ("virus_b", 0, -8),
                           ("bacilo", -12, 1), ("coco", 4, -5)):
            _nueva(tipo, x, z)
        for tipo, x, z in (("eritrocito", -8, 4), ("eritrocito", 8, 6), ("eritrocito", 0, 2),
                           ("atp", -7, -2), ("atp", 7, -3), ("atp", 0, 8), ("anticuerpo", 0, -4),
                           ("vesicula", -4, -6), ("vesicula", 4, -7)):
            _nueva(tipo, x, z)
    else:
        # Ganglio linfático: más patógenos y el jefe
        for tipo, x, z in (("virus_a", -12, -4), ("virus_a", 12, -5), ("virus_a", -6, -12), ("virus_a", 7, -11),
                           ("virus_b", -10, -10), ("virus_b", 10, -9), ("virus_b", 0, -6),
                           ("bacilo", -12, 2), ("bacilo", 12, 4), ("bacilo", -8, -13),
                           ("coco", -5, -2), ("coco", 6, -3), ("jefe", 0, -12.5)):
            _nueva(tipo, x, z)
        for tipo, x, z in (("eritrocito", -8, 6), ("eritrocito", 8, 7), ("eritrocito", 0, 4),
                           ("atp", -9, 0), ("atp", 9, 0), ("atp", -3, 7), ("atp", 3, -3),
                           ("anticuerpo", -6, 5), ("anticuerpo", 6, -8),
                           ("vesicula", -7, -8), ("vesicula", 7, -6), ("vesicula", 0, -1)):
            _nueva(tipo, x, z)
    total_inicial = sum(1 for e in entidades if e["tipo"] in PATOGENOS)


# =====================================================================
# CONSULTAS
# =====================================================================

# Inicia: patógenos vivos (para ataques y HUD)
def patogenos_vivos():
    return [e for e in entidades if e["tipo"] in PATOGENOS and e["estado"] == "vivo"]


# Inicia: ¿quedan patógenos, incluidos los que están en lisis?
def hay_patogenos():
    return any(e["tipo"] in PATOGENOS for e in entidades)


# Inicia: patógeno más cercano a un punto
def mas_cercano(x, z, rango):
    mejor, md = None, rango * rango
    for e in patogenos_vivos():
        d = (e["x"] - x) ** 2 + (e["z"] - z) ** 2
        if d < md:
            mejor, md = e, d
    return mejor


# Inicia: entidad (patógeno o recolectable) más cercana para la ficha informativa
def ficha_cercana(x, z, rango=9.0):
    mejor, md = None, rango * rango
    for e in entidades:
        if e["tipo"] == "vesicula" or e["estado"] != "vivo":
            continue
        d = (e["x"] - x) ** 2 + (e["z"] - z) ** 2
        if d < md:
            mejor, md = e, d
    return mejor


def jefe_vivo():
    for e in entidades:
        if e["tipo"] == "jefe" and e["estado"] == "vivo":
            return e
    return None


# Inicia: objetos que tocan al jugador (para el panel de colisiones)
def objetos_en_colision():
    return sorted({e["tipo"] for e in entidades if e["colisionando"]})


# Inicia: sombras (x, z, radio, altura) de lo que flota o está sobre el piso
def sombras():
    out = []
    for e in entidades:
        if e["tipo"] == "vesicula":
            out.append((e["x"], e["z"], 1.5, 0.0))
        else:
            r = e["radio"] if e["tipo"] in PATOGENOS else 0.8
            out.append((e["x"], e["z"], min(r, 3.0) * 1.0, max(0.0, e["y"] - 0.4)))
    return out


# Inicia: tomar y vaciar la cola de eventos
def tomar_eventos():
    sal = list(eventos)
    eventos.clear()
    return sal


# =====================================================================
# DAÑO, ESTADOS Y LISIS
# =====================================================================

# Inicia: dañar a un patógeno; devuelve True si entra en lisis
def danar(e, cantidad, marca=0.0):
    if e["tipo"] not in PATOGENOS or e["estado"] != "vivo":
        return False
    if e["marcado"] > 0.0:
        cantidad *= 1.8
    if marca > 0.0:
        e["marcado"] = max(e["marcado"], marca)
    e["hp"] -= cantidad
    e["golpe"] = 0.15
    fx.explosion((e["x"], e["y"], e["z"]), (1.0, 0.9, 0.6), 6, 4.0, 0.4, 6.0)
    if e["hp"] <= 0.0:
        _iniciar_lisis(e)
        return True
    return False


def aturdir(e, seg):
    if e["tipo"] in PATOGENOS and e["estado"] == "vivo":
        e["aturdido"] = max(e["aturdido"], seg)


def marcar_todos(seg):
    for e in patogenos_vivos():
        e["marcado"] = max(e["marcado"], seg)


# Inicia: comenzar la lisis (la membrana se deforma, se rompe y se desvanece)
def _iniciar_lisis(e):
    e["estado"] = "lisis"
    e["t_lisis"] = 0.0
    e["colisionando"] = False
    colores = {"virus_a": (0.5, 1.0, 0.3), "virus_b": (1.0, 0.5, 0.3), "bacilo": (0.4, 1.0, 0.4),
               "coco": (1.0, 0.85, 0.2), "jefe": (1.0, 0.6, 0.2)}
    c = colores.get(e["tipo"], (1.0, 1.0, 1.0))
    n = 70 if e["tipo"] == "jefe" else 34
    fx.explosion((e["x"], e["y"], e["z"]), c, n, 8.0, 1.0, 13.0)
    fx.anillo(e["x"], e["z"], 0.5, e["radio"] * 2.4 + 1.0, 0.6, c)
    eventos.append(("eliminado", e))


# Inicia: premios al terminar la lisis y división del coco
def _terminar_lisis(e):
    if e["tipo"] == "coco" and e["nivel"] == 0:
        for lado in (-1, 1):
            _nueva("coco", e["x"] + lado * 1.4, e["z"], nivel=1, radio=0.8, hp=30, hp_max=30)
    if e["tipo"] == "jefe" or random.random() < config["prob_eri"]:
        _nueva("eritrocito", e["x"], e["z"])
    if e["tipo"] == "jefe" or random.random() < 0.25:
        _nueva("atp", e["x"] + 1.0, e["z"] + 0.6)
    entidades.remove(e)


# =====================================================================
# MOVIMIENTO Y OBSTÁCULOS
# =====================================================================

# Inicia: sacar un círculo de los obstáculos (corazón y vesículas)
def resolver(x, z, r):
    for cx, cz, cr in circulos:
        dx, dz = x - cx, z - cz
        d = math.hypot(dx, dz)
        m = cr + r
        if d < m:
            if d < 1e-6:
                dx, dz, d = 1.0, 0.0, 1.0
            x, z = cx + dx / d * m, cz + dz / d * m
    for e in entidades:
        if e["tipo"] != "vesicula":
            continue
        hw = e["tam"][0] / 2.0 + r
        hd = e["tam"][2] / 2.0 + r
        dx, dz = x - e["x"], z - e["z"]
        if abs(dx) < hw and abs(dz) < hd:
            px, pz = hw - abs(dx), hd - abs(dz)
            if px < pz:
                x += px * (1.0 if dx >= 0 else -1.0)
            else:
                z += pz * (1.0 if dz >= 0 else -1.0)
    return max(-LIMITE, min(LIMITE, x)), max(-LIMITE, min(LIMITE, z))


def _hacia(e, ox, oz, vel, dt):
    dx, dz = ox - e["x"], oz - e["z"]
    d = math.hypot(dx, dz)
    if d > 0.01:
        e["x"] += dx / d * vel * dt
        e["z"] += dz / d * vel * dt


# Inicia: comportamiento de cada patógeno
def _ia(e, dt, px, pz):
    tipo = e["tipo"]
    if e["aturdido"] > 0.0:
        return
    if e["retro"] > 0.0:
        _hacia(e, px, pz, -4.5, dt)
        return
    if tipo == "virus_a":
        _hacia(e, px, pz, 5.5, dt)
    elif tipo == "virus_b":
        e["cd"] -= dt
        if e["dash"] > 0.0:
            e["dash"] -= dt
            e["x"] += e["dx"] * 17.0 * dt
            e["z"] += e["dz"] * 17.0 * dt
        else:
            e["orb"] += 1.1 * dt
            _hacia(e, px + math.cos(e["orb"]) * 7.0, pz + math.sin(e["orb"]) * 7.0, 7.5, dt)
            if e["cd"] <= 0.0:
                d = max(0.01, math.hypot(px - e["x"], pz - e["z"]))
                e["dx"], e["dz"] = (px - e["x"]) / d, (pz - e["z"]) / d
                e["dash"] = 0.7
                e["cd"] = 3.5 + random.uniform(0.0, 1.5)
    elif tipo == "bacilo":
        e["cd"] -= dt
        if e["cd"] <= 0.0:
            e["cd"] = 2.2 + random.uniform(0.0, 1.0)
            e["ang"] = math.degrees(math.atan2(-(pz - e["z"]), px - e["x"]))
        a = math.radians(e["ang"])
        e["x"] += math.cos(a) * 4.6 * dt
        e["z"] += -math.sin(a) * 4.6 * dt
        if abs(e["x"]) > LIMITE:
            e["ang"] = 180.0 - e["ang"]
        if abs(e["z"]) > LIMITE:
            e["ang"] = -e["ang"]
    elif tipo == "coco":
        _hacia(e, px, pz, 2.6 if e["nivel"] == 0 else 4.0, dt)
    elif tipo == "jefe":
        furia = e["hp"] < e["hp_max"] * 0.5
        e["cd"] -= dt
        if e["dash"] > 0.0:
            e["dash"] -= dt
            e["x"] += e["dx"] * 13.0 * dt
            e["z"] += e["dz"] * 13.0 * dt
        else:
            _hacia(e, px, pz, 4.2 if furia else 3.0, dt)
            if e["cd"] <= 0.0:
                d = max(0.01, math.hypot(px - e["x"], pz - e["z"]))
                e["dx"], e["dz"] = (px - e["x"]) / d, (pz - e["z"]) / d
                e["dash"] = 0.9
                e["cd"] = 4.0 if furia else 5.5


# Inicia: separar a los patógenos para que no se encimen
def _separar(patogenos):
    for i in range(len(patogenos)):
        for j in range(i + 1, len(patogenos)):
            a, b = patogenos[i], patogenos[j]
            dx, dz = b["x"] - a["x"], b["z"] - a["z"]
            d = math.hypot(dx, dz)
            m = (a["radio"] + b["radio"]) * 0.8
            if 1e-6 < d < m:
                push = (m - d) * 0.5
                a["x"] -= dx / d * push
                a["z"] -= dz / d * push
                b["x"] += dx / d * push
                b["z"] += dz / d * push


# =====================================================================
# COLISIONES CON EL JUGADOR
# =====================================================================

# Esfera contra esfera (virus, coco y jefe)
def _col_esfera(e, px, py, pz, pr):
    dx, dy, dz = px - e["x"], py - e["y"], pz - e["z"]
    return dx * dx + dy * dy + dz * dz <= (pr + e["radio"]) ** 2


# Caja orientada (OBB) contra círculo (bacilo); si el jugador salta por encima no lo toca
def _col_obb(e, px, py, pz, pr):
    if py - ALTURA_CENTRO > 1.0:
        return False
    bw, bh, bd = e["tam"]
    rad = math.radians(e["ang"])
    c, s = math.cos(rad), math.sin(rad)
    dx, dz = px - e["x"], pz - e["z"]
    lx = dx * c - dz * s
    lz = dx * s + dz * c
    ddx = lx - max(-bw / 2, min(bw / 2, lx))
    ddz = lz - max(-bd / 2, min(bd / 2, lz))
    return ddx * ddx + ddz * ddz <= pr * pr


# Cilindro vertical: círculo en XZ y rango en Y (eritrocito)
def _col_cilindro(e, px, py, pz, pr):
    dx, dz = px - e["x"], pz - e["z"]
    en_plano = dx * dx + dz * dz <= (pr + e["radio"]) ** 2
    return en_plano and abs(py - e["y"]) <= (DATOS["eritrocito"]["alto"] / 2 + pr)


# Distancia Manhattan (rombo en XZ) para el ATP
def _col_manhattan(e, px, py, pz, pr):
    return abs(px - e["x"]) + abs(pz - e["z"]) <= DATOS["atp"]["umbral"] + pr * 0.5


# Distancia punto-segmento al cuadrado (cápsula del anticuerpo)
def _dist2_punto_segmento(px, py, pz, ax, ay, az, bx, by, bz):
    abx, aby, abz = bx - ax, by - ay, bz - az
    apx, apy, apz = px - ax, py - ay, pz - az
    ab2 = abx * abx + aby * aby + abz * abz
    s = 0.0 if ab2 == 0 else max(0.0, min(1.0, (apx * abx + apy * aby + apz * abz) / ab2))
    cx, cy, cz = ax + abx * s, ay + aby * s, az + abz * s
    return (px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2


def _col_capsula(e, px, py, pz, pr):
    alto = DATOS["anticuerpo"]["alto"]
    d2 = _dist2_punto_segmento(px, py, pz, e["x"], e["y"], e["z"], e["x"], e["y"] + alto, e["z"])
    return d2 <= (pr + DATOS["anticuerpo"]["radio"]) ** 2


# Caja alineada a los ejes (AABB) en el plano XZ (vesícula)
def _col_aabb(e, px, py, pz, pr):
    bw, bh, bd = e["tam"]
    return (px + pr >= e["x"] - bw / 2 and px - pr <= e["x"] + bw / 2 and
            pz + pr >= e["z"] - bd / 2 and pz - pr <= e["z"] + bd / 2)


COLISION = {"virus_a": _col_esfera, "virus_b": _col_esfera, "coco": _col_esfera, "jefe": _col_esfera,
            "bacilo": _col_obb, "eritrocito": _col_cilindro, "atp": _col_manhattan,
            "anticuerpo": _col_capsula, "vesicula": _col_aabb}


# Inicia: actualizar todas las entidades y detectar contactos
def actualizar(dt, t, px, pz, py, pr):
    patogenos = []
    for e in entidades[:]:
        tipo = e["tipo"]
        for clave in ("aturdido", "marcado", "golpe", "retro"):
            if e[clave] > 0.0:
                e[clave] = max(0.0, e[clave] - dt)
        if e["estado"] == "lisis":
            e["t_lisis"] += dt
            if e["t_lisis"] >= DURACION_LISIS:
                _terminar_lisis(e)
            continue
        if tipo in PATOGENOS:
            _ia(e, dt, px, pz)
            e["x"], e["z"] = resolver(e["x"], e["z"], e["radio"] * 0.6)
            if tipo in ("virus_a", "virus_b"):
                e["y"] = e["y0"] + math.sin(t * 5.0 + e["fase"]) * 0.3
            patogenos.append(e)
    _separar(patogenos)

    for e in entidades[:]:
        if e["estado"] != "vivo":
            continue
        toca = COLISION[e["tipo"]](e, px, py, pz, pr)
        e["colisionando"] = toca
        if not toca:
            continue
        if e["tipo"] in PATOGENOS:
            if e["retro"] <= 0.0:
                e["retro"] = 0.9
                eventos.append(("contacto", e))
        elif e["tipo"] != "vesicula":
            entidades.remove(e)
            eventos.append(("recoger", e))


# =====================================================================
# DIBUJO
# =====================================================================

def _restaurar_material():
    v.material(48.0, 0.35)


def _esf(pos, esc, col, alfa=1.0, det=14):
    glPushMatrix()
    glTranslatef(*pos)
    glScalef(*esc)
    glColor4f(col[0], col[1], col[2], alfa)
    glutSolidSphere(1.0, det, det)
    glPopMatrix()


# Inicia: color con efectos de golpe, aturdimiento y marca
def _tinte(e, col):
    if e["golpe"] > 0.0:
        return v.mezclar(col, (1.0, 1.0, 1.0), 0.7)
    if e["aturdido"] > 0.0:
        return v.mezclar(col, (0.8, 0.8, 0.35), 0.5)
    return col


# Inicia: dibujo del virus (espículas con puntas)
def _dibujar_virus(e, t, alfa, esc):
    r = e["radio"] * esc
    club = e["tipo"] == "virus_b"
    cuerpo = (0.80, 0.30, 0.22) if club else (0.30, 0.72, 0.30)
    punta = (1.0, 0.72, 0.30) if club else (0.95, 0.95, 0.25)
    cuerpo = _tinte(e, cuerpo)
    emision = (0.0, 0.0, 0.0)
    if club and e["dash"] <= 0.0 and e["cd"] < 0.7:
        emision = (0.6 * abs(math.sin(t * 24.0)), 0.05, 0.0)
    glPushMatrix()
    glTranslatef(e["x"], e["y"], e["z"])
    glRotatef((t * 28.0 + e["fase"] * 20.0) % 360.0, 0, 1, 0)
    glRotatef(15.0 * math.sin(t * 1.7 + e["fase"]), 1, 0, 0)
    v.material(70.0, 0.7, emision)
    glColor4f(cuerpo[0], cuerpo[1], cuerpo[2], alfa)
    glutSolidSphere(r * (1.0 + 0.05 * math.sin(t * 6.0 + e["fase"])), 14, 14)
    glColor4f(punta[0], punta[1], punta[2], alfa)
    for ang, ax, ay in ESPINAS:
        glPushMatrix()
        glRotatef(ang, ax, ay, 0.0)
        glTranslatef(0.0, 0.0, r * 0.85)
        glutSolidCone(r * 0.15, r * 0.55, 6, 1)
        if club:
            glTranslatef(0.0, 0.0, r * 0.55)
            glutSolidSphere(r * 0.17, 8, 8)
        glPopMatrix()
    glPopMatrix()
    _restaurar_material()


# Inicia: dibujo del bacilo (cápsula con flagelo ondulante)
def _dibujar_bacilo(e, t, alfa, esc):
    col = _tinte(e, (0.28, 0.72, 0.30))
    quad = _quadric()
    glPushMatrix()
    glTranslatef(e["x"], 0.9, e["z"])
    glRotatef(e["ang"], 0, 1, 0)
    glScalef(esc, esc, esc)

    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    glColor4f(0.4, 0.95, 0.4, alfa)
    glLineWidth(2.0)
    glBegin(GL_LINE_STRIP)
    for i in range(21):
        u = i / 20.0
        glVertex3f(-1.65 - u * 1.6, math.sin(t * 9.0 + u * 8.0) * 0.12 * u, math.sin(t * 9.0 + u * 8.0 + 1.5) * 0.3 * u)
    glEnd()
    glLineWidth(1.0)
    if con_luz:
        glEnable(GL_LIGHTING)

    v.material(60.0, 0.6)
    glColor4f(col[0], col[1], col[2], alfa)
    glRotatef(90, 0, 1, 0)
    glTranslatef(0.0, 0.0, -1.1)
    rad = 0.55 * (1.0 + 0.05 * math.sin(t * 8.0 + e["fase"]))
    gluCylinder(quad, rad, rad, 2.2, 16, 1)
    glutSolidSphere(rad, 14, 12)
    glTranslatef(0.0, 0.0, 2.2)
    glutSolidSphere(rad, 14, 12)
    glPopMatrix()
    _restaurar_material()


# Inicia: dibujo del coco y del jefe (racimo de esferas)
def _dibujar_coco(e, t, alfa, esc):
    r = e["radio"] * esc
    jefe = e["tipo"] == "jefe"
    col = _tinte(e, (0.78, 0.38, 0.12) if jefe else (0.95, 0.76, 0.18))
    glPushMatrix()
    glTranslatef(e["x"], e["y"], e["z"])
    glRotatef((t * 15.0 + e["fase"] * 10.0) % 360.0, 0, 1, 0)
    v.material(50.0, 0.5, (0.35, 0.05, 0.0) if jefe and e["hp"] < e["hp_max"] * 0.5 else (0.0, 0.0, 0.0))
    _esf((0, 0, 0), (r * 0.72,) * 3, col, alfa, 18)
    for i, (x, y, z) in enumerate(((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
        k = 0.62 + 0.04 * math.sin(t * 4.0 + i)
        _esf((x * r * k, y * r * k, z * r * k), (r * 0.5,) * 3, v.mezclar(col, (1, 1, 1), 0.12), alfa, 12)
    if jefe:
        glColor4f(0.95, 0.85, 0.3, alfa)
        for ang, ax, ay in ESPINAS:
            glPushMatrix()
            glRotatef(ang, ax, ay, 0.0)
            glTranslatef(0.0, 0.0, r * 1.0)
            glutSolidCone(r * 0.12, r * 0.4, 6, 1)
            glPopMatrix()
    glPopMatrix()
    _restaurar_material()


# Inicia: marcas visuales sobre los patógenos (anticuerpo y aturdimiento)
def _decorar(e, t):
    r = e["radio"]
    if e["marcado"] > 0.0:
        v.halo((e["x"], e["y"], e["z"]), r * 1.9, (1.0, 0.25, 0.85), 0.28, 3)
    if e["aturdido"] > 0.0:
        for i in range(3):
            a = t * 4.0 + i * 2.094
            _esf((e["x"] + math.cos(a) * r * 0.9, e["y"] + r + 0.5, e["z"] + math.sin(a) * r * 0.9),
                 (0.16, 0.16, 0.16), (1.0, 0.95, 0.3), 1.0, 8)


# Inicia: dibujo de un patógeno (con efecto de lisis)
def _dibujar_patogeno(e, t):
    alfa, esc = 1.0, 1.0
    if e["estado"] == "lisis":
        k = e["t_lisis"] / DURACION_LISIS
        alfa = max(0.0, 1.0 - k)
        esc = 1.0 + 0.7 * k + 0.12 * math.sin(k * 40.0)
    tipo = e["tipo"]
    if tipo in ("virus_a", "virus_b"):
        _dibujar_virus(e, t, alfa, esc)
    elif tipo == "bacilo":
        _dibujar_bacilo(e, t, alfa, esc)
    else:
        _dibujar_coco(e, t, alfa, esc)
    if e["estado"] == "vivo":
        _decorar(e, t)


# Inicia: dibujo del eritrocito (disco bicóncavo)
def _dibujar_eritrocito(e, t):
    glPushMatrix()
    glTranslatef(e["x"], e["y"] + math.sin(t * 2.0 + e["fase"]) * 0.18, e["z"])
    glRotatef((t * 45.0 + e["fase"] * 30.0) % 360.0, 0, 1, 0)
    glRotatef(55.0, 1, 0, 0)
    v.material(45.0, 0.55, (0.12, 0.0, 0.0))
    glColor3f(0.80, 0.06, 0.10)
    glutSolidTorus(0.3, 0.58, 12, 22)
    glScalef(1.0, 1.0, 0.42)
    glColor3f(0.62, 0.03, 0.08)
    glutSolidSphere(0.66, 16, 12)
    glPopMatrix()
    _restaurar_material()
    v.halo((e["x"], e["y"], e["z"]), 1.5, (1.0, 0.1, 0.12), 0.16, 3)


# Inicia: dibujo del ATP (adenosina y tres fosfatos)
def _dibujar_atp(e, t):
    glPushMatrix()
    glTranslatef(e["x"], e["y"] + math.sin(t * 3.0 + e["fase"]) * 0.2, e["z"])
    glRotatef((t * 60.0) % 360.0, 0, 1, 0)
    v.material(80.0, 0.8, (0.05, 0.25, 0.2))
    _esf((0, 0, 0), (0.42,) * 3, (0.15, 0.9, 0.85), 1.0, 14)
    _esf((0.2, 0.28, 0), (0.24,) * 3, (0.3, 1.0, 0.7), 1.0, 10)
    v.material(80.0, 0.8, (0.35, 0.28, 0.0))
    for i in range(3):
        x = -0.75 - i * 0.5
        _esf((x, -0.05 + 0.06 * i, 0), (0.22,) * 3, (1.0, 0.82, 0.12), 1.0, 10)
    glPopMatrix()
    _restaurar_material()
    v.halo((e["x"], e["y"], e["z"]), 1.7, (0.3, 1.0, 0.6), 0.22, 4)


# Inicia: dibujo del anticuerpo en forma de Y
def _dibujar_anticuerpo(e, t):
    quad = _quadric()
    glPushMatrix()
    glTranslatef(e["x"], e["y"] + 0.1 + math.sin(t * 2.5 + e["fase"]) * 0.2, e["z"])
    glRotatef((t * 55.0) % 360.0, 0, 1, 0)
    v.material(70.0, 0.7, (0.25, 0.05, 0.22))
    glColor3f(0.78, 0.35, 0.95)
    glutSolidSphere(0.4, 12, 12)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.38, 0.28, 1.2, 12, 1)
    glPopMatrix()
    glTranslatef(0.0, 1.2, 0.0)
    for ang in (-35, 35):
        glPushMatrix()
        glRotatef(ang, 0, 0, 1)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quad, 0.24, 0.24, 1.0, 10, 1)
        glTranslatef(0.0, 0.0, 1.0)
        glColor3f(1.0, 0.55, 0.9)
        glutSolidSphere(0.3, 10, 10)
        glColor3f(0.78, 0.35, 0.95)
        glPopMatrix()
    glPopMatrix()
    _restaurar_material()
    v.halo((e["x"], e["y"] + 1.0, e["z"]), 1.9, (0.9, 0.3, 1.0), 0.2, 3)


# Inicia: dibujo de la vesícula (bloque de membrana que estorba el paso)
def _dibujar_vesicula(e, t):
    bw, bh, bd = e["tam"]
    glPushMatrix()
    glTranslatef(e["x"], bh / 2.0, e["z"])
    glScalef(bw, bh, bd)
    v.material(60.0, 0.6)
    glColor4f(0.88, 0.62, 0.22, 0.92)
    glutSolidCube(1.0)
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    glColor3f(0.45, 0.28, 0.05)
    glutWireCube(1.01)
    if con_luz:
        glEnable(GL_LIGHTING)
    glPopMatrix()
    _restaurar_material()


# Inicia: hitbox de cada entidad
def _dibujar_hitbox(e):
    tipo = e["tipo"]
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    glPushMatrix()
    if tipo in ("virus_a", "virus_b", "coco", "jefe"):
        glTranslatef(e["x"], e["y"], e["z"])
        glColor3f(1.0, 1.0, 0.0)
        glutWireSphere(e["radio"] * 1.05, 10, 10)
    elif tipo == "bacilo":
        glTranslatef(e["x"], 0.9, e["z"])
        glRotatef(e["ang"], 0, 1, 0)
        glScalef(*e["tam"])
        glColor3f(1.0, 1.0, 1.0)
        glutWireCube(1.0)
    elif tipo == "eritrocito":
        glTranslatef(e["x"], e["y"] - DATOS[tipo]["alto"] / 2, e["z"])
        glRotatef(-90, 1, 0, 0)
        glColor3f(1.0, 0.5, 0.0)
        gluCylinder(_quadric_alambre(), e["radio"], e["radio"], DATOS[tipo]["alto"], 16, 1)
    elif tipo == "atp":
        glTranslatef(e["x"], e["y"], e["z"])
        glRotatef(45, 0, 1, 0)
        glColor3f(1.0, 0.0, 1.0)
        glutWireCube(DATOS[tipo]["umbral"] * 0.7)
    elif tipo == "anticuerpo":
        glTranslatef(e["x"], e["y"], e["z"])
        glColor3f(1.0, 0.0, 1.0)
        glutWireSphere(DATOS[tipo]["radio"], 10, 10)
        glTranslatef(0.0, DATOS[tipo]["alto"], 0.0)
        glutWireSphere(DATOS[tipo]["radio"], 10, 10)
    elif tipo == "vesicula":
        glTranslatef(e["x"], e["tam"][1] / 2.0, e["z"])
        glScalef(*e["tam"])
        glColor3f(1.0, 1.0, 1.0)
        glutWireCube(1.04)
    glPopMatrix()
    if con_luz:
        glEnable(GL_LIGHTING)


_quad_alambre = None


def _quadric_alambre():
    global _quad_alambre
    if _quad_alambre is None:
        _quad_alambre = gluNewQuadric()
        gluQuadricDrawStyle(_quad_alambre, GLU_LINE)
    return _quad_alambre


# Inicia: dibujar todas las entidades
def dibujar(t, mostrar_hitboxes):
    for e in entidades:
        tipo = e["tipo"]
        if tipo in PATOGENOS:
            _dibujar_patogeno(e, t)
        elif tipo == "eritrocito":
            _dibujar_eritrocito(e, t)
        elif tipo == "atp":
            _dibujar_atp(e, t)
        elif tipo == "anticuerpo":
            _dibujar_anticuerpo(e, t)
        else:
            _dibujar_vesicula(e, t)
        if mostrar_hitboxes and e["estado"] == "vivo":
            _dibujar_hitbox(e)
