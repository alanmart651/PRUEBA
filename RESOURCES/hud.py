import ctypes
import math
import textwrap
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS import combate
from ACTIONS import juego
from RESOURCES import HandLes as h
from RESOURCES import iluminacion as luz
from SCENS import objetos_biologicos as bio

NOMBRES_ESCENARIO = {6: "Ángel", 7: "Diablo", 8: "Dark room", 9: "Home", 0: "Miocardio", "y": "Puzzle",
                     "u": "Planetario", 1: "Vaso sanguíneo", 2: "Ganglio linfático"}
FUENTE = GLUT_BITMAP_HELVETICA_18  # type: ignore
FUENTE_GRANDE = GLUT_BITMAP_TIMES_ROMAN_24  # type: ignore


TEXTO_FINAL = [
    "CREDITOS: Roberto Tapia Ramírez y Alan Yahir Martinez Flores",
    "Versión 1.0 - noviembre 2026",
    "PROFESoRA : Rocio Elizabeth Pulido Alba",
    "PROYECTO DE GRAFICACION",
    "PURO T-LC1 MARTES Y JUEVES DE 9-11!!!!"
]

# Valores que siguen a la barra real para mostrar el "rastro" del daño
_visible = {"salud": 1.0, "energia": 1.0}

# Anchos de texto ya calculados (los mismos textos se miden en cada cuadro)
_anchos = {}


#texto 2D
def draw_text_2D(x, y, text, r, g, b, fuente=FUENTE, a=1.0):
    glColor4f(r, g, b, a)
    glRasterPos2f(x, y)
    # Una sola llamada por línea (mucho más rápido que letra por letra desde Python)
    glutBitmapString(fuente, text.encode("latin-1", "replace"))


#ancho en píxeles de un texto
def ancho_texto(texto, fuente=FUENTE):
    clave = (texto, fuente is FUENTE)
    ancho = _anchos.get(clave)
    if ancho is None:
        datos = texto.encode("latin-1", "replace")
        try:
            ancho = glutBitmapLength(fuente, ctypes.cast(ctypes.c_char_p(datos), ctypes.POINTER(ctypes.c_ubyte)))
        except Exception:
            ancho = sum(glutBitmapWidth(fuente, b) for b in datos)
        _anchos[clave] = ancho
    return ancho


#texto con sombra para que se lea sobre cualquier fondo
def texto_sombra(x, y, text, color, fuente=FUENTE, a=1.0):
    draw_text_2D(x + 2, y + 2, text, 0.0, 0.0, 0.0, fuente, a * 0.8)
    draw_text_2D(x, y, text, color[0], color[1], color[2], fuente, a)


#texto centrado horizontalmente
def texto_centrado(y, text, color, ancho, fuente=FUENTE, a=1.0):
    texto_sombra((ancho - ancho_texto(text, fuente)) / 2, y, text, color, fuente, a)


#rectángulo relleno
def _rect(x, y, w, hh, r, g, b, a):
    glColor4f(r, g, b, a)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + hh)
    glVertex2f(x, y + hh)
    glEnd()


#barra con degradado vertical, rastro de daño y etiqueta
def _barra(x, y, w, alto, frac, vis, c_arriba, c_abajo, etiqueta):
    frac = max(0.0, min(1.0, frac))
    _rect(x - 3, y - 3, w + 6, alto + 6, 0.0, 0.0, 0.0, 0.55)
    _rect(x, y, w * max(vis, frac), alto, 1.0, 1.0, 1.0, 0.35)
    if frac > 0.0:
        glBegin(GL_QUADS)
        glColor4f(c_arriba[0], c_arriba[1], c_arriba[2], 0.95)
        glVertex2f(x, y)
        glVertex2f(x + w * frac, y)
        glColor4f(c_abajo[0], c_abajo[1], c_abajo[2], 0.95)
        glVertex2f(x + w * frac, y + alto)
        glVertex2f(x, y + alto)
        glEnd()
    glColor4f(1.0, 1.0, 1.0, 0.85)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + alto)
    glVertex2f(x, y + alto)
    glEnd()
    glLineWidth(1.0)
    texto_sombra(x + 8, y + alto - 6, etiqueta, (1.0, 1.0, 1.0))


#viñeta de bordes con color
def _vineta(width, height, color, alfa, grosor=170):
    if alfa <= 0.01:
        return
    r, g, b = color
    bordes = (((0, 0), (width, 0), (width, grosor), (0, grosor)),
              ((0, height), (width, height), (width, height - grosor), (0, height - grosor)),
              ((0, 0), (0, height), (grosor, height), (grosor, 0)),
              ((width, 0), (width, height), (width - grosor, height), (width - grosor, 0)))
    for quad in bordes:
        glBegin(GL_QUADS)
        for i, (px, py) in enumerate(quad):
            glColor4f(r, g, b, alfa if i < 2 else 0.0)
            glVertex2f(px, py)
        glEnd()


#panel de colisiones
def draw_panel_colisiones(x, y):
    activos = bio.objetos_en_colision()
    draw_text_2D(x, y, "COLISIONES", 1, 1, 1)
    for i, nombre in enumerate(bio.NOMBRES):
        marca = "[X]" if nombre in activos else "[  ]"
        draw_text_2D(x, y + 28 + i * 26, f"{marca} {bio.NOMBRES[nombre]} ({bio.METODOS[nombre]})", 1, 1, 1)


#panel de información general
def draw_panel_estado(height):
    pj = h.personaje_actual.capitalize()
    esc = NOMBRES_ESCENARIO.get(h.estado_escenario, str(h.estado_escenario))
    exp = h.expresion_mostrada + (" (reacción)" if h.expresion_mostrada != h.estado_expresion else "")
    mov = h.movimiento_mostrado + (" (reacción)" if h.movimiento_mostrado != h.estado_movimiento else "")

    def onoff(v):
        return "ON" if v else "OFF"

    draw_text_2D(20, height - 100, f"Personaje: {pj}  |  Escenario: {esc}", 1, 1, 1)
    draw_text_2D(20, height - 74, f"Expresión: {exp}  |  Movimiento: {mov}", 1, 1, 1)
    draw_text_2D(20, height - 48,
                 f"Luz: {onoff(luz.luz_activa)}  |  Sombreado: {'Suave' if luz.sombreado_suave else 'Plano'}  |  "
                 f"Sombras: {onoff(luz.sombras_activas)}  |  Hitboxes: {onoff(h.mostrar_hitboxes)}  |  "
                 f"Reacciones: {onoff(h.reacciones_activas)}", 1, 1, 1)


#barras, contadores y avisos de la partida
def _hud_partida(width, height):
    j = juego.jugador
    st = juego.stats()
    nivel = juego.en_nivel()

    _visible["salud"] += (j["salud"] / juego.SALUD_MAX - _visible["salud"]) * 0.06
    _visible["energia"] += (j["energia"] / juego.ENERGIA_MAX - _visible["energia"]) * 0.10

    texto_sombra(20, 28, f"{h.personaje_actual.upper()} - {st['celula']}", (1.0, 0.85, 0.3), FUENTE)
    _barra(20, 40, 280, 24, j["salud"] / juego.SALUD_MAX, _visible["salud"], (1.0, 0.35, 0.35), (0.7, 0.05, 0.1),
           f"SALUD {int(j['salud'])}/{int(juego.SALUD_MAX)}")
    _barra(20, 76, 280, 24, j["energia"] / juego.ENERGIA_MAX, _visible["energia"], (0.4, 1.0, 1.0), (0.1, 0.55, 0.8),
           f"ENERGÍA {int(j['energia'])}/{int(juego.ENERGIA_MAX)}")

    # Enfriamiento del ataque
    listo = 1.0 - j["cd"] / st["cooldown"] if st["cooldown"] > 0 else 1.0
    _rect(20, 108, 280, 6, 0.0, 0.0, 0.0, 0.5)
    _rect(20, 108, 280 * max(0.0, min(1.0, listo)), 6, 1.0, 0.85, 0.3, 0.9)
    texto_sombra(310, 116, "ESPACIO: ataque", (0.9, 0.9, 0.9))

    if nivel:
        quedan = sum(1 for e in bio.entidades if e["tipo"] in bio.PATOGENOS)
        texto_sombra(20, 146, f"Patógenos: {quedan}   ATP: {juego.contadores['atp']}   "
                              f"Eritrocitos: {juego.contadores['eritrocitos']}   Eliminados: {juego.contadores['eliminados']}",
                     (1.0, 1.0, 1.0))
        y = 172
        if j["marcado_t"] > 0.0:
            texto_sombra(20, y, f"Anticuerpos activos: {j['marcado_t']:.0f} s", (1.0, 0.5, 0.95))
            y += 24
        if st["escudo"]:
            texto_sombra(20, y, "Escudo frontal activo | no recupera salud", (0.4, 1.0, 1.0))

    # Barra del jefe
    jefe = bio.jefe_vivo() if nivel else None
    if jefe is not None:
        w = min(460, width - 80)
        x = (width - w) / 2
        texto_centrado(24, "BIOPELÍCULA BACTERIANA", (1.0, 0.7, 0.3), width)
        _barra(x, 34, w, 16, jefe["hp"] / jefe["hp_max"], jefe["hp"] / jefe["hp_max"], (1.0, 0.6, 0.2), (0.7, 0.25, 0.05), "")

    # Mensajes (no se muestran sobre las pantallas de victoria o derrota)
    if juego.fase != "JUGANDO":
        return
    if juego.mensaje[1] > 0.0:
        texto_centrado(height * 0.3, juego.mensaje[0], (1.0, 1.0, 0.7), width, FUENTE_GRANDE, min(1.0, juego.mensaje[1] * 2.0))
    if j["aviso_t"] > 0.0:
        texto_centrado(height * 0.36, j["aviso"], (1.0, 0.65, 0.3), width, FUENTE, min(1.0, j["aviso_t"] * 2.0))

    # Ficha informativa del patógeno o la molécula más cercana
    if nivel and not h.mostrar_instrucciones and juego.fase == "JUGANDO":
        e = bio.ficha_cercana(j["x"], j["z"])
        if e is not None:
            d = bio.DATOS[e["tipo"]]
            w, y = min(620, width - 40), height - 118
            x = (width - w) / 2
            _rect(x, y, w, 78, 0.0, 0.0, 0.0, 0.55)
            texto_sombra(x + 14, y + 26, f"{d['nombre']}  |  tamaño real: {d['tam']}  |  método: {d['metodo']}", (1.0, 0.9, 0.5))
            texto_sombra(x + 14, y + 56, d["info"], (1.0, 1.0, 1.0))


#viñetas y destello de pantalla
def _efectos_pantalla(width, height):
    j = juego.jugador
    t = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    if juego.fase == "JUGANDO" and juego.en_nivel():
        _vineta(width, height, (0.9, 0.05, 0.05), j["dano_t"] / 0.5 * 0.6)
        if j["salud"] < 30.0:
            _vineta(width, height, (0.7, 0.0, 0.0), (0.18 + 0.12 * math.sin(t * 6.0)) * (1.0 - j["salud"] / 30.0) * 2.0)
        if h.estado_escenario in (0, 1):
            _vineta(width, height, (0.5, 0.0, 0.05), 0.10 * luz.pulso_latido(t), 120)
    if combate.destello > 0.0:
        _rect(0, 0, width, height, 0.9, 0.85, 1.0, combate.destello * 0.35)


#pantallas de victoria y derrota con un dato curioso
def _pantalla_final(width, height):
    if juego.fase == "JUGANDO":
        return
    k = min(1.0, juego.t_fase * 1.2)
    victoria = juego.fase == "VICTORIA"
    _rect(0, 0, width, height, 0.0, 0.05 if victoria else 0.0, 0.02 if victoria else 0.0, 0.72 * k)
    titulo = "¡VICTORIA!" if victoria else "DERROTA"
    sub = ("Eliminaste a los patógenos y limpiaste el recorrido." if victoria
           else "Tu salud llegó a cero: los patógenos ganaron esta vez.")
    color = (0.5, 1.0, 0.7) if victoria else (1.0, 0.4, 0.4)
    texto_centrado(height * 0.30, titulo, color, width, FUENTE_GRANDE, k)
    texto_centrado(height * 0.30 + 40, sub, (1.0, 1.0, 1.0), width, FUENTE, k)
    texto_centrado(height * 0.30 + 66, f"Patógenos eliminados: {juego.contadores['eliminados']}   ATP: "
                                       f"{juego.contadores['atp']}   Eritrocitos: {juego.contadores['eritrocitos']}",
                   (1.0, 0.9, 0.6), width, FUENTE, k)
    texto_centrado(height * 0.30 + 112, "¿SABÍAS QUE...?", (1.0, 0.85, 0.3), width, FUENTE, k)
    for i, linea in enumerate(textwrap.wrap(juego.dato, 78)):
        texto_centrado(height * 0.30 + 140 + i * 26, linea, (1.0, 1.0, 1.0), width, FUENTE, k)
    for i, linea in enumerate(TEXTO_FINAL[:4]):
        if linea.strip():
            texto_centrado(height * 0.30 + 204 + i * 26, linea, (1.0, 0.9, 0.5), width, FUENTE, k)
    pulso = 0.6 + 0.4 * math.sin(juego.t_fase * 4.0)
    pie = "[ENTER] Reiniciar   [RETROCESO] Menú   [ESC] Salir" if not victoria else "[ENTER] Volver al menú   [ESC] Salir"
    texto_centrado(height * 0.30 + 325, pie, (1.0, 1.0, 1.0), width, FUENTE, k * pulso)


#fundido y título al entrar a un nivel
def _transicion(width, height):
    t = juego.transicion["t"]
    if t <= 0.0:
        return
    _rect(0, 0, width, height, 0.0, 0.0, 0.0, min(1.0, t / 0.7))
    texto_centrado(height * 0.46, juego.transicion["titulo"], (1.0, 0.9, 0.5), width, FUENTE_GRANDE, min(1.0, t / 0.5))


#HUD completo
def draw_hud(width, height):
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    _efectos_pantalla(width, height)
    _hud_partida(width, height)

    draw_text_2D(width - 150, height - 40, "[I]  Instrucciones", 1, 1, 1)
    draw_text_2D(width - 150, height - 20, "[H]  Acerca De", 1, 1, 1)

    if h.mostrar_acerca_de:
        draw_text_2D(20, 190, "ACERCA DE", 1, 1, 1)
        draw_text_2D(20, 220, "Isaac, Azazel, Chispa, Mapi, Brote y Perno", 1, 1, 1)
        draw_text_2D(20, 245, "Creado por: Roberto Tapia Ramírez y Alan Yahir Martinez", 1, 1, 1)

    if h.mostrar_instrucciones:
        _rect(10, 160, width - 20, 280, 0.0, 0.0, 0.0, 0.6)
        draw_text_2D(20, 184, "CONTROLES", 1, 0.85, 0.3)
        draw_text_2D(20, 210, "Mover: A/D o flechas izq/der = lados | W/S o flechas arriba/abajo = avanzar y retroceder", 1, 1, 1)
        draw_text_2D(20, 236, "ESPACIO = atacar (mantener = repetir) | C = saltar (gasta energía) | Ratón: arrastrar = orbitar, rueda = zoom", 1, 1, 1)
        draw_text_2D(20, 262, "Objetivo: elimina todos los patógenos y cruza la salida luminosa | Eritrocito = salud | ATP = energía | Anticuerpo = marca", 1, 1, 1)
        draw_text_2D(20, 288, "Depuración: Z/X/G/B/N/M/,/. movimientos | 1-5 Q J expresiones | 6 7 8 9 Y U salas | F1 F2 F3 (o 0 y T) = niveles 1 2 3", 1, 1, 1)
        draw_text_2D(20, 314, "K personaje | V hitboxes | L luz | F sombreado | O sombras | E reacciones | P sonido | R cámara | ESC salir", 1, 1, 1)

        # A la derecha: en la columna izquierda se encimaría con el panel de estado
        draw_panel_colisiones(width - 330, 350)
        draw_panel_estado(height)

    _pantalla_final(width, height)
    _transicion(width, height)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    if luz.luz_activa:
        glEnable(GL_LIGHTING)
