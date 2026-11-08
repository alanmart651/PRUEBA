from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import sys
import time
from CHARACTERS import personajes
from RESOURCES import HandLes as h
from RESOURCES import iluminacion as luz
from RESOURCES import hud
from RESOURCES import visual as v
from SCENS import saladeangel as sala_angel
from SCENS import saladeldiablo as sala_diablo
from SCENS import saladarkroom as darkroom
from ACTIONS import juego
from ACTIONS import combate
from ACTIONS.audio import init_audio, shutdown_audio
from SCENS import homeroom as home
from SCENS import heartroom as heart
from SCENS import salapuzle as sala
from SCENS import salaplanetarium as planetario
from SCENS import vasos
from SCENS import objetos_biologicos as bio
from SCENS import efectos as fx
from SCENS import menu_seleccion as menu

width = 1240
height = 680

# Fondo y niebla de los escenarios orgánicos: (color, densidad)
AMBIENTES = {0: ((0.10, 0.01, 0.02), 0.013), "t": ((0.12, 0.02, 0.04), 0.012)}

ultimo_t = time.time()

# El modelo del jugador se reduce un poco en partida para no tapar el escenario
ESCALA_JUGADOR = 0.8


#init
def init():
    luz.configurar_iluminacion_base()
    glClearColor(*h.bg_colors[h.bg_color_index])
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)


#personaje del jugador, girado hacia donde mira
def dibujar_jugador(t, expresion, movimiento, salto):
    j = juego.jugador
    en_juego = juego.en_nivel() and juego.fase == "JUGANDO"
    glPushMatrix()
    glTranslatef(j["x"], 0.0, j["z"] - 7.0)
    glTranslatef(0.0, 0.0, 7.0)
    glRotatef(j["ang"], 0, 1, 0)
    glPushMatrix()
    glScalef(ESCALA_JUGADOR, ESCALA_JUGADOR, ESCALA_JUGADOR)
    glTranslatef(0.0, 0.0, -7.0)

    # Parpadea mientras es invulnerable tras un golpe
    if not (en_juego and j["inv"] > 0.0 and int(t * 14) % 2 == 0):
        personajes.DIBUJAR[h.personaje_actual](expresion, movimiento, t)

    # Escudo frontal del Perno
    if en_juego and juego.stats()["escudo"]:
        v.iniciar_aditivo()
        glPushMatrix()
        glTranslatef(0.0, 2.4, 7.0 + 1.9)
        glScalef(1.9, 2.4, 0.25)
        glColor4f(0.3, 0.9, 1.0, 0.2 + 0.06 * math.sin(t * 6.0))
        glutSolidSphere(1.0, 18, 14)
        glPopMatrix()
        v.terminar_transparencia()
    glPopMatrix()
    glTranslatef(0.0, 0.0, -7.0)

    # Hitbox del jugador
    if h.mostrar_hitboxes:
        con_luz = glIsEnabled(GL_LIGHTING)
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glTranslatef(0.0, bio.ALTURA_CENTRO + salto, 7.0)
        glColor3f(1.0, 0.0, 0.0) if bio.objetos_en_colision() else glColor3f(0.0, 1.0, 0.0)
        glutWireSphere(juego.RADIO_JUGADOR, 12, 12)
        glPopMatrix()
        if con_luz:
            glEnable(GL_LIGHTING)
    glPopMatrix()


def display():
    global ultimo_t
    ahora = time.time()
    dt = ahora - ultimo_t
    ultimo_t = ahora
    juego.actualizar(dt, ahora)

    ambiente = AMBIENTES.get(h.estado_escenario)
    if ambiente:
        glClearColor(ambiente[0][0], ambiente[0][1], ambiente[0][2], 1.0)
    else:
        glClearColor(*h.bg_colors[h.bg_color_index])
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Menú de selección de personaje: pantalla propia, sin escena ni objetos
    if h.estado_escenario == "MENU":
        v.sin_niebla()
        menu.draw_character_select_menu(ahora)
        glutSwapBuffers()
        return

    j = juego.jugador
    glTranslatef(0.0, -3.0, h.zoom_z)
    glRotatef(h.angle_x, 1, 0, 0)
    glRotatef(h.angle_y, 0, 1, 0)
    # La cámara sigue un poco al personaje
    glTranslatef(-j["x"] * 0.3, 0.0, -(j["z"] - 7.0) * 0.3)

    if ambiente:
        v.niebla(*ambiente)
    else:
        v.sin_niebla()

    t = ahora
    salto = juego.altura_salto(t)
    luz.aplicar_luces(t, h.estado_escenario)

    # Escenarios
    if h.estado_escenario == 6:
        sala_angel.draw_angel_room()
    elif h.estado_escenario == 7:
        sala_diablo.draw_devil_room()
    elif h.estado_escenario == 8:
        darkroom.draw_dark_room()
    elif h.estado_escenario == 9:
        home.draw_home_room()
    elif h.estado_escenario == 0:
        heart.draw_moms_heart_room()
    elif h.estado_escenario == "t":
        vasos.draw_vessel_room(t)
    elif h.estado_escenario == "y":
        sala.draw_puzzle_room()
    elif h.estado_escenario == "u":
        planetario.draw_planetarium_room()

    luz.aplicar_luces(t, h.estado_escenario)

    # Sombras
    luz.dibujar_sombra(j["x"], j["z"], 1.3, salto)
    en_nivel = juego.en_nivel()
    if en_nivel:
        for sx, sz, radio, altura in bio.sombras():
            luz.dibujar_sombra(sx, sz, radio, altura)
        bio.dibujar(t, h.mostrar_hitboxes)
        juego.dibujar_salida(t)
        combate.dibujar(t)

    # Personaje
    expresion, movimiento = juego.pose()
    h.expresion_mostrada = expresion
    h.movimiento_mostrado = movimiento
    dibujar_jugador(t, expresion, movimiento, salto)

    fx.dibujar()
    v.sin_niebla()

    # HUD
    hud.draw_hud(width, height)
    glutSwapBuffers()


#reshape
def reshape(w, h_win):
    global width, height
    width, height = w, h_win
    if h_win == 0:
        h_win = 1
    glViewport(0, 0, w, h_win)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(w) / float(h_win), 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)


#main
def main():
    glutInit(sys.argv)
    # Al salir (ESC o cerrar la ventana) glutMainLoop regresa para poder cerrar el audio
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_CONTINUE_EXECUTION)
    init_audio()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # type: ignore
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Isaac")
    init()
    h.crear_menu()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(display)

    # Las teclas de movimiento se leen como "sostenidas": se ignora la repetición automática
    glutIgnoreKeyRepeat(1)
    glutKeyboardFunc(h.keyboard)
    glutKeyboardUpFunc(h.keyboard_up)
    glutSpecialFunc(h.special_keys)
    glutSpecialUpFunc(h.special_up)
    glutMouseFunc(h.mouse_click)
    glutMotionFunc(h.mouse_motion)

    glutMainLoop()
    shutdown_audio()


if __name__ == "__main__":
    main()
