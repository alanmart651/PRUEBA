from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import HandLes as h
from RESOURCES import hud

DORADO = (1.0, 0.84, 0.0)
BLANCO = (1.0, 1.0, 1.0)

# Guía de teclas que se muestra en "Controles e Instrucciones"
LINEAS_CONTROLES = [
    "J1: A / D / W / S mover | ESPACIO atacar (mantener = repetir) | E hablar con un NPC",
    "J2 (dos jugadores): flechas mover | ENTER atacar | SHIFT derecho o FIN hablar",
    "Jugando solo, las flechas, ENTER y SHIFT derecho también son del J1",
    "Diálogo: W/S o flechas elegir | E o ENTER aceptar | 1-9 opción | RETROCESO cerrar",
    "Saltar: C (gasta energía)",
    "Cámara: arrastrar con el ratón = orbitar | rueda = zoom | R = reiniciar cámara",
    "Pantalla: I = instrucciones | H = acerca de",
    "Cambiar de nivel: F1, F2 y F3",
    "Pausa: P o ESC",
    "Eritrocito = salud | ATP = energía | Anticuerpo = marca a los patógenos",
    "Objetivo: elimina a todos los patógenos y cruza la salida luminosa",
]

_textura = None          # imagen de la escena congelada
_textura_valida = False  # False si la tarjeta no pudo copiar la imagen


# Inicia: tamaño actual de la ventana
def _tamano():
    viewport = glGetIntegerv(GL_VIEWPORT)
    return int(viewport[2]), int(viewport[3])


# Inicia: pasar a proyección 2D (origen arriba a la izquierda) y aislar el estado gráfico
def _abrir_2d(ancho, alto):
    glPushAttrib(GL_ALL_ATTRIB_BITS)  # type: ignore
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, ancho, alto, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


# Inicia: restaurar las matrices y el estado gráfico
def _cerrar_2d():
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glPopAttrib()


# Inicia: guardar la imagen de la escena 3D que se está viendo (se llama al empezar la pausa)
def capturar_escena():
    global _textura, _textura_valida
    ancho, alto = _tamano()
    try:
        if _textura is None:
            _textura = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, _textura)
        glReadBuffer(GL_BACK)
        glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 0, 0, ancho, alto, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glBindTexture(GL_TEXTURE_2D, 0)
        _textura_valida = True
    except Exception:
        _textura_valida = False


# Inicia: dibujar la escena congelada a pantalla completa
def dibujar_fondo_congelado():
    if not _textura_valida:
        return
    ancho, alto = _tamano()
    _abrir_2d(ancho, alto)
    glDisable(GL_BLEND)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, _textura)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex2f(0, 0)
    glTexCoord2f(1.0, 1.0); glVertex2f(ancho, 0)
    glTexCoord2f(1.0, 0.0); glVertex2f(ancho, alto)
    glTexCoord2f(0.0, 0.0); glVertex2f(0, alto)
    glEnd()
    glBindTexture(GL_TEXTURE_2D, 0)
    _cerrar_2d()


# Inicia: dibujar el menú de pausa (opciones según h.subestado_pausa)
def draw_pause_menu():
    ancho, alto = _tamano()
    opciones = h.opciones_pausa()
    _abrir_2d(ancho, alto)

    # Fondo oscuro semitransparente que atenúa la escena
    hud._rect(0, 0, ancho, alto, 0.0, 0.0, 0.0, 0.68)

    # Panel central que tapa el HUD congelado y deja leer el menú
    panel = min(700, ancho - 40)
    hud._rect((ancho - panel) / 2, 44, panel, alto - 80, 0.03, 0.03, 0.08, 0.93)

    hud.texto_centrado(78, "PAUSA", DORADO, ancho, hud.FUENTE_GRANDE)
    if h.subestado_pausa != "PRINCIPAL":
        hud.texto_centrado(108, h.TITULOS_PAUSA[h.subestado_pausa], BLANCO, ancho)

    # Guía de teclas (solo en la vista de controles)
    y = 150
    if h.subestado_pausa == "CONTROLES":
        for linea in LINEAS_CONTROLES:
            hud.texto_centrado(y, linea, BLANCO, ancho)
            y += 30
        y += 20

    # Opciones: la seleccionada en dorado y las demás en blanco
    paso = max(24, min(34, (alto - y - 70) / max(1, len(opciones))))
    for i, (etiqueta, _) in enumerate(opciones):
        if i == h.indice_pausa:
            hud.texto_centrado(y + i * paso, "> " + etiqueta + " <", DORADO, ancho)
        else:
            hud.texto_centrado(y + i * paso, etiqueta, BLANCO, ancho)

    hud.texto_centrado(alto - 28, "[W/S] o flechas: mover    [ENTER]: elegir    [ESC]: atrás    [P]: reanudar",
                       (0.75, 0.75, 0.75), ancho)
    _cerrar_2d()
