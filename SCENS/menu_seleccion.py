import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from CHARACTERS import personajes
from RESOURCES import HandLes as h
from RESOURCES import hud
from RESOURCES import visual as v

TITULO = "SELECCIONA TU CÉLULA"
AYUDA = "[A/D o FLECHAS] mover   |   [ENTER] confirmar   |   [ESC] salir"
FUENTE_TITULO = GLUT_BITMAP_TIMES_ROMAN_24  # type: ignore
FUENTE = GLUT_BITMAP_HELVETICA_18  # type: ignore

# posición X de cada pedestal y personaje que muestra
SLOTS = {"isaac": -15.0, "azazel": -9.0, "chispa": -3.0, "mapi": 3.0, "brote": 9.0, "perno": 15.0}
NOMBRES = {"isaac": "ISAAC", "azazel": "AZAZEL", "chispa": "CHISPA", "mapi": "MAPI",
           "brote": "BROTE", "perno": "PERNO"}
RADIO_PEDESTAL = 2.6
ALTO_PEDESTAL = 0.8

# Célula que representa cada personaje, su habilidad y su limitación
ROLES = {
    "isaac": "Macrófago (inmunidad innata) - disparo de lágrimas - resistente, pasos pesados",
    "azazel": "Linfocito T citotóxico (adaptativa) - rayo de sangre - daño alto, alcance medio",
    "chispa": "Célula dendrítica (innata) - destello que aturde - el más rápido, daño bajo",
    "mapi": "Linfocito B de memoria (adaptativa) - anticuerpos teledirigidos - débil de cerca",
    "brote": "Fibroblasto cardiaco (soporte) - polen que atrae eritrocitos - daño muy bajo",
    "perno": "Nanobot de inmunoterapia (externo) - lisis instantánea y escudo - gasta mucha energía",
}

_quad = None


#quadric sólido
def _quadric():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
        gluQuadricDrawStyle(_quad, GLU_FILL)
        gluQuadricNormals(_quad, GLU_SMOOTH)
    return _quad


#luz destacada para el personaje seleccionado
def _luz_destacada(x):
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.20, 0.20, 0.22, 1.0))
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (x, 10.0, 8.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.25, 0.25, 0.25, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.00, 0.95, 0.85, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.00, 1.00, 1.00, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 96.0)


#luz tenue para el personaje no seleccionado
def _luz_atenuada(x):
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.04, 0.04, 0.05, 1.0))
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (x, 10.0, 8.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.02, 0.02, 0.03, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.14, 0.14, 0.18, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.0, 0.0, 0.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 4.0)


#piso del escenario
def _dibujar_piso():
    glColor3f(0.06, 0.06, 0.08)
    glNormal3f(0.0, 1.0, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-30, 0, -20)
    glVertex3f(30, 0, -20)
    glVertex3f(30, 0, 20)
    glVertex3f(-30, 0, 20)
    glEnd()


#pedestal cilíndrico con aro de color
def _dibujar_pedestal(seleccionado):
    quad = _quadric()
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)

    glColor3f(0.55, 0.55, 0.60)
    gluCylinder(quad, RADIO_PEDESTAL, RADIO_PEDESTAL * 0.92, ALTO_PEDESTAL, 32, 1)

    # tapa superior
    glTranslatef(0.0, 0.0, ALTO_PEDESTAL)
    gluDisk(quad, 0.0, RADIO_PEDESTAL * 0.92, 32, 1)

    # aro de color (dorado si está seleccionado)
    glColor3f(1.0, 0.8, 0.2) if seleccionado else glColor3f(0.25, 0.22, 0.12)
    glTranslatef(0.0, 0.0, 0.02)
    gluDisk(quad, RADIO_PEDESTAL * 0.80, RADIO_PEDESTAL * 0.88, 32, 1)
    glPopMatrix()


#haz de luz cálido sobre el pedestal seleccionado
def _haz_de_luz():
    v.iniciar_aditivo()
    glPushMatrix()
    glTranslatef(0.0, ALTO_PEDESTAL, 0.0)
    glRotatef(-90, 1, 0, 0)
    glColor4f(1.0, 0.85, 0.5, 0.07)
    glutSolidCone(RADIO_PEDESTAL * 0.95, 12.0, 28, 1)
    glColor4f(1.0, 0.9, 0.6, 0.05)
    glutSolidCone(RADIO_PEDESTAL * 0.55, 12.0, 20, 1)
    glPopMatrix()
    v.terminar_transparencia()


#personaje sobre su pedestal
def _dibujar_personaje(nombre, seleccionado, t):
    x = SLOTS[nombre]
    glPushMatrix()
    glTranslatef(x, 0.0, 0.0)

    _dibujar_pedestal(seleccionado)
    if seleccionado:
        _haz_de_luz()

    glTranslatef(0.0, ALTO_PEDESTAL, 0.0)
    glTranslatef(0.0, 0.0, -7.0)
    if seleccionado:
        # giro suave para lucir al personaje seleccionado
        glTranslatef(0.0, 0.0, 7.0)
        glRotatef(math.sin(t * 1.5) * 25.0, 0, 1, 0)
        glTranslatef(0.0, 0.0, -7.0)
        expresion, movimiento = "feliz", "saludar"
    else:
        expresion, movimiento = "normal", "reposo"

    personajes.DIBUJAR[nombre](expresion, movimiento, t)
    glPopMatrix()


#ancho en píxeles de un texto con la fuente del HUD
def _ancho_texto(texto):
    return hud.ancho_texto(texto)


#HUD 2D del menú
def _dibujar_hud():
    viewport = glGetIntegerv(GL_VIEWPORT)
    ancho, alto = viewport[2], viewport[3]

    # centro en pantalla de cada pedestal
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    centros = {nombre: gluProject(x, 0.0, 0.0, modelview, projection, viewport)[0]
               for nombre, x in SLOTS.items()}

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, ancho, alto, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    hud.texto_centrado(48, TITULO, (1.0, 0.85, 0.3), ancho, FUENTE_TITULO)
    hud.texto_centrado(80, AYUDA, (1.0, 1.0, 1.0), ancho)
    hud.texto_centrado(alto - 24, ROLES[h.personaje_actual], (1.0, 0.85, 0.5), ancho)

    for nombre, centro in centros.items():
        etiqueta = NOMBRES[nombre]
        r, g, b = (1.0, 0.8, 0.2) if nombre == h.personaje_actual else (1.0, 1.0, 1.0)
        hud.draw_text_2D(centro - _ancho_texto(etiqueta) / 2, alto - 60, etiqueta, r, g, b)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)


#menú de selección de personaje estilo arcade
def draw_character_select_menu(t):
    # Cámara fija
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 6.0, 21.0, 0.0, 2.8, 0.0, 0.0, 1.0, 0.0)

    glPushAttrib(GL_LIGHTING_BIT | GL_ENABLE_BIT | GL_CURRENT_BIT)  # type: ignore
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glDisable(GL_LIGHT1)

    # El piso y el personaje no seleccionado reciben la luz tenue
    _luz_atenuada(0.0)
    _dibujar_piso()

    for nombre in SLOTS:
        seleccionado = (nombre == h.personaje_actual)
        if seleccionado:
            _luz_destacada(SLOTS[nombre])
        else:
            _luz_atenuada(SLOTS[nombre])
        _dibujar_personaje(nombre, seleccionado, t)

    glPopAttrib()

    _dibujar_hud()
