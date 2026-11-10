import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound
from ACTIONS import combate
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
teclas = set()            # direcciones sostenidas: izq, der, arr, aba

jugador = {"x": INICIO[0], "z": INICIO[1], "ang": 180.0, "salud": SALUD_MAX, "energia": ENERGIA_MAX,
           "inv": 0.0, "cd": 0.0, "ataque_t": 0.0, "marcado_t": 0.0, "dano_t": 0.0, "cura_t": 0.0,
           "aviso": "", "aviso_t": 0.0, "moviendo": False}

_polen_t = 0.0
transicion = {"t": 0.0, "titulo": ""}   # fundido y título al cambiar de nivel
_iniciada = False


# Inicia: estadísticas del personaje activo
def stats():
    return ESTADISTICAS[h.personaje_actual]


# Inicia: mensaje central temporal
def avisar(texto, seg=2.5):
    mensaje[0] = texto
    mensaje[1] = seg


# Inicia: ¿el escenario actual es el nivel en juego?
def en_nivel():
    return h.estado_escenario == NIVELES[nivel]


# Inicia: nueva partida desde el primer escenario
def iniciar_partida(personaje):
    global fase, nivel, t_fase, salida_activa, _iniciada
    _iniciada = True
    fase = "JUGANDO"
    nivel = 0
    t_fase = 0.0
    salida_activa = False
    contadores.update(eliminados=0, atp=0, eritrocitos=0)
    teclas.clear()
    combate.limpiar()
    _poner_jugador(personaje)
    bio.iniciar_nivel(NIVELES[0])
    avisar("Elimina a los patógenos y cruza la salida", 4.0)
    transicion.update(t=1.2, titulo="NIVEL 1 - MIOCARDIO")


def _poner_jugador(personaje):
    j = jugador
    j.update(x=INICIO[0], z=INICIO[1], ang=180.0, salud=SALUD_MAX, energia=ENERGIA_MAX, inv=0.0, cd=0.0,
             ataque_t=0.0, marcado_t=0.0, dano_t=0.0, cura_t=0.0, aviso="", aviso_t=0.0, moviendo=False)


# Inicia: reiniciar la partida con el mismo personaje (derrota o menú)
def reiniciar():
    iniciar_partida(h.personaje_actual)
    h.estado_escenario = NIVELES[0]
    play_sound("reiniciar")


# Inicia: regresar al menú de selección
def volver_al_menu():
    global fase
    fase = "JUGANDO"
    teclas.clear()
    h.estado_escenario = "MENU"
    play_sound("click")


# Inicia: tecla ENTER en las pantallas finales
def aceptar():
    if fase == "DERROTA":
        reiniciar()
    elif fase == "VICTORIA":
        volver_al_menu()


# Inicia: registrar dirección sostenida
def tecla(direccion, presionada):
    if presionada:
        teclas.add(direccion)
    else:
        teclas.discard(direccion)


# Inicia: ataque del personaje
def atacar():
    if h.estado_escenario == "MENU" or fase != "JUGANDO" or not en_nivel():
        return
    combate.atacar(jugador, stats(), h.personaje_actual)


# Inicia: altura del salto (el movimiento "saltar" gasta energía)
def altura_salto(t):
    if h.estado_movimiento == "saltar":
        return abs(math.sin(t * 8)) * 2.0
    return 0.0


# Inicia: expresión y movimiento que se muestran según lo que ocurre
def pose():
    exp, mov = h.estado_expresion, h.estado_movimiento
    j = jugador
    if fase == "VICTORIA":
        return "feliz", "saludar"
    if fase == "DERROTA":
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


# Inicia: mover al jugador con velocidad por personaje
def _mover(dt, st):
    j = jugador
    dx = (1.0 if "der" in teclas else 0.0) - (1.0 if "izq" in teclas else 0.0)
    dz = (1.0 if "aba" in teclas else 0.0) - (1.0 if "arr" in teclas else 0.0)
    j["moviendo"] = bool(dx or dz)
    if j["moviendo"]:
        n = math.hypot(dx, dz)
        dx, dz = dx / n, dz / n
        j["x"] += dx * st["vel"] * VEL_FACTOR * dt
        j["z"] += dz * st["vel"] * VEL_FACTOR * dt
        objetivo = math.degrees(math.atan2(dx, dz))
        diff = (objetivo - j["ang"] + 180.0) % 360.0 - 180.0
        j["ang"] += diff * min(1.0, 14.0 * dt)
    j["x"], j["z"] = bio.resolver(j["x"], j["z"], RADIO_JUGADOR)


# Inicia: aplicar un golpe recibido (el escudo frontal del Perno lo bloquea)
def _recibir_dano(e, st):
    j = jugador
    if j["inv"] > 0.0:
        return
    dx, dz = e["x"] - j["x"], e["z"] - j["z"]
    d = max(0.01, math.hypot(dx, dz))
    a = math.radians(j["ang"])
    if st["escudo"] and (dx * math.sin(a) + dz * math.cos(a)) / d > 0.3:
        j["inv"] = 0.35
        fx.explosion((j["x"] + dx / d * 1.8, 2.2, j["z"] + dz / d * 1.8), (0.4, 1.0, 1.0), 14, 6.0, 0.4, 7.0, 0.0)
        play_sound("click")
        avisar("Escudo: golpe bloqueado", 0.8)
        return
    j["salud"] -= bio.DATOS[e["tipo"]]["dano"] * st["defensa"]
    j["inv"] = INVULNERABLE
    j["dano_t"] = 0.5
    fx.explosion((j["x"], 2.0, j["z"]), (1.0, 0.2, 0.2), 16, 5.0, 0.5, 7.0)
    play_sound("abajo")


# Inicia: recoger eritrocito, ATP o anticuerpo
def _recoger(e, st):
    j = jugador
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


# Inicia: procesar eventos de las entidades
def _procesar_eventos(st):
    for tipo, e in bio.tomar_eventos():
        if tipo == "contacto":
            _recibir_dano(e, st)
        elif tipo == "recoger":
            _recoger(e, st)
        elif tipo == "eliminado":
            contadores["eliminados"] += 1
            play_sound("reiniciar")


NOMBRES_NIVEL = {0: "MIOCARDIO", 1: "VASO SANGUÍNEO", 2: "GANGLIO LINFÁTICO"}


# Inicia: saltar a un nivel (al limpiar la sala o con la tecla de cambio de nivel)
def ir_a_nivel(indice):
    global nivel, salida_activa
    if not _iniciada:
        iniciar_partida(h.personaje_actual)
    if fase != "JUGANDO" or not 0 <= indice < len(NIVELES):
        return
    nivel = indice
    salida_activa = False
    h.estado_escenario = NIVELES[nivel]
    bio.iniciar_nivel(NIVELES[nivel])
    combate.limpiar()
    jugador["x"], jugador["z"] = INICIO
    titulo = f"NIVEL {nivel + 1} - {NOMBRES_NIVEL[NIVELES[nivel]]}"
    avisar("Elimina a los patógenos y cruza la salida", 3.0)
    transicion.update(t=1.2, titulo=titulo)
    jugador["inv"] = 1.2   # a salvo durante el fundido


# Inicia: pasar al siguiente escenario o ganar
def _avanzar():
    global nivel, fase, t_fase, salida_activa, dato
    if nivel + 1 < len(NIVELES):
        ir_a_nivel(nivel + 1)
        if h.personaje_actual == "perno":
            jugador["salud"] = SALUD_MAX
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


# Inicia: actualizar todo el juego un cuadro
def actualizar(dt, t):
    global t_fase, salida_activa, _polen_t
    dt = min(dt, 0.05)
    fx.actualizar(dt)
    if h.estado_escenario == "MENU":
        return
    if not _iniciada:   # por si se salta el menú con el clic derecho
        iniciar_partida(h.personaje_actual)
    j = jugador
    st = stats()
    transicion["t"] = max(0.0, transicion["t"] - dt)
    for clave in ("inv", "cd", "ataque_t", "marcado_t", "dano_t", "cura_t", "aviso_t"):
        j[clave] = max(0.0, j[clave] - dt)
    mensaje[1] = max(0.0, mensaje[1] - dt)

    if fase != "JUGANDO":
        t_fase += dt
        return
    _mover(dt, st)
    if not en_nivel():
        return

    # Energía: el salto la consume, si no se recupera sola
    if h.estado_movimiento == "saltar":
        j["energia"] -= ENERGIA_SALTO * dt
        if j["energia"] <= 0.0:
            j["energia"] = 0.0
            h.estado_movimiento = "reposo"
    else:
        j["energia"] = min(ENERGIA_MAX, j["energia"] + st["regen"] * dt)

    # Polen reparador de Brote
    if h.personaje_actual == "brote":
        _polen_t -= dt
        if _polen_t <= 0.0:
            _polen_t = 0.12
            fx.flotar((j["x"], 1.2, j["z"]), (1.0, 0.9, 0.3), 1, 1.6, 5.0)

    # Disparo sostenido: mientras se mantiene ESPACIO se repite el ataque (el enfriamiento lo limita)
    if "fuego" in teclas:
        combate.atacar(j, st, h.personaje_actual)

    bio.config["prob_eri"] = st["prob_eri"]
    bio.actualizar(dt, t, j["x"], j["z"], bio.ALTURA_CENTRO + altura_salto(t), RADIO_JUGADOR)
    _procesar_eventos(st)
    combate.actualizar(dt, j)

    if j["salud"] <= 0.0:
        j["salud"] = 0.0
        _derrota()
        return
    if not bio.hay_patogenos():
        if not salida_activa:
            salida_activa = True
            avisar("Sala limpia: cruza la salida luminosa", 3.5)
            play_sound("cambiarcolor")
        elif math.hypot(j["x"] - SALIDA[0], j["z"] - SALIDA[1]) < RADIO_SALIDA:
            _avanzar()


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
        _flecha_guia(t, col)
    if activa and random.random() < 0.5:
        fx.flotar((x, 0.5, z), col, 1, 1.4, 5.0)


# Inicia: flecha en el piso que señala hacia la salida
def _flecha_guia(t, col):
    j = jugador
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


_q = None


def gluNewQuadric_cache():
    global _q
    if _q is None:
        _q = gluNewQuadric()
    return _q
