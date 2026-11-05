from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import sys
import time
from CHARACTERS import Issac as issac
from RESOURCES import HandLes as h
from RESOURCES import iluminacion as luz
from RESOURCES import hud
from SCENS import saladeangel as sala_angel
from SCENS import saladeldiablo as sala_diablo
from SCENS import saladarkroom as darkroom
from ACTIONS.audio import init_audio, shutdown_audio, play_sound
from CHARACTERS import azazel as azazel
from CHARACTERS import chispa as chispa
from CHARACTERS import mapi as mapi
from SCENS import homeroom as home
from SCENS import heartroom as heart
from SCENS import salapuzle as sala
from SCENS import salaplanetarium as planetario
from SCENS import objetos_biologicos as bio
from SCENS import menu_seleccion as menu

width = 1240
height = 680

RADIO_JUGADOR = 1.2

PRIORIDAD = ["virus", "bacteria", "anticuerpo", "globulo", "vesicula", "atp"]

REACCIONES = {
    "virus": ("enojado", "agacharse"),
    "bacteria": ("miedo", "caminar"),
    "anticuerpo": ("triste", None),
    "globulo": ("guiño", None),
    "vesicula": ("asombro", None),
    "atp": ("feliz", "saludar"),
}

colisiones_previas = set()


#init
def init():
    luz.configurar_iluminacion_base()
    glClearColor(*h.bg_colors[h.bg_color_index])


#altura del salto del jugador
def altura_salto(t):
    if h.estado_movimiento == "saltar":
        return abs(math.sin(t * 8)) * 2.0
    return 0.0


#verificar y dibujar objetos biológicos
def verificar_y_dibujar_biologicos(px, py, pz, pradio, t, mostrar_hitboxes):
    bio.verificar_vesicula(px, pz, pradio)
    bio.verificar_virus(px, py, pz, pradio, t)
    bio.verificar_atp(px, pz)
    bio.verificar_globulo(px, py, pz, pradio, t)
    bio.verificar_bacteria(px, pz, pradio, t)
    bio.verificar_anticuerpo(px, py, pz, pradio, t)

    bio.draw_vesicula(mostrar_hitboxes)
    bio.draw_virus(mostrar_hitboxes)
    bio.draw_atp(mostrar_hitboxes, t)
    bio.draw_globulo(mostrar_hitboxes, t)
    bio.draw_bacteria(mostrar_hitboxes, t)
    bio.draw_anticuerpo(mostrar_hitboxes)

    return bio.objetos_en_colision()


#reacción del personaje ante las colisiones
def reaccion_actual(colisiones):
    if not colisiones or not h.reacciones_activas:
        return h.estado_expresion, h.estado_movimiento
    for nombre in PRIORIDAD:
        if nombre in colisiones:
            expresion, movimiento = REACCIONES[nombre]
            return expresion, (movimiento or h.estado_movimiento)
    return h.estado_expresion, h.estado_movimiento


#sonido al entrar en contacto con un objeto nuevo
def notificar_nuevas_colisiones(actuales):
    global colisiones_previas
    if set(actuales) - colisiones_previas:
        play_sound("click")
    colisiones_previas = set(actuales)


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Menú de selección de personaje: pantalla propia, sin escena ni objetos
    if h.estado_escenario == "MENU":
        menu.draw_character_select_menu(time.time())
        glutSwapBuffers()
        return

    glTranslatef(0.0, -3.0, h.zoom_z)
    glRotatef(h.angle_x, 1, 0, 0)
    glRotatef(h.angle_y, 0, 1, 0)

    t = time.time()
    salto = altura_salto(t)
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
    elif h.estado_escenario == "y":
        sala.draw_puzzle_room()
    elif h.estado_escenario == "u":
        planetario.draw_planetarium_room()

    luz.aplicar_luces(t, h.estado_escenario)

    # Sombras
    luz.dibujar_sombra(h.player_x, h.player_z, 1.3, salto)
    for sx, sz, radio, altura in bio.sombras():
        luz.dibujar_sombra(sx, sz, radio, altura)

    colisiones = verificar_y_dibujar_biologicos(
        h.player_x, bio.ALTURA_CENTRO + salto, h.player_z, RADIO_JUGADOR, t, h.mostrar_hitboxes)
    notificar_nuevas_colisiones(colisiones)

    expresion, movimiento = reaccion_actual(colisiones)
    h.expresion_mostrada = expresion
    h.movimiento_mostrado = movimiento

    # Personaje
    glPushMatrix()
    glTranslatef(h.player_x, 0.0, h.player_z - 7.0)

    if h.personaje_actual == "isaac":
        issac.draw_isaac(expresion, movimiento, t)
    elif h.personaje_actual == "azazel":
        azazel.draw_azazel(expresion, movimiento, t)
    elif h.personaje_actual == "chispa":
        chispa.draw_chispa(expresion, movimiento, t)
    else:
        mapi.draw_mapi(expresion, movimiento, t)

    # Hitbox del jugador
    if h.mostrar_hitboxes:
        con_luz = glIsEnabled(GL_LIGHTING)
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glTranslatef(0.0, bio.ALTURA_CENTRO + salto, 7.0)
        glColor3f(1.0, 0.0, 0.0) if colisiones else glColor3f(0.0, 1.0, 0.0)
        glutWireSphere(RADIO_JUGADOR, 12, 12)
        glPopMatrix()
        if con_luz:
            glEnable(GL_LIGHTING)

    glPopMatrix()

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

    glutKeyboardFunc(h.keyboard)
    glutSpecialFunc(h.special_keys)
    glutMouseFunc(h.mouse_click)
    glutMotionFunc(h.mouse_motion)

    glutMainLoop()
    shutdown_audio()


if __name__ == "__main__":
    main()
