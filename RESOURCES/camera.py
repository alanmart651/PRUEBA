# camera.py
# ============================================================
# CONTROL DE CÁMARA
# ============================================================

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# ============================================================
# POSICIÓN INICIAL
# ============================================================

CAMERA_START_POSITION = [0.0, 1.5, 6.0]

cam_pos = CAMERA_START_POSITION.copy()


# ============================================================
# ROTACIÓN
# ============================================================

yaw = 0.0
pitch = 0.0


# ============================================================
# CONFIGURACIÓN
# ============================================================

cam_speed = 0.2
mouse_sensitivity = 0.2

zoom_speed = 0.5

min_zoom = 1.0
max_zoom = 30.0


# ============================================================
# ESTADO DEL MOUSE
# ============================================================

mouse_down = False

last_mouse_x = 0
last_mouse_y = 0


# ============================================================
# APLICAR CÁMARA
# ============================================================

def apply_camera():
    """
    Aplica la transformación de la cámara
    antes de dibujar la escena.
    """

    glRotatef(-pitch, 1.0, 0.0, 0.0)

    glRotatef(-yaw, 0.0, 1.0, 0.0)

    glTranslatef(
        -cam_pos[0],
        -cam_pos[1],
        -cam_pos[2]
    )


# ============================================================
# DIRECCIÓN HACIA ADELANTE
# ============================================================

def get_forward():
    """
    Obtiene el vector horizontal hacia adelante
    según el yaw actual.
    """

    angle = math.radians(yaw)

    return [
        math.sin(angle),
        0.0,
        -math.cos(angle)
    ]


# ============================================================
# DIRECCIÓN DERECHA
# ============================================================

def get_right():
    """
    Obtiene el vector horizontal hacia la derecha
    según el yaw actual.
    """

    angle = math.radians(yaw)

    return [
        math.cos(angle),
        0.0,
        math.sin(angle)
    ]


# ============================================================
# MOVIMIENTO HACIA ADELANTE
# ============================================================

def move_forward():

    forward = get_forward()

    cam_pos[0] += forward[0] * cam_speed
    cam_pos[2] += forward[2] * cam_speed


# ============================================================
# MOVIMIENTO HACIA ATRÁS
# ============================================================

def move_backward():

    forward = get_forward()

    cam_pos[0] -= forward[0] * cam_speed
    cam_pos[2] -= forward[2] * cam_speed


# ============================================================
# MOVIMIENTO HACIA LA IZQUIERDA
# ============================================================

def move_left():

    right = get_right()

    cam_pos[0] -= right[0] * cam_speed
    cam_pos[2] -= right[2] * cam_speed


# ============================================================
# MOVIMIENTO HACIA LA DERECHA
# ============================================================

def move_right():

    right = get_right()

    cam_pos[0] += right[0] * cam_speed
    cam_pos[2] += right[2] * cam_speed


# ============================================================
# MOVIMIENTO VERTICAL
# ============================================================

def move_up():

    cam_pos[1] += cam_speed


def move_down():

    cam_pos[1] -= cam_speed

    # Evitar que la cámara baje demasiado
    if cam_pos[1] < 0.2:
        cam_pos[1] = 0.2


# ============================================================
# MANEJO DE TECLAS ESPECIALES
# ============================================================

def handle_special_keys(key, x, y):

    if key == GLUT_KEY_UP:
        move_forward()

    elif key == GLUT_KEY_DOWN:
        move_backward()

    elif key == GLUT_KEY_LEFT:
        move_left()

    elif key == GLUT_KEY_RIGHT:
        move_right()

    elif key == GLUT_KEY_PAGE_UP:
        move_up()

    elif key == GLUT_KEY_PAGE_DOWN:
        move_down()

    glutPostRedisplay()


# ============================================================
# TECLAS WASD
# ============================================================

def handle_key(key):

    # Convertir mayúsculas a minúsculas
    key = key.lower()

    if key == b'w':
        move_forward()

    elif key == b's':
        move_backward()

    elif key == b'a':
        move_left()

    elif key == b'd':
        move_right()

    elif key == b'q':
        move_up()

    elif key == b'e':
        move_down()

    else:
        return False

    glutPostRedisplay()

    return True


# ============================================================
# MOUSE - BOTONES
# ============================================================

def mouse(button, button_state, x, y):

    global mouse_down
    global last_mouse_x
    global last_mouse_y

    # --------------------------------------------------------
    # BOTÓN IZQUIERDO
    # --------------------------------------------------------

    if button == GLUT_LEFT_BUTTON:

        if button_state == GLUT_DOWN:

            mouse_down = True

            last_mouse_x = x
            last_mouse_y = y

        else:

            mouse_down = False

    # --------------------------------------------------------
    # RUEDA DEL MOUSE
    # --------------------------------------------------------

    elif button == 3:

        zoom_in()

    elif button == 4:

        zoom_out()

    glutPostRedisplay()


# ============================================================
# MOVIMIENTO DEL MOUSE
# ============================================================

def motion(x, y):

    global yaw
    global pitch
    global last_mouse_x
    global last_mouse_y

    if not mouse_down:
        return

    dx = x - last_mouse_x
    dy = y - last_mouse_y

    yaw += dx * mouse_sensitivity

    pitch += dy * mouse_sensitivity

    # Limitar rotación vertical
    pitch = max(-89.0, min(89.0, pitch))

    last_mouse_x = x
    last_mouse_y = y

    glutPostRedisplay()


# ============================================================
# ZOOM HACIA DENTRO
# ============================================================

def zoom_in():

    forward = get_forward()

    cam_pos[0] += forward[0] * zoom_speed
    cam_pos[2] += forward[2] * zoom_speed

    limit_zoom()


# ============================================================
# ZOOM HACIA FUERA
# ============================================================

def zoom_out():

    forward = get_forward()

    cam_pos[0] -= forward[0] * zoom_speed
    cam_pos[2] -= forward[2] * zoom_speed

    limit_zoom()


# ============================================================
# LIMITAR ZOOM
# ============================================================

def limit_zoom():

    distance = math.sqrt(
        cam_pos[0] ** 2 +
        cam_pos[2] ** 2
    )

    if distance < min_zoom:

        if distance > 0:
            factor = min_zoom / distance

            cam_pos[0] *= factor
            cam_pos[2] *= factor

    elif distance > max_zoom:

        factor = max_zoom / distance

        cam_pos[0] *= factor
        cam_pos[2] *= factor


# ============================================================
# REINICIAR CÁMARA
# ============================================================

def reset_camera():

    global cam_pos
    global yaw
    global pitch
    global mouse_down

    cam_pos = CAMERA_START_POSITION.copy()

    yaw = 0.0
    pitch = 0.0

    mouse_down = False

    glutPostRedisplay()