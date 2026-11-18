import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound
from ACTIONS.npcs_datos import NPCS_POR_NIVEL
from RESOURCES import visual as v
from SCENS import objetos_biologicos as bio
from SCENS import efectos as fx

# Sistema de NPC: los datos de cada nivel están en npcs_datos.py; aquí viven el estado,
# la proximidad, el motor de diálogos, las acciones y el dibujo.

RADIO_INTERACCION = 3.4     # distancia (centro a centro) para poder hablar
ESCALA = 1.3                # tamaño de los NPC respecto a sus datos
ALTURA_ETIQUETA = 5.6       # altura del nombre sobre el NPC

actuales = []               # NPC del nivel en juego
estado = {}                 # por id: misión, progreso y opciones usadas
dialogo = None              # conversación abierta (una a la vez; el juego se pausa)
etiquetas = []              # (npc, x, y) en pantalla para el HUD, calculadas al dibujar


def _juego():
    from ACTIONS import juego   # import tardío: juego.py importa este módulo
    return juego


# =====================================================================
# NIVEL Y PROXIMIDAD
# =====================================================================

# Inicia: colocar a los NPC del escenario (llamar después de bio.iniciar_nivel)
def iniciar_nivel(escenario):
    global dialogo
    dialogo = None
    actuales.clear()
    estado.clear()
    for datos in NPCS_POR_NIVEL.get(escenario, []):
        x, z = datos["pos"]
        n = {"datos": datos, "x": x, "z": z, "ang": 0.0, "fase": (x + z) * 0.37}
        actuales.append(n)
        estado[datos["id"]] = {"mision": "sin_empezar", "progreso": 0, "usadas": set()}
        rx, _, rz = datos["apariencia"]["cuerpo"]
        # Los NPC son obstáculos sólidos para jugadores y patógenos
        bio.circulos.append((x, z, max(rx, rz) * ESCALA + 0.15))


# Inicia: NPC más cercano a un jugador dentro del radio de interacción
def cercano(j):
    mejor, md = None, RADIO_INTERACCION + ESCALA - 1.0
    for n in actuales:
        d = math.hypot(n["x"] - j["x"], n["z"] - j["z"])
        if d < md:
            mejor, md = n, d
    return mejor


def abierto():
    return dialogo is not None


# =====================================================================
# CONDICIONES Y ACCIONES (los nombres se usan en npcs_datos.py)
# =====================================================================

def _cond_mision(valor):
    return lambda n, j: estado[n["datos"]["id"]]["mision"] == valor


def _hay_caido(n, j):
    juego = _juego()
    return any(o["caido"] for o in juego.activos() if o is not j)


def _hay_vesiculas(n, j):
    return any(e["tipo"] == "vesicula" for e in bio.entidades)


CONDICIONES = {
    "mision_sin_empezar": _cond_mision("sin_empezar"),
    "mision_activa": _cond_mision("activa"),
    "mision_lista": _cond_mision("lista"),
    "mision_entregada": _cond_mision("entregada"),
    "hay_caido": _hay_caido,
    "hay_vesiculas": _hay_vesiculas,
    "hay_patogenos": lambda n, j: bio.hay_patogenos(),
}


def _cumple(condicion, n, j):
    if not condicion:
        return True
    if condicion.startswith("!"):
        return not CONDICIONES[condicion[1:]](n, j)
    return CONDICIONES[condicion](n, j)


# Cada acción recibe (npc, jugador) y devuelve (éxito, texto que responde el NPC)
def _dar_energia(n, j):
    juego = _juego()
    j["energia"] = juego.ENERGIA_MAX
    fx.explosion((j["x"], 1.5, j["z"]), (0.4, 1.0, 0.7), 18, 4.0, 0.6, 7.0, 0.0)
    return True, "Toma, comparte mi ATP: tu energía está al máximo. ¡Late fuerte!"


def _curar(j, cantidad):
    juego = _juego()
    if not juego.stats(j)["cura"]:
        return False, "Lo siento, Perno: un nanobot no se repara con células."
    if j["salud"] >= juego.SALUD_MAX:
        return False, "Ya estás completamente sano."
    j["salud"] = min(juego.SALUD_MAX, j["salud"] + cantidad)
    j["cura_t"] = 0.8
    fx.explosion((j["x"], 1.5, j["z"]), (1.0, 0.35, 0.4), 18, 4.0, 0.6, 7.0, 0.0)
    return True, None


def _curar_completo(n, j):
    ok, texto = _curar(j, _juego().SALUD_MAX)
    return ok, texto or "Mis citocinas te devuelven toda la salud."


def _comerciar_salud(n, j):
    if j["energia"] < 30.0:
        return False, "Necesitas al menos 30 de energía. Recoge ATP y vuelve."
    ok, texto = _curar(j, 35.0)
    if ok:
        j["energia"] -= 30.0
    return ok, texto or "Listo: -30 de energía, +35 de salud."


def _aceptar_mision(n, j):
    st = estado[n["datos"]["id"]]
    m = n["datos"]["mision"]
    # El avance cuenta desde que empieza el nivel: si ya se cumplió, queda lista para cobrar
    if st["progreso"] >= m["meta"]:
        st["mision"] = "lista"
        return True, f"¡Ya lo habías hecho! Llevas {st['progreso']}. Habla conmigo de nuevo por tu premio."
    st["mision"] = "activa"
    _juego().avisar("Misión: " + m["descripcion"], 2.5)
    return True, None


def _entregar_mision(n, j):
    st = estado[n["datos"]["id"]]
    st["mision"] = "entregada"
    ok, texto = ACCIONES[n["datos"]["mision"]["premio"]](n, j)
    play_sound("cambiarcolor")
    return True, texto


def _premio_reservas(n, j):
    juego = _juego()
    for o in juego.activos():
        o["energia"] = juego.ENERGIA_MAX
        if juego.stats(o)["cura"] and not o["caido"]:
            o["salud"] = min(juego.SALUD_MAX, o["salud"] + 30.0)
    return True, "Energía al máximo y +30 de salud para el equipo."


def _devorar_vesiculas(n, j):
    vesiculas = [e for e in bio.entidades if e["tipo"] == "vesicula"]
    for e in vesiculas:
        fx.explosion((e["x"], 1.2, e["z"]), (0.95, 0.8, 0.45), 26, 6.0, 0.8, 8.0)
        bio.entidades.remove(e)
    return True, f"¡Ñam! Devoré {len(vesiculas)} vesículas. El camino está despejado."


def _fabricar_anticuerpos(n, j):
    if j["energia"] < 40.0:
        return False, "Necesito 40 de tu energía para fabricarlos."
    j["energia"] -= 40.0
    bio.marcar_todos(10.0)
    j["marcado_t"] = 10.0
    return True, "¡Anticuerpos liberados! Los patógenos quedan marcados 10 segundos (daño x1.8)."


def _debilitar_jefe(n, j):
    jefe = bio.jefe_vivo()
    if jefe is None:
        return _premio_reservas(n, j)
    jefe["hp"] = max(1.0, jefe["hp"] - jefe["hp_max"] * 0.35)
    jefe["marcado"] = max(jefe["marcado"], 12.0)
    fx.explosion((jefe["x"], jefe["y"], jefe["z"]), (0.6, 0.85, 1.0), 40, 8.0, 0.9, 9.0)
    return True, "La biopelícula perdió 35 % de su salud y quedó marcada 12 segundos."


def _reanimar_companero(n, j):
    juego = _juego()
    for o in juego.activos():
        if o is not j and o["caido"]:
            juego.reanimar(o)
            return True, "¡Señal enviada! Tu compañero vuelve a la pelea."
    return False, "Tu compañero está bien."


ACCIONES = {
    "dar_energia": _dar_energia,
    "curar_completo": _curar_completo,
    "comerciar_salud": _comerciar_salud,
    "aceptar_mision": _aceptar_mision,
    "entregar_mision": _entregar_mision,
    "premio_reservas": _premio_reservas,
    "devorar_vesiculas": _devorar_vesiculas,
    "fabricar_anticuerpos": _fabricar_anticuerpos,
    "debilitar_jefe": _debilitar_jefe,
    "reanimar_companero": _reanimar_companero,
}


# =====================================================================
# MISIONES
# =====================================================================

# Inicia: contar un patógeno eliminado para las misiones del nivel
# (cuenta desde el inicio del nivel, para que eliminar antes de hablar no deje la misión imposible)
def registrar_eliminado(tipo):
    for n in actuales:
        m = n["datos"].get("mision")
        st = estado[n["datos"]["id"]]
        if m is None or st["mision"] not in ("sin_empezar", "activa") or tipo not in m["tipos"]:
            continue
        st["progreso"] += 1
        if st["mision"] == "activa" and st["progreso"] >= m["meta"]:
            st["mision"] = "lista"
            _juego().avisar(f"Misión cumplida: vuelve con {n['datos']['nombre']}", 3.0)


# Inicia: textos de las misiones en curso para el HUD
def misiones_en_curso():
    salida = []
    for n in actuales:
        m = n["datos"].get("mision")
        st = estado[n["datos"]["id"]]
        if m is None:
            continue
        if st["mision"] == "activa":
            salida.append(f"Misión ({n['datos']['nombre']}): {m['descripcion']} {st['progreso']}/{m['meta']}")
        elif st["mision"] == "lista":
            salida.append(f"Misión ({n['datos']['nombre']}): ¡cumplida! Ve por tu premio")
    return salida


# =====================================================================
# MOTOR DE DIÁLOGOS
# =====================================================================

# Inicia: abrir la conversación con el NPC más cercano al jugador
def interactuar(j):
    global dialogo
    n = cercano(j)
    if n is None:
        return False
    inicio = "inicio"
    for condicion, nodo in n["datos"]["entrada"]:
        if _cumple(condicion, n, j):
            inicio = nodo
            break
    dialogo = {"npc": n, "jugador": j, "nodo": inicio, "temp": None, "sel": 0}
    play_sound("click")
    return True


def cerrar():
    global dialogo
    if dialogo is not None:
        play_sound("click")
    dialogo = None


# Inicia: nodo actual (una respuesta temporal tiene prioridad)
def nodo_actual():
    if dialogo is None:
        return None
    if dialogo["temp"] is not None:
        return dialogo["temp"]
    return dialogo["npc"]["datos"]["dialogo"][dialogo["nodo"]]


# Inicia: texto del nodo con el avance de la misión
def texto_actual():
    n = dialogo["npc"]
    st = estado[n["datos"]["id"]]
    m = n["datos"].get("mision") or {}
    return nodo_actual()["texto"].format(progreso=st["progreso"], meta=m.get("meta", 0))


# Inicia: opciones que el jugador puede elegir ahora
def opciones():
    n, j = dialogo["npc"], dialogo["jugador"]
    usadas = estado[n["datos"]["id"]]["usadas"]
    nodo = nodo_actual()
    visibles = []
    for i, o in enumerate(nodo["opciones"]):
        clave = (dialogo["nodo"], i)
        if dialogo["temp"] is None and o.get("una_vez") and clave in usadas:
            continue
        if _cumple(o.get("si"), n, j):
            visibles.append((clave, o))
    return visibles


def mover(delta):
    if dialogo is None:
        return
    total = len(opciones())
    if total:
        dialogo["sel"] = (dialogo["sel"] + delta) % total
        play_sound("click")


def elegir(indice):
    if dialogo is not None and 0 <= indice < len(opciones()):
        dialogo["sel"] = indice
        confirmar()


# Inicia: ejecutar la opción seleccionada
def confirmar():
    global dialogo
    if dialogo is None:
        return
    visibles = opciones()
    if not visibles:
        cerrar()
        return
    clave, o = visibles[min(dialogo["sel"], len(visibles) - 1)]
    n, j = dialogo["npc"], dialogo["jugador"]
    exito, respuesta = True, None
    if o.get("accion"):
        exito, respuesta = ACCIONES[o["accion"]](n, j)
        if exito and o.get("una_vez"):
            estado[n["datos"]["id"]]["usadas"].add(clave)
        play_sound("cambiarcolor" if exito else "abajo")
    siguiente = o.get("ir") if exito else dialogo["nodo"]
    if respuesta:
        # La respuesta se muestra en un nodo temporal; "Continuar" sigue al destino
        dialogo["temp"] = {"texto": respuesta, "opciones": [{"texto": "Continuar", "ir": siguiente}]}
        dialogo["sel"] = 0
        return
    dialogo["temp"] = None
    if siguiente is None:
        cerrar()
    else:
        dialogo["nodo"] = siguiente
        dialogo["sel"] = 0


# =====================================================================
# DIBUJO
# =====================================================================

def _sombra_y_material():
    v.material(40.0, 0.4)


def _cara(rx, ry, rz, cy):
    # ojos, brillo, rubor y sonrisa sobre el frente del cuerpo (+z)
    zf = rz * 0.93
    for lado in (-1, 1):
        v.esfera((lado * rx * 0.3, cy + ry * 0.18, zf), (0.13, 0.19, 0.08), (0.08, 0.06, 0.12), 12)
        v.esfera((lado * rx * 0.55, cy - ry * 0.1, zf * 0.93), (0.14, 0.08, 0.05), (1.0, 0.55, 0.6), 10)
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    for lado in (-1, 1):
        v.esfera((lado * rx * 0.3 + 0.04, cy + ry * 0.26, zf + 0.06), (0.04, 0.05, 0.03), (1.0, 1.0, 1.0), 6)
    if con_luz:
        glEnable(GL_LIGHTING)
    for i in range(7):
        u = -1.0 + i / 3.0
        v.esfera((u * rx * 0.18, cy - ry * 0.12 + 0.07 * u * u, zf - 0.02 * u * u), (0.035, 0.035, 0.035),
                 (0.25, 0.08, 0.1), 6)


def _detalle(tipo, rx, ry, rz, cy, color, t):
    oscuro = v.mezclar(color, (0.0, 0.0, 0.0), 0.35)
    if tipo == "estrias":
        for i in range(5):
            glPushMatrix()
            glTranslatef(-rx * 0.6 + i * rx * 0.3, cy, 0.0)
            glRotatef(90, 0, 1, 0)
            glScalef(rz / ry, 1.0, 1.0)
            glColor3fv(oscuro)
            glutSolidTorus(0.035, ry * 0.92, 6, 24)
            glPopMatrix()
    elif tipo == "puntas":
        for i in range(8):
            a = math.radians(i * 45 + t * 20.0)
            v.esfera((math.cos(a) * rx * 1.02, cy, math.sin(a) * rz * 1.02), (0.16, 0.1, 0.16), oscuro, 8)
    elif tipo == "seudopodos":
        for i in range(5):
            a = math.radians(i * 72 + 30)
            ext = 1.0 + 0.12 * math.sin(t * 2.0 + i)
            v.esfera((math.cos(a) * rx * 0.95 * ext, cy - ry * 0.35, math.sin(a) * rz * 0.95 * ext),
                     (0.38, 0.28, 0.38), color, 10)
    elif tipo == "anticuerpos":
        for i in range(4):
            a = t * 1.2 + i * 1.5708
            glPushMatrix()
            glTranslatef(math.cos(a) * (rx + 0.7), cy + 0.5 + math.sin(t * 2 + i) * 0.2, math.sin(a) * (rz + 0.7))
            glRotatef(math.degrees(-a) % 360.0, 0, 1, 0)
            v.caja((0, -0.12, 0), (0.05, 0.24, 0.05), (1.0, 0.95, 0.6))
            v.caja((-0.08, 0.06, 0), (0.05, 0.2, 0.05), (1.0, 0.95, 0.6), (0, 0, 1, 35))
            v.caja((0.08, 0.06, 0), (0.05, 0.2, 0.05), (1.0, 0.95, 0.6), (0, 0, 1, -35))
            glPopMatrix()


def _marcador(n, alto, t):
    st = estado[n["datos"]["id"]]
    if n["datos"].get("mision") is None or st["mision"] not in ("sin_empezar", "lista"):
        return
    color = (1.0, 0.85, 0.15) if st["mision"] == "sin_empezar" else (0.3, 1.0, 0.45)
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(0.0, alto + 0.15 * math.sin(t * 3.0), 0.0)
    glRotatef((t * 90.0) % 360.0, 0, 1, 0)
    v.caja((0, 0.32, 0), (0.16, 0.5, 0.16), color)
    v.esfera((0, -0.08, 0), (0.1, 0.1, 0.1), color, 8)
    glPopMatrix()
    if con_luz:
        glEnable(GL_LIGHTING)
    v.halo((0.0, alto + 0.2, 0.0), 0.55, color, 0.25, 3, 10)


def _dibujar_npc(n, t, objetivo):
    a = n["datos"]["apariencia"]
    rx, ry, rz = a["cuerpo"]
    color = a["color"]
    cy = 1.0 + ry + 0.12 * math.sin(t * 2.0 + n["fase"])

    # Gira con suavidad hacia el jugador más cercano
    if objetivo is not None:
        meta = math.degrees(math.atan2(objetivo["x"] - n["x"], objetivo["z"] - n["z"]))
    else:
        meta = math.sin(t * 0.5 + n["fase"]) * 30.0
    n["ang"] += ((meta - n["ang"] + 180.0) % 360.0 - 180.0) * 0.08

    glPushMatrix()
    glTranslatef(n["x"], 0.0, n["z"])
    glRotatef(n["ang"], 0, 1, 0)
    glScalef(ESCALA, ESCALA, ESCALA)
    _sombra_y_material()

    # Núcleo opaco y membrana translúcida encima
    for dx, dy, dz, r in a["nucleo"]:
        v.esfera((dx, cy + dy, dz), (r, r, r), a["color_nucleo"], 14)
    _detalle(a["detalle"], rx, ry, rz, cy, color, t)
    glPushAttrib(GL_ENABLE_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_CURRENT_BIT)  # type: ignore
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)
    glPushMatrix()
    glTranslatef(0.0, cy, 0.0)
    glScalef(rx, ry, rz)
    glColor4f(color[0], color[1], color[2], 0.55)
    glutSolidSphere(1.0, 24, 18)
    glPopMatrix()
    glPopAttrib()

    _cara(rx, ry, rz, cy)
    _marcador(n, cy + ry + 0.9, t)
    glPopMatrix()
    v.material()


# Inicia: dibujar a los NPC y calcular dónde van sus nombres en pantalla
def dibujar(t, jugadores):
    for n in actuales:
        objetivo, md = None, 9.0
        for j in jugadores:
            d = math.hypot(j["x"] - n["x"], j["z"] - n["z"])
            if d < md:
                objetivo, md = j, d
        _dibujar_npc(n, t, objetivo)

    etiquetas.clear()
    if not actuales:
        return
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    proyeccion = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)
    for n in actuales:
        sx, sy, sz = gluProject(n["x"], ALTURA_ETIQUETA, n["z"], modelview, proyeccion, viewport)
        if 0.0 < sz < 1.0:
            etiquetas.append((n, sx, viewport[3] - sy))


# Inicia: sombras de los NPC (x, z, radio, altura)
def sombras():
    return [(n["x"], n["z"], max(n["datos"]["apariencia"]["cuerpo"][0], 1.0) * ESCALA, 1.0) for n in actuales]
