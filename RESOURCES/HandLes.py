from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound, stop_sound
from RESOURCES import iluminacion as luz

ZOOM_INICIAL = -25.0

angle_x, angle_y = 0.0, 0.0
zoom_z = ZOOM_INICIAL
last_mouse_x, last_mouse_y = 0, 0
is_mouse_pressed = False
bg_color_index = 3
is_sound_playing = False
bg_colors = [(1.0, 0.0, 0.0, 1.0), (0.0, 1.0, 0.0, 1.0), (0.0, 0.0, 1.0, 1.0), (0.1, 0.1, 0.1, 1.0)]
estado_expresion = "normal"
estado_movimiento = "reposo"
mostrar_instrucciones = False
mostrar_acerca_de = False
estado_escenario = "MENU"
personaje_actual = "isaac"
opciones_personaje = ["isaac", "azazel", "chispa", "mapi"]
indice_seleccionado = 0
player_x = 0.0
player_z = 7.0
mostrar_hitboxes = False
reacciones_activas = True

expresion_mostrada = "normal"
movimiento_mostrado = "reposo"

MOVIMIENTOS = {
    b'z': "reposo", b'x': "caminar", b'c': "saltar", b'g': "saludar", b'b': "agacharse",
    b'n': "elevar_brazos", b'm': "doblar_piernas", b',': "inclinarse", b'.': "flotar",
}
EXPRESIONES = {
    b'1': "normal", b'2': "feliz", b'3': "triste", b'4': "enojado",
    b'5': "asombro", b'q': "guiño", b'j': "miedo",
}
ESCENARIOS = {b'6': 6, b'7': 7, b'8': 8, b'9': 9, b'0': 0, b'y': "y", b'u': "u"}

SONIDO_MOVIMIENTO = {"reposo": "normal", "caminar": "caminar", "saltar": "saltar", "saludar": "saludar", "agacharse": "agacharse"}
SONIDO_EXPRESION = {"normal": "normal", "feliz": "caminar", "triste": "saltar", "enojado": "saludar",
                    "asombro": "agacharse", "guiño": "saludar", "miedo": "caminar"}

ETIQUETAS_EXPRESION = [("Normal", "normal"), ("Feliz", "feliz"), ("Triste", "triste"), ("Enojado", "enojado"),
                       ("Asombro", "asombro"), ("Guino", "guiño"), ("Miedo", "miedo")]
ETIQUETAS_MOVIMIENTO = [("Reposo", "reposo"), ("Caminar", "caminar"), ("Saltar", "saltar"), ("Saludar", "saludar"),
                        ("Agacharse", "agacharse"), ("Elevar brazos", "elevar_brazos"),
                        ("Doblar piernas", "doblar_piernas"), ("Inclinarse", "inclinarse"), ("Flotar", "flotar")]
ETIQUETAS_ESCENARIO = [("Angel", 6), ("Diablo", 7), ("Dark room", 8), ("Home", 9),
                       ("Corazon", 0), ("Puzzle", "y"), ("Planetario", "u")]
ACCIONES_MENU = [
    ("Luz on/off", 500), ("Sombreado plano/suave", 501), ("Sombras on/off", 502),
    ("Hitboxes on/off", 503), ("Reacciones on/off", 504), ("Instrucciones", 505),
    ("Acerca de", 506), ("Reiniciar camara", 507),
]


#cambiar movimiento
def cambiar_movimiento(movimiento):
    global estado_movimiento
    estado_movimiento = movimiento
    sonido = SONIDO_MOVIMIENTO.get(movimiento)
    if sonido:
        play_sound(sonido)


#cambiar expresión
def cambiar_expresion(expresion):
    global estado_expresion
    estado_expresion = expresion
    play_sound(SONIDO_EXPRESION.get(expresion, "click"))


#cambiar escenario
def cambiar_escenario(escenario):
    global estado_escenario
    estado_escenario = escenario
    play_sound("reiniciar")


#cambiar personaje
def cambiar_personaje(personaje):
    global personaje_actual, indice_seleccionado
    personaje_actual = personaje
    if personaje in opciones_personaje:
        indice_seleccionado = opciones_personaje.index(personaje)
    play_sound("click")


#mover la selección del menú de personajes (-1 izquierda, +1 derecha)
def mover_seleccion_personaje(delta):
    nuevo = max(0, min(len(opciones_personaje) - 1, indice_seleccionado + delta))
    if nuevo != indice_seleccionado:
        cambiar_personaje(opciones_personaje[nuevo])


#confirmar el personaje elegido y entrar al juego
def confirmar_personaje():
    cambiar_personaje(opciones_personaje[indice_seleccionado])
    cambiar_escenario(0)


#reiniciar cámara
def reiniciar_camara():
    global angle_x, angle_y, zoom_z
    angle_x, angle_y = 0.0, 0.0
    zoom_z = ZOOM_INICIAL
    play_sound("reiniciar")


#alternar sonido general
def alternar_sonido():
    global is_sound_playing
    if not is_sound_playing:
        play_sound("general")
        is_sound_playing = True
    else:
        stop_sound("general")
        is_sound_playing = False


#alternar paneles y opciones
def alternar_instrucciones():
    global mostrar_instrucciones
    mostrar_instrucciones = not mostrar_instrucciones
    play_sound("click")


def alternar_acerca_de():
    global mostrar_acerca_de
    mostrar_acerca_de = not mostrar_acerca_de
    play_sound("click")


def alternar_hitboxes():
    global mostrar_hitboxes
    mostrar_hitboxes = not mostrar_hitboxes
    play_sound("click")


def alternar_reacciones():
    global reacciones_activas
    reacciones_activas = not reacciones_activas
    play_sound("click")


#teclado
def keyboard(key, x, y):
    global player_x, player_z
    k = key.lower()

    if key == b'\x1b':  # Tecla ESC para salir
        # sys.exit() no sirve aquí: dentro de un callback de GLUT la excepción se ignora
        play_sound("salir")
        glutLeaveMainLoop()

    #MENÚ DE SELECCIÓN DE PERSONAJE (solo A/D, flechas y ENTER)
    elif estado_escenario == "MENU":
        if k == b'a':
            mover_seleccion_personaje(-1)
        elif k == b'd':
            mover_seleccion_personaje(1)
        elif key in (b'\r', b'\n'):
            confirmar_personaje()

    elif k == b'r':
        reiniciar_camara()
    elif k == b'p':
        alternar_sonido()

    #INTERFAZ
    elif k == b'i':
        alternar_instrucciones()
    elif k == b'h':
        alternar_acerca_de()

    #MOVIMIENTOS, EXPRESIONES Y ESCENARIOS
    elif k in MOVIMIENTOS:
        cambiar_movimiento(MOVIMIENTOS[k])
    elif k in EXPRESIONES:
        cambiar_expresion(EXPRESIONES[k])
    elif k in ESCENARIOS:
        cambiar_escenario(ESCENARIOS[k])

    #MOVER AL PERSONAJE
    elif k == b'w':
        player_z -= 0.3
    elif k == b's':
        player_z += 0.3
    elif k == b'a':
        player_x -= 0.3
    elif k == b'd':
        player_x += 0.3

    #OPCIONES
    elif k == b'v':
        alternar_hitboxes()
    elif k == b'k':
        cambiar_personaje(opciones_personaje[(indice_seleccionado + 1) % len(opciones_personaje)])
    elif k == b'l':
        luz.alternar_luz()
        play_sound("click")
    elif k == b'f':
        luz.alternar_sombreado()
        play_sound("click")
    elif k == b'o':
        luz.alternar_sombras()
        play_sound("click")
    elif k == b'e':
        alternar_reacciones()

    glutPostRedisplay()


#teclas especiales
def special_keys(key, x, y):
    global angle_x, angle_y
    # En el menú las flechas eligen personaje; la cámara del juego no se toca
    if estado_escenario == "MENU":
        if key == GLUT_KEY_LEFT:
            mover_seleccion_personaje(-1)
        elif key == GLUT_KEY_RIGHT:
            mover_seleccion_personaje(1)
        glutPostRedisplay()
        return

    if key == GLUT_KEY_RIGHT:
        angle_y += 5
        play_sound("derecha")
    elif key == GLUT_KEY_LEFT:
        angle_y -= 5
        play_sound("izquierda")
    elif key == GLUT_KEY_UP:
        angle_x -= 5
        play_sound("arriba")
    elif key == GLUT_KEY_DOWN:
        angle_x += 5
        play_sound("abajo")
    glutPostRedisplay()


#clic del mouse
def mouse_click(button, state, x, y):
    global last_mouse_x, last_mouse_y, is_mouse_pressed, zoom_z

    # El menú tiene cámara fija: arrastrar o hacer zoom no debe afectar al juego
    if estado_escenario == "MENU":
        return

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            is_mouse_pressed = True
            last_mouse_x, last_mouse_y = x, y
            play_sound("click")
        elif state == GLUT_UP:
            is_mouse_pressed = False

    elif button == 3 and state == GLUT_DOWN:
        zoom_z += 0.5
    elif button == 4 and state == GLUT_DOWN:
        zoom_z -= 0.5

    glutPostRedisplay()


#movimiento del mouse
def mouse_motion(x, y):
    global angle_x, angle_y, last_mouse_x, last_mouse_y
    if is_mouse_pressed:
        dx = x - last_mouse_x
        dy = y - last_mouse_y

        angle_y += dx * 0.5
        angle_x += dy * 0.5

        last_mouse_x, last_mouse_y = x, y
        glutPostRedisplay()


#menú del clic derecho
def menu_callback(valor):
    if valor == 100:
        cambiar_personaje("isaac")
    elif valor == 101:
        cambiar_personaje("azazel")
    elif valor == 102:
        cambiar_personaje("chispa")
    elif valor == 103:
        cambiar_personaje("mapi")
    elif 200 <= valor < 300:
        cambiar_expresion(ETIQUETAS_EXPRESION[valor - 200][1])
    elif 300 <= valor < 400:
        cambiar_movimiento(ETIQUETAS_MOVIMIENTO[valor - 300][1])
    elif 400 <= valor < 500:
        cambiar_escenario(ETIQUETAS_ESCENARIO[valor - 400][1])
    elif valor == 500:
        luz.alternar_luz()
    elif valor == 501:
        luz.alternar_sombreado()
    elif valor == 502:
        luz.alternar_sombras()
    elif valor == 503:
        alternar_hitboxes()
    elif valor == 504:
        alternar_reacciones()
    elif valor == 505:
        alternar_instrucciones()
    elif valor == 506:
        alternar_acerca_de()
    elif valor == 507:
        reiniciar_camara()
    glutPostRedisplay()


#crear menú (llamar después de glutCreateWindow)
def crear_menu():
    sub_personaje = glutCreateMenu(menu_callback)
    glutAddMenuEntry(b"Isaac", 100)
    glutAddMenuEntry(b"Azazel", 101)
    glutAddMenuEntry(b"Chispa", 102)
    glutAddMenuEntry(b"Mapi", 103)

    sub_expresion = glutCreateMenu(menu_callback)
    for i, (etiqueta, _) in enumerate(ETIQUETAS_EXPRESION):
        glutAddMenuEntry(etiqueta.encode(), 200 + i)

    sub_movimiento = glutCreateMenu(menu_callback)
    for i, (etiqueta, _) in enumerate(ETIQUETAS_MOVIMIENTO):
        glutAddMenuEntry(etiqueta.encode(), 300 + i)

    sub_escenario = glutCreateMenu(menu_callback)
    for i, (etiqueta, _) in enumerate(ETIQUETAS_ESCENARIO):
        glutAddMenuEntry(etiqueta.encode(), 400 + i)

    glutCreateMenu(menu_callback)
    glutAddSubMenu(b"Personaje", sub_personaje)
    glutAddSubMenu(b"Expresion", sub_expresion)
    glutAddSubMenu(b"Movimiento", sub_movimiento)
    glutAddSubMenu(b"Escenario", sub_escenario)
    for etiqueta, valor in ACCIONES_MENU:
        glutAddMenuEntry(etiqueta.encode(), valor)
    glutAttachMenu(GLUT_RIGHT_BUTTON)
