from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import HandLes as h
from RESOURCES import iluminacion as luz
from SCENS import objetos_biologicos as bio

NOMBRES_ESCENARIO = {6: "Ángel", 7: "Diablo", 8: "Dark room", 9: "Home", 0: "Corazón", "y": "Puzzle", "u": "Planetario"}


#texto 2D
def draw_text_2D(x, y, text, r, g, b):
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))  # type: ignore


#panel de colisiones
def draw_panel_colisiones(x, y):
    activos = bio.objetos_en_colision()
    draw_text_2D(x, y, "COLISIONES", 1, 1, 1)
    for i, nombre in enumerate(bio.OBJETOS):
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

    draw_text_2D(width - 150, height - 40, "[I]  Instrucciones", 1, 1, 1)
    draw_text_2D(width - 150, height - 20, "[H]  Acerca De", 1, 1, 1)

    if h.mostrar_acerca_de:
        draw_text_2D(20, 30, "ACERCA DE", 1, 1, 1)
        draw_text_2D(20, 60, "Isaac, Azazel, Chispa y Mapi", 1, 1, 1)
        draw_text_2D(20, 85, "Creado por: Roberto Tapia Ramírez (cannibalfps)\n Alana Yahir Martinez Flores", 1, 1, 1)

    if h.mostrar_instrucciones:
        draw_text_2D(20, 150, "CONTROLES", 1, 1, 1)
        draw_text_2D(20, 178, "Cámara: clic izq. y arrastrar | Rueda = zoom | Flechas = girar | Clic der. = menú", 1, 1, 1)
        draw_text_2D(20, 206, "Mover personaje: W A S D", 1, 1, 1)
        draw_text_2D(20, 234, "Movimientos: Z reposo | X caminar | C saltar | G saludar | B agacharse", 1, 1, 1)
        draw_text_2D(20, 262, "N brazos | M piernas | , inclinarse | . flotar", 1, 1, 1)
        draw_text_2D(20, 290, "Expresiones: 1 normal | 2 feliz | 3 triste | 4 enojado | 5 asombro | Q guiño | J miedo", 1, 1, 1)
        draw_text_2D(20, 318, "Escenarios: 6 ángel | 7 diablo | 8 dark | 9 home | 0 corazón | Y puzzle | U planetario", 1, 1, 1)
        draw_text_2D(20, 346, "Personaje: K | Hitboxes: V | Luz: L | Sombreado: F | Sombras: O | Reacciones: E", 1, 1, 1)
        draw_text_2D(20, 374, "Sonido: P | Reiniciar cámara: R | Salir: ESC", 1, 1, 1)

        # A la derecha: en la columna izquierda se encimaría con el panel de estado
        draw_panel_colisiones(width - 300, 150)
        draw_panel_estado(height)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    if luz.luz_activa:
        glEnable(GL_LIGHTING)