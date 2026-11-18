import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound
from ACTIONS import combate
from ACTIONS import npcs
from RESOURCES import HandLes as h
from RESOURCES import visual as v
from SCENS import objetos_biologicos as bio
from SCENS import efectos as fx

NIVELES = [0, 1, 2]              # miocardio, vaso sanguíneo y ganglio linfático
RADIO_JUGADOR = 1.2
SALIDA = (11.0, -14.0)
RADIO_SALIDA = 2.6
SALUD_MAX = 100.0
ENERGIA_MAX = 100.0
ENERGIA_SALTO = 5.0
VEL_FACTOR = 1.28               # todos los personajes se mueven 28 % más rápido
INVULNERABLE = 0.9
INICIO = (0.0, 12.0)
INICIO_DOS = ((-1.8, 12.0), (1.8, 12.0))   # posiciones de salida en modo de dos jugadores
DISTANCIA_REANIMAR = 2.8        # el compañero debe quedarse así de cerca...
TIEMPO_REANIMAR = 2.5           # ...durante estos segundos para reanimar
SALUD_REANIMADO = 40.0
COLORES_JUGADOR = ((1.0, 0.8, 0.2), (0.3, 0.85, 1.0))   # J1 dorado, J2 cian

# Tabla de balance: velocidad (unidades/s), daño del ataque, defensa (multiplica el daño recibido),
# costo de energía por ataque, enfriamiento, recarga pasiva, si cura con eritrocitos y si tiene escudo
ESTADISTICAS = {
    "isaac": {"celula": "Macrófago", "vel": 8.0, "dano": 22, "defensa": 0.6, "costo": 6, "cooldown": 0.3,
              "regen": 3.0, "cura": True, "escudo": False, "prob_eri": 0.15},
    "azazel": {"celula": "Linfocito T citotóxico", "vel": 9.5, "dano": 70, "defensa": 1.0, "costo": 24,
               "cooldown": 0.9, "regen": 3.0, "cura": True, "escudo": False, "prob_eri": 0.15},
    "chispa": {"celula": "Célula dendrítica", "vel": 12.5, "dano": 8, "defensa": 1.35, "costo": 10,
               "cooldown": 0.6, "regen": 2.5, "cura": True, "escudo": False, "prob_eri": 0.15},
    "mapi": {"celula": "Linfocito B de memoria", "vel": 8.0, "dano": 28, "defensa": 1.3, "costo": 18,
             "cooldown": 0.4, "regen": 3.0, "cura": True, "escudo": False, "prob_eri": 0.15},
    "brote": {"celula": "Fibroblasto cardiaco", "vel": 8.0, "dano": 10, "defensa": 1.0, "costo": 10,
              "cooldown": 0.5, "regen": 3.5, "cura": True, "escudo": False, "prob_eri": 0.55},
    "perno": {"celula": "Nanobot de inmunoterapia", "vel": 6.0, "dano": 9999, "defensa": 1.0, "costo": 30,
              "cooldown": 0.9, "regen": 2.0, "cura": False, "escudo": True, "prob_eri": 0.15},
}

DATOS_CURIOSOS = [
    "Los ganglios linfáticos filtran la linfa y concentran linfocitos para responder rápido a las infecciones.",
    "Los eritrocitos no tienen núcleo: así dejan más espacio para la hemoglobina que transporta oxígeno.",
    "Los anticuerpos tienen forma de Y: las puntas reconocen al antígeno y el tallo avisa a otras células.",
    "Los linfocitos B de memoria recuerdan un antígeno por años; así funcionan las vacunas.",
    "El ATP es la moneda de energía de la célula: se gasta y se recarga todo el tiempo.",
    "Las células dendríticas muestran fragmentos del patógeno a los linfocitos T para iniciar la defensa.",
    "El corazón late unas 100,000 veces al día sin descansar.",
    "Un virus no es una célula: necesita infectar una para poder reproducirse.",
]

fase = "JUGANDO"          # JUGANDO, VICTORIA o DERROTA
nivel = 0
t_fase = 0.0
salida_activa = False
dato = ""
mensaje = ["", 0.0]
contadores = {"eliminados": 0, "atp": 0, "eritrocitos": 0}


# Inicia: ficha de un jugador (cada uno tiene sus teclas sostenidas y sus puntos)
def _nuevo_jugador(indice):
    return {"id": indice, "x": INICIO[0], "z": INICIO[1], "ang": 180.0, "salud": SALUD_MAX,
            "energia": ENERGIA_MAX, "inv": 0.0, "cd": 0.0, "ataque_t": 0.0, "marcado_t": 0.0, "dano_t": 0.0,
            "cura_t": 0.0, "aviso": "", "aviso_t": 0.0, "moviendo": False, "teclas": set(),
            "caido": False, "reanimar": 0.0, "puntos": 0}


jugadores = [_nuevo_jugador(0), _nuevo_jugador(1)]
jugador = jugadores[0]    # el J1; la cámara, la luz y el HUD de un jugador lo usan directamente

_polen_t = [0.0, 0.0]
transicion = {"t": 0.0, "titulo": ""}   # fundido y título al cambiar de nivel
_iniciada = False


# =====================================================================
# CONSULTAS
# =====================================================================

# Inicia: jugadores en la partida (uno o dos)
def activos():
    return jugadores[:2] if h.dos_jugadores else jugadores[:1]


# Inicia: jugadores que no están caídos
def en_pie():
    return [j for j in activos() if not j["caido"]]


# Inicia: personaje que controla cada jugador
def personaje_de(j):
    return h.personaje_actual if j["id"] == 0 else h.personaje_j2


# Inicia: estadísticas del personaje de un jugador (por omisión el J1)
def stats(j=None):
    return ESTADISTICAS[personaje_de(j or jugador)]


# Inicia: punto que sigue la cámara (centro de los jugadores)
def centro():
    grupo = activos()
    return (sum(j["x"] for j in grupo) / len(grupo), sum(j["z"] for j in grupo) / len(grupo))


# Inicia: mensaje central temporal
def avisar(texto, seg=2.5):
    mensaje[0] = texto
    mensaje[1] = seg


# Inicia: ¿el escenario actual es el nivel en juego?
def en_nivel():
    return h.estado_escenario == NIVELES[nivel]


# =====================================================================
# PARTIDA Y NIVELES
# =====================================================================

# Inicia: nueva partida desde el primer escenario (el modo 1 o 2 jugadores sale de HandLes)
def iniciar_partida(personaje=None):
    global fase, nivel, t_fase, salida_activa, _iniciada
    _iniciada = True
    fase = "JUGANDO"
    nivel = 0
    t_fase = 0.0
    salida_activa = False
    contadores.update(eliminados=0, atp=0, eritrocitos=0)
    combate.limpiar()
    for j in jugadores:
        _poner_jugador(j)
    _colocar_en_inicio()
    bio.iniciar_nivel(NIVELES[0])
    npcs.iniciar_nivel(NIVELES[0])
    avisar("Elimina a los patógenos y cruza la salida", 4.0)
    transicion.update(t=1.2, titulo="NIVEL 1 - MIOCARDIO")


def _poner_jugador(j):
    j.update(ang=180.0, salud=SALUD_MAX, energia=ENERGIA_MAX, inv=0.0, cd=0.0, ataque_t=0.0, marcado_t=0.0,
             dano_t=0.0, cura_t=0.0, aviso="", aviso_t=0.0, moviendo=False, caido=False, reanimar=0.0, puntos=0)
    j["teclas"].clear()


def _colocar_en_inicio():
    posiciones = INICIO_DOS if h.dos_jugadores else (INICIO,)
    for j, (x, z) in zip(activos(), posiciones):
        j["x"], j["z"] = x, z


# Inicia: reiniciar la partida con los mismos personajes (derrota o menú)
def reiniciar():
    iniciar_partida()
    h.estado_escenario = NIVELES[0]
    play_sound("reiniciar")


# Inicia: regresar al menú de selección
def volver_al_menu():
    global fase
    fase = "JUGANDO"
    soltar_teclas()
    npcs.cerrar()
    h.estado_escenario = "MENU"
    play_sound("click")


# Inicia: ENTER en las pantallas finales
def aceptar():
    if fase == "DERROTA":
        reiniciar()
    elif fase == "VICTORIA":
        volver_al_menu()


NOMBRES_NIVEL = {0: "MIOCARDIO", 1: "VASO SANGUÍNEO", 2: "GANGLIO LINFÁTICO"}


# Inicia: saltar a un nivel (al limpiar la sala o con la tecla de cambio de nivel)
def ir_a_nivel(indice):
    global nivel, salida_activa
    if not _iniciada:
        iniciar_partida()
    if fase != "JUGANDO" or not 0 <= indice < len(NIVELES):
        return
    nivel = indice
    salida_activa = False
    h.estado_escenario = NIVELES[nivel]
    bio.iniciar_nivel(NIVELES[nivel])
    npcs.iniciar_nivel(NIVELES[nivel])
    combate.limpiar()
    _colocar_en_inicio()
    for j in activos():
        if j["caido"]:
            reanimar(j, 50.0)
        j["inv"] = 1.2   # a salvo durante el fundido
    titulo = f"NIVEL {nivel + 1} - {NOMBRES_NIVEL[NIVELES[nivel]]}"
    avisar("Elimina a los patógenos y cruza la salida", 3.0)
    transicion.update(t=1.2, titulo=titulo)


# Inicia: pasar al siguiente escenario o ganar
def _avanzar():
    global fase, t_fase, dato
    if nivel + 1 < len(NIVELES):
        ir_a_nivel(nivel + 1)
        for j in activos():
            if personaje_de(j) == "perno":
                j["salud"] = SALUD_MAX
        play_sound("cambiarcolor")
    else:
        fase = "VICTORIA"
        t_fase = 0.0
        dato = random.choice(DATOS_CURIOSOS)
        play_sound("cambiarcolor")


def _derrota():
    global fase, t_fase, dato
    fase = "DERROTA"
    t_fase = 0.0
    dato = random.choice(DATOS_CURIOSOS)
    play_sound("salir")


# =====================================================================
# ENTRADA (HandLes traduce teclado y mandos a estas llamadas)
# =====================================================================

# Inicia: registrar dirección o disparo sostenido de un jugador
def tecla(direccion, presionada, indice=0):
    teclas = jugadores[indice]["teclas"]
    if presionada:
        teclas.add(direccion)
    else:
        teclas.discard(direccion)


def soltar_teclas():
    for j in jugadores:
        j["teclas"].clear()


def _puede_actuar(j):
    return (h.estado_escenario != "MENU" and fase == "JUGANDO" and en_nivel() and j in activos()
            and not j["caido"] and not npcs.abierto())


# Inicia: ataque del personaje de un jugador
def atacar(indice=0):
    j = jugadores[indice]
    if _puede_actuar(j):
        combate.atacar(j, stats(j), personaje_de(j))


# Inicia: hablar con el NPC cercano (el juego se pausa mientras dura el diálogo)
def interactuar(indice=0):
    j = jugadores[indice]
    if _puede_actuar(j) and npcs.interactuar(j):
        soltar_teclas()


# =====================================================================
# POSE Y SALTO
# =====================================================================

# Inicia: altura del salto (solo el J1 usa el salto de depuración con C)
def altura_salto(t, j=None):
    if (j is None or j["id"] == 0) and h.estado_movimiento == "saltar":
        return abs(math.sin(t * 8)) * 2.0
    return 0.0


# Inicia: expresión y movimiento que se muestran según lo que le ocurre a un jugador
def pose(j=None):
    j = j or jugador
    if j["id"] == 0:
        exp, mov = h.estado_expresion, h.estado_movimiento
    else:
        exp, mov = "normal", "reposo"
    if fase == "VICTORIA":
        return "feliz", "saludar"
    if fase == "DERROTA" or j["caido"]:
        return "triste", "agacharse"
    if not h.reacciones_activas or not en_nivel():
        return exp, mov
    if j["dano_t"] > 0.0:
        exp = "miedo"
    elif j["cura_t"] > 0.0:
        exp = "feliz"
    elif j["ataque_t"] > 0.0:
        exp = "enojado"
    elif j["salud"] < 30.0:
        exp = "triste"
    if mov in ("reposo", "caminar"):
        if j["ataque_t"] > 0.0:
            mov = "elevar_brazos"
        elif j["moviendo"]:
            mov = "caminar"
    return exp, mov


# =====================================================================
# LÓGICA POR JUGADOR
# =====================================================================

# Inicia: mover a un jugador con la velocidad de su personaje
def _mover(dt, j, st):
    teclas = j["teclas"]
    dx = (1.0 if "der" in teclas else 0.0) - (1.0 if "izq" in teclas else 0.0)
    dz = (1.0 if "aba" in teclas else 0.0) - (1.0 if "arr" in teclas else 0.0)
    j["moviendo"] = bool(dx or dz) and not j["caido"]
    if j["moviendo"]:
        n = math.hypot(dx, dz)
        dx, dz = dx / n, dz / n
        j["x"] += dx * st["vel"] * VEL_FACTOR * dt
        j["z"] += dz * st["vel"] * VEL_FACTOR * dt
        objetivo = math.degrees(math.atan2(dx, dz))
        diff = (objetivo - j["ang"] + 180.0) % 360.0 - 180.0
        j["ang"] += diff * min(1.0, 14.0 * dt)
    j["x"], j["z"] = bio.resolver(j["x"], j["z"], RADIO_JUGADOR)


# Inicia: los dos jugadores no se enciman
def _separar_jugadores():
    grupo = activos()
    if len(grupo) < 2:
        return
    a, b = grupo
    dx, dz = b["x"] - a["x"], b["z"] - a["z"]
    d = math.hypot(dx, dz)
    minimo = RADIO_JUGADOR * 1.6
    if 1e-6 < d < minimo:
        empuje = (minimo - d) * 0.5
        a["x"], a["z"] = bio.resolver(a["x"] - dx / d * empuje, a["z"] - dz / d * empuje, RADIO_JUGADOR)
        b["x"], b["z"] = bio.resolver(b["x"] + dx / d * empuje, b["z"] + dz / d * empuje, RADIO_JUGADOR)


# Inicia: aplicar un golpe recibido (el escudo frontal del Perno lo bloquea)
def _recibir_dano(e, j):
    st = stats(j)
    if j["inv"] > 0.0 or j["caido"]:
        return
    dx, dz = e["x"] - j["x"], e["z"] - j["z"]
    d = max(0.01, math.hypot(dx, dz))
    a = math.radians(j["ang"])
    if st["escudo"] and (dx * math.sin(a) + dz * math.cos(a)) / d > 0.3:
        j["inv"] = 0.35
        fx.explosion((j["x"] + dx / d * 1.8, 2.2, j["z"] + dz / d * 1.8), (0.4, 1.0, 1.0), 14, 6.0, 0.4, 7.0, 0.0)
        play_sound("click")
        j["aviso"], j["aviso_t"] = "Escudo: golpe bloqueado", 0.8
        return
    j["salud"] -= bio.DATOS[e["tipo"]]["dano"] * st["defensa"]
    j["inv"] = INVULNERABLE
    j["dano_t"] = 0.5
    fx.explosion((j["x"], 2.0, j["z"]), (1.0, 0.2, 0.2), 16, 5.0, 0.5, 7.0)
    play_sound("abajo")
    if j["salud"] <= 0.0:
        _caer(j)


# Inicia: un jugador sin salud; con un jugador es derrota, con dos queda caído
def _caer(j):
    j["salud"] = 0.0
    j["teclas"].clear()
    if not h.dos_jugadores:
        _derrota()
        return
    j["caido"] = True
    j["reanimar"] = 0.0
    fx.anillo(j["x"], j["z"], 0.5, 3.0, 0.7, (1.0, 0.3, 0.3))
    if not en_pie():
        _derrota()
    else:
        avisar(f"¡J{j['id'] + 1} cayó! Acércate para reanimarlo", 3.0)


# Inicia: levantar a un jugador caído
def reanimar(j, salud=SALUD_REANIMADO):
    j["caido"] = False
    j["reanimar"] = 0.0
    j["salud"] = salud
    j["inv"] = 2.0
    j["cura_t"] = 0.8
    fx.explosion((j["x"], 1.5, j["z"]), (0.5, 1.0, 0.6), 30, 6.0, 0.8, 8.0, 0.0)
    fx.anillo(j["x"], j["z"], 0.5, 3.0, 0.6, (0.5, 1.0, 0.6))
    play_sound("cambiarcolor")


# Inicia: el compañero en pie reanima al caído quedándose cerca
def _actualizar_reanimacion(dt):
    for j in activos():
        if not j["caido"]:
            continue
        cerca = any(math.hypot(o["x"] - j["x"], o["z"] - j["z"]) < DISTANCIA_REANIMAR for o in en_pie())
        if cerca:
            j["reanimar"] += dt
            if j["reanimar"] >= TIEMPO_REANIMAR:
                reanimar(j)
        else:
            j["reanimar"] = max(0.0, j["reanimar"] - dt * 0.5)


# Inicia: recoger eritrocito, ATP o anticuerpo
def _recoger(e, j):
    st = stats(j)
    tipo = e["tipo"]
    if tipo == "eritrocito":
        contadores["eritrocitos"] += 1
        if st["cura"]:
            j["salud"] = min(SALUD_MAX, j["salud"] + 25.0)
            j["cura_t"] = 0.8
            avisar("Eritrocito: +25 salud", 1.2)
        else:
            avisar("Perno no recupera salud", 1.5)
        fx.explosion((e["x"], 1.5, e["z"]), (1.0, 0.3, 0.3), 14, 4.0, 0.6, 7.0, 0.0)
    elif tipo == "atp":
        contadores["atp"] += 1
        j["energia"] = min(ENERGIA_MAX, j["energia"] + 35.0)
        avisar("ATP: +35 energía", 1.2)
        fx.explosion((e["x"], 1.5, e["z"]), (0.4, 1.0, 0.7), 14, 4.0, 0.6, 7.0, 0.0)
    elif tipo == "anticuerpo":
        bio.marcar_todos(8.0)
        j["marcado_t"] = 8.0
        avisar("Anticuerpo: patógenos marcados (daño x1.8)", 2.0)
        fx.explosion((e["x"], 1.5, e["z"]), (1.0, 0.4, 0.9), 18, 5.0, 0.7, 7.0, 0.0)
    play_sound("click")


# Inicia: procesar eventos de las entidades (cada uno dice qué jugador lo causó)
def _procesar_eventos():
    for tipo, e, indice in bio.tomar_eventos():
        if tipo == "contacto":
            _recibir_dano(e, jugadores[indice])
        elif tipo == "recoger":
            _recoger(e, jugadores[indice])
        elif tipo == "eliminado":
            contadores["eliminados"] += 1
            if indice is not None:
                jugadores[indice]["puntos"] += 1
            npcs.registrar_eliminado(e["tipo"])
            play_sound("reiniciar")


# =====================================================================
# CUADRO
# =====================================================================

# Inicia: actualizar todo el juego un cuadro
def actualizar(dt, t):
    global t_fase, salida_activa
    dt = min(dt, 0.05)
    fx.actualizar(dt)
    if h.estado_escenario == "MENU":
        return
    if not _iniciada:   # por si se salta el menú con el clic derecho
        iniciar_partida()
    transicion["t"] = max(0.0, transicion["t"] - dt)
    mensaje[1] = max(0.0, mensaje[1] - dt)

    # Con un diálogo abierto el mundo se detiene
    if npcs.abierto():
        return
    for j in activos():
        for clave in ("inv", "cd", "ataque_t", "marcado_t", "dano_t", "cura_t", "aviso_t"):
            j[clave] = max(0.0, j[clave] - dt)

    if fase != "JUGANDO":
        t_fase += dt
        return
    for j in activos():
        _mover(dt, j, stats(j))
    _separar_jugadores()
    if not en_nivel():
        return

    for j in en_pie():
        st = stats(j)
        # Energía: el salto la consume, si no se recupera sola
        if j["id"] == 0 and h.estado_movimiento == "saltar":
            j["energia"] -= ENERGIA_SALTO * dt
            if j["energia"] <= 0.0:
                j["energia"] = 0.0
                h.estado_movimiento = "reposo"
        else:
            j["energia"] = min(ENERGIA_MAX, j["energia"] + st["regen"] * dt)

        # Polen reparador de Brote
        if personaje_de(j) == "brote":
            _polen_t[j["id"]] -= dt
            if _polen_t[j["id"]] <= 0.0:
                _polen_t[j["id"]] = 0.12
                fx.flotar((j["x"], 1.2, j["z"]), (1.0, 0.9, 0.3), 1, 1.6, 5.0)

        # Disparo sostenido: mientras se mantiene la tecla se repite el ataque (el enfriamiento lo limita)
        if "fuego" in j["teclas"]:
            combate.atacar(j, st, personaje_de(j))

    bio.config["prob_eri"] = max(stats(j)["prob_eri"] for j in activos())
    cuerpos = [(j["id"], j["x"], j["z"], bio.ALTURA_CENTRO + altura_salto(t, j), RADIO_JUGADOR) for j in en_pie()]
    bio.actualizar(dt, t, cuerpos)
    _procesar_eventos()
    combate.actualizar(dt)
    _actualizar_reanimacion(dt)
    if fase != "JUGANDO":
        return

    if not bio.hay_patogenos():
        if not salida_activa:
            salida_activa = True
            avisar("Sala limpia: cruza la salida luminosa", 3.5)
            play_sound("cambiarcolor")
        elif any(math.hypot(j["x"] - SALIDA[0], j["z"] - SALIDA[1]) < RADIO_SALIDA for j in en_pie()):
            _avanzar()


# =====================================================================
# DIBUJO
# =====================================================================

# Inicia: dibujo de la salida del escenario
def dibujar_salida(t):
    x, z = SALIDA
    activa = salida_activa
    col = (0.25, 1.0, 0.75) if activa else (0.55, 0.12, 0.12)
    glPushMatrix()
    glTranslatef(x, 0.0, z)
    v.iniciar_aditivo()
    for i in range(3):
        glPushMatrix()
        glTranslatef(0.0, 0.15 + i * 0.12, 0.0)
        glRotatef(-90, 1, 0, 0)
        glColor4f(col[0], col[1], col[2], (0.55 if activa else 0.25) - i * 0.1)
        glRotatef(t * (40 + i * 25) if activa else 0.0, 0, 0, 1)
        glutSolidTorus(0.08, RADIO_SALIDA * (1.0 - i * 0.2) * (1.0 + (0.04 * math.sin(t * 5.0) if activa else 0.0)), 8, 36)
        glPopMatrix()
    if activa:
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor4f(col[0], col[1], col[2], 0.24)
        gluCylinder(gluNewQuadric_cache(), RADIO_SALIDA * 0.9, RADIO_SALIDA * 0.45, 16.0, 24, 1)
        glPopMatrix()
    v.terminar_transparencia()
    glPopMatrix()
    if activa and fase == "JUGANDO":
        for j in en_pie():
            _flecha_guia(j, t, col)
    if activa and random.random() < 0.5:
        fx.flotar((x, 0.5, z), col, 1, 1.4, 5.0)


# Inicia: flecha en el piso que señala hacia la salida
def _flecha_guia(j, t, col):
    dx, dz = SALIDA[0] - j["x"], SALIDA[1] - j["z"]
    d = math.hypot(dx, dz)
    if d < RADIO_SALIDA * 2.5:
        return
    ux, uz = dx / d, dz / d
    avance = 3.2 + 0.4 * math.sin(t * 6.0)
    cx, cz = j["x"] + ux * avance, j["z"] + uz * avance
    px, pz = -uz, ux
    v.iniciar_aditivo()
    glColor4f(col[0], col[1], col[2], 0.6)
    glBegin(GL_TRIANGLES)
    glVertex3f(cx + ux * 0.9, 0.2, cz + uz * 0.9)
    glVertex3f(cx - ux * 0.5 + px * 0.7, 0.2, cz - uz * 0.5 + pz * 0.7)
    glVertex3f(cx - ux * 0.5 - px * 0.7, 0.2, cz - uz * 0.5 - pz * 0.7)
    glEnd()
    v.terminar_transparencia()


# Inicia: aro de color bajo cada jugador (modo de dos jugadores) y progreso de reanimación
def dibujar_marcas(t):
    if not h.dos_jugadores:
        return
    for j in activos():
        col = (1.0, 0.25, 0.25) if j["caido"] else COLORES_JUGADOR[j["id"]]
        v.iniciar_aditivo()
        glPushMatrix()
        glTranslatef(j["x"], 0.1, j["z"])
        glRotatef(-90, 1, 0, 0)
        glColor4f(col[0], col[1], col[2], 0.55 + (0.25 * math.sin(t * 8.0) if j["caido"] else 0.0))
        glutSolidTorus(0.07, 1.5, 6, 32)
        if j["caido"] and j["reanimar"] > 0.0:
            glColor4f(0.5, 1.0, 0.6, 0.8)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0.0, 0.0, 0.02)
            pasos = 32
            fin = int(pasos * min(1.0, j["reanimar"] / TIEMPO_REANIMAR))
            for i in range(fin + 1):
                a = i / pasos * 2.0 * math.pi
                glVertex3f(math.sin(a) * 1.4, math.cos(a) * 1.4, 0.02)
            glEnd()
        glPopMatrix()
        v.terminar_transparencia()


_q = None


def gluNewQuadric_cache():
    global _q
    if _q is None:
        _q = gluNewQuadric()
    return _q
