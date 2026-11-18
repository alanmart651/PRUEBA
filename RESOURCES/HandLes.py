from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from ACTIONS.audio import play_sound, stop_sound, stop_all_sounds
from ACTIONS import state
from RESOURCES import iluminacion as luz

# Cámara inicial: vista desde arriba para ver todo el escenario
ZOOM_INICIAL = -31.0
ANGULO_X_INICIAL = 30.0

angle_x, angle_y = ANGULO_X_INICIAL, 0.0
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
opciones_personaje = ["isaac", "azazel", "chispa", "mapi", "brote", "perno"]
indice_seleccionado = 0
# Modo de dos jugadores: el J2 elige su propio personaje (distinto al del J1)
dos_jugadores = False
personaje_j2 = "azazel"
indice_j2 = 1
mostrar_hitboxes = False
reacciones_activas = True

# --- Menú de pausa (sustituye al antiguo menú de clic derecho) ---
juego_pausado = False
subestado_pausa = "PRINCIPAL"   # PRINCIPAL, ESCENARIOS, PERSONAJES, AJUSTES, AVANZADO o CONTROLES
indice_pausa = 0                # cursor de selección del menú
captura_pausa_lista = False     # main.py guarda la imagen de la escena al empezar la pausa
# --- Ajustes ---
sonido_activo = True
mostrar_hud = True
sensibilidad_camara = 1.0

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
ESCENARIOS = {b'6': 6, b'7': 7, b'8': 8, b'9': 9, b'0': 0, b'y': "y", b'u': "u", b't': 1}

SONIDO_MOVIMIENTO = {"reposo": "normal", "caminar": "caminar", "saltar": "saltar", "saludar": "saludar", "agacharse": "agacharse"}
SONIDO_EXPRESION = {"normal": "normal", "feliz": "caminar", "triste": "saltar", "enojado": "saludar",
                    "asombro": "agacharse", "guiño": "saludar", "miedo": "caminar"}

ETIQUETAS_EXPRESION = [("Normal", "normal"), ("Feliz", "feliz"), ("Triste", "triste"), ("Enojado", "enojado"),
                       ("Asombro", "asombro"), ("Guiño", "guiño"), ("Miedo", "miedo")]
ETIQUETAS_MOVIMIENTO = [("Reposo", "reposo"), ("Caminar", "caminar"), ("Saltar", "saltar"), ("Saludar", "saludar"),
                        ("Agacharse", "agacharse"), ("Elevar brazos", "elevar_brazos"),
                        ("Doblar piernas", "doblar_piernas"), ("Inclinarse", "inclinarse"), ("Flotar", "flotar")]
ETIQUETAS_ESCENARIO = [("Nivel 1 - Corazón", 0), ("Nivel 2 - Vaso sanguíneo", 1), ("Nivel 3 - Ganglio linfático", 2),
                       ("Sala del ángel", 6), ("Sala del diablo", 7), ("Dark room", 8), ("Sala home", 9),
                       ("Puzzle", "y"), ("Planetario", "u")]
# CONTROLES: cada tecla se traduce a una acción de un jugador ("izq", "der", "arr", "aba", "atacar", "hablar").
# J1 usa WASD + ESPACIO + E. Las flechas + ENTER + SHIFT derecho son del J2 en modo de dos jugadores
# y del J1 cuando juega solo. Los mandos (ACTIONS/mandos.py) usan las mismas acciones.
TECLAS_J1 = {b'a': "izq", b'd': "der", b'w': "arr", b's': "aba", b' ': "atacar", b'e': "hablar"}
TECLAS_FLECHAS = {b'\r': "atacar", b'\n': "atacar"}
# freeglut 3 reporta Shift y Ctrl como teclas especiales; PyOpenGL no trae estas constantes.
# FIN (End) es una tecla especial estándar de GLUT: sirve de respaldo para hablar.
GLUT_KEY_SHIFT_R = 0x0071
GLUT_KEY_CTRL_R = 0x0073
FLECHAS = {GLUT_KEY_LEFT: "izq", GLUT_KEY_RIGHT: "der", GLUT_KEY_UP: "arr", GLUT_KEY_DOWN: "aba",
           GLUT_KEY_SHIFT_R: "hablar", GLUT_KEY_CTRL_R: "hablar", GLUT_KEY_END: "hablar"}
NIVELES_F = {GLUT_KEY_F1: 0, GLUT_KEY_F2: 1, GLUT_KEY_F3: 2}   # F1, F2 y F3 cambian de nivel
ACCIONES_MENU = [
    ("Luz on/off", 500), ("Sombreado plano/suave", 501), ("Sombras on/off", 502),
    ("Hitboxes on/off", 503), ("Reacciones on/off", 504), ("Instrucciones", 505),
    ("Acerca de", 506), ("Reiniciar camara", 507), ("Reiniciar partida", 508), ("Volver al menu", 509),
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


#siguiente índice libre en una dirección (en modo de dos jugadores no se repite personaje)
def _siguiente_libre(actual, delta, ocupado):
    nuevo = actual + delta
    while 0 <= nuevo < len(opciones_personaje):
        if nuevo != ocupado:
            return nuevo
        nuevo += delta
    return actual


#mover la selección del menú de personajes (-1 izquierda, +1 derecha)
def mover_seleccion_personaje(delta, jugador=0):
    global personaje_j2, indice_j2
    if jugador == 1:
        nuevo = _siguiente_libre(indice_j2, delta, indice_seleccionado)
        if nuevo != indice_j2:
            indice_j2 = nuevo
            personaje_j2 = opciones_personaje[nuevo]
            play_sound("click")
        return
    nuevo = _siguiente_libre(indice_seleccionado, delta, indice_j2 if dos_jugadores else None)
    if nuevo != indice_seleccionado:
        cambiar_personaje(opciones_personaje[nuevo])


#activar o desactivar el modo de dos jugadores (solo desde el menú)
def cambiar_modo(dos):
    global dos_jugadores, indice_j2, personaje_j2
    if dos == dos_jugadores:
        return
    dos_jugadores = dos
    if dos and indice_j2 == indice_seleccionado:
        indice_j2 = (indice_seleccionado + 1) % len(opciones_personaje)
        personaje_j2 = opciones_personaje[indice_j2]
    play_sound("cambiarcolor")


#jugador que usa las flechas y ENTER
def indice_flechas():
    return 1 if dos_jugadores else 0


#ir a un escenario (los niveles de juego reinician sus patógenos)
def ir_a_escenario(escenario):
    from ACTIONS import juego  # import tardío: juego.py también importa este módulo
    if escenario in juego.NIVELES:
        juego.ir_a_nivel(juego.NIVELES.index(escenario))
    else:
        cambiar_escenario(escenario)
    glutPostRedisplay()


#confirmar el personaje elegido y entrar al juego
def confirmar_personaje():
    from ACTIONS import juego  # import tardío: juego.py también importa este módulo
    cambiar_personaje(opciones_personaje[indice_seleccionado])
    juego.iniciar_partida(personaje_actual)
    cambiar_escenario(0)


#reiniciar cámara
def reiniciar_camara():
    global angle_x, angle_y, zoom_z
    angle_x, angle_y = ANGULO_X_INICIAL, 0.0
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


#acción de un jugador, venga del teclado o de un mando
#nombre: "izq", "der", "arr", "aba", "atacar", "hablar", "cerrar" (diálogo) o "aceptar" (menú y pantallas finales)
def accion(jugador, nombre, presionada):
    from ACTIONS import juego, npcs
    direcciones = ("izq", "der", "arr", "aba")

    #MENÚ DE SELECCIÓN: cada jugador mueve su selección; atacar o aceptar confirma
    if estado_escenario == "MENU":
        if not presionada:
            return
        if nombre in ("izq", "der"):
            mover_seleccion_personaje(-1 if nombre == "izq" else 1, jugador if dos_jugadores else 0)
        elif nombre in ("atacar", "aceptar"):
            confirmar_personaje()
        return

    #PANTALLAS FINALES
    if juego.fase != "JUGANDO":
        if presionada and nombre in ("atacar", "aceptar"):
            juego.aceptar()
        return

    #DIÁLOGO ABIERTO: solo lo maneja quien habla (las teclas soltadas se registran igual)
    if npcs.abierto():
        if not presionada:
            if nombre in direcciones:
                juego.tecla(nombre, False, jugador)
            return
        if npcs.dialogo["jugador"]["id"] != jugador:
            return
        if nombre == "arr":
            npcs.mover(-1)
        elif nombre == "aba":
            npcs.mover(1)
        elif nombre in ("atacar", "hablar", "aceptar"):
            npcs.confirmar()
        elif nombre == "cerrar":
            npcs.cerrar()
        return

    #JUEGO: moverse (sostenido), atacar (sostenido) y hablar
    if nombre in direcciones:
        juego.tecla(nombre, presionada, jugador)
    elif nombre == "atacar":
        juego.tecla("fuego", presionada, jugador)
        if presionada:
            juego.atacar(jugador)
    elif nombre == "hablar" and presionada:
        juego.interactuar(jugador)


#tecla normal -> (jugador, acción) o None
def _accion_de_tecla(key):
    k = key.lower()
    if k in TECLAS_J1:
        return 0, TECLAS_J1[k]
    if key in TECLAS_FLECHAS:
        return indice_flechas(), TECLAS_FLECHAS[key]
    return None


#teclado
def keyboard(key, x, y):
    from ACTIONS import juego, npcs
    k = key.lower()
    mapeada = _accion_de_tecla(key)

    #PAUSA: todas las teclas son del menú de pausa
    if juego_pausado and estado_escenario != "MENU":
        tecla_pausa(key)

    elif key == b'\x1b':
        # ESC en una partida abre la pausa; en el menú de personajes o en las pantallas finales sale del juego
        if estado_escenario == "MENU" or juego.fase != "JUGANDO":
            # sys.exit() no sirve aquí: dentro de un callback de GLUT la excepción se ignora
            play_sound("salir")
            glutLeaveMainLoop()
        else:
            pausar()

    #MENÚ DE SELECCIÓN: 1 o 2 jugadores, elegir personaje y confirmar
    elif estado_escenario == "MENU":
        if k == b'1':
            cambiar_modo(False)
        elif k == b'2':
            cambiar_modo(True)
        elif mapeada:
            accion(mapeada[0], mapeada[1], True)

    #PANTALLAS FINALES: ENTER acepta, RETROCESO vuelve al menú
    elif juego.fase != "JUGANDO" and key in (b'\r', b'\n'):
        juego.aceptar()
    elif juego.fase != "JUGANDO" and key == b'\x08':
        juego.volver_al_menu()

    #DIÁLOGO: números eligen una opción, RETROCESO cierra; las demás teclas no hacen nada
    elif npcs.abierto() and mapeada is None:
        if b'1' <= k <= b'9':
            npcs.elegir(int(k) - 1)
        elif key == b'\x08':
            npcs.cerrar()

    #JUEGO: movimiento, ataque y hablar de cada jugador (se sueltan en keyboard_up)
    elif mapeada:
        accion(mapeada[0], mapeada[1], True)

    elif k == b'r':
        reiniciar_camara()
    elif k == b'p':
        pausar()

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
        ir_a_escenario(ESCENARIOS[k])

    #OPCIONES
    elif k == b'v':
        alternar_hitboxes()
    elif k == b'k':
        siguiente = (indice_seleccionado + 1) % len(opciones_personaje)
        if dos_jugadores and siguiente == indice_j2:
            siguiente = (siguiente + 1) % len(opciones_personaje)
        cambiar_personaje(opciones_personaje[siguiente])
    elif k == b'l':
        luz.alternar_luz()
        play_sound("click")
    elif k == b'f':
        luz.alternar_sombreado()
        play_sound("click")
    elif k == b'o':
        luz.alternar_sombras()
        play_sound("click")

    glutPostRedisplay()


#soltar una tecla normal
def keyboard_up(key, x, y):
    mapeada = _accion_de_tecla(key)
    if mapeada:
        accion(mapeada[0], mapeada[1], False)


#teclas especiales: flechas, SHIFT/CTRL derechos (acciones del jugador de las flechas) y F1-F3
def special_keys(key, x, y):
    from ACTIONS import juego
    if key in FLECHAS:
        accion(indice_flechas(), FLECHAS[key], True)
    elif key in NIVELES_F and estado_escenario != "MENU" and juego.fase == "JUGANDO":
        ir_a_escenario(NIVELES_F[key])
    glutPostRedisplay()


#soltar una tecla especial
def special_up(key, x, y):
    if key in FLECHAS:
        accion(indice_flechas(), FLECHAS[key], False)


#clic del mouse
def mouse_click(button, state, x, y):
    global last_mouse_x, last_mouse_y, is_mouse_pressed, zoom_z

    # El menú tiene cámara fija: arrastrar o hacer zoom no debe afectar al juego
    if estado_escenario == "MENU" or juego_pausado:
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
    if is_mouse_pressed and not juego_pausado:
        dx = x - last_mouse_x
        dy = y - last_mouse_y

        angle_y += dx * 0.5 * sensibilidad_camara
        angle_x += dy * 0.5 * sensibilidad_camara

        last_mouse_x, last_mouse_y = x, y
        glutPostRedisplay()
