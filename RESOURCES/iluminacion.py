import math
from OpenGL.GL import *

luz_activa = True
sombreado_suave = True
sombras_activas = True


#configuración de iluminación
def configurar_iluminacion_base():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (0.35, 0.35, 0.35, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 48.0)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.18, 0.18, 0.20, 1.0))
    glLightModeli(GL_LIGHT_MODEL_LOCAL_VIEWER, GL_TRUE)
    glLightModeli(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


#latido del miocardio (0 a 1): sincroniza la luz, el corazón y los vasos
def pulso_latido(t):
    return abs(math.sin(t * 4.0))


# Atmósfera de cada nivel: luz ambiente global, ambiente y difusa de la luz principal
ATMOSFERA = {
    0: {"ambiente": (0.30, 0.10, 0.10), "amb0": (0.18, 0.08, 0.07), "difusa": (1.00, 0.72, 0.62)},
    1: {"ambiente": (0.06, 0.14, 0.24), "amb0": (0.05, 0.12, 0.20), "difusa": (0.45, 0.75, 1.00)},
    2: {"ambiente": (0.14, 0.20, 0.07), "amb0": (0.12, 0.18, 0.06), "difusa": (1.00, 0.93, 0.62)},
}


#aplicar luces (foco = posición x, z del jugador para la luz focalizada del vaso)
def aplicar_luces(t, escenario, foco=None):
    glShadeModel(GL_SMOOTH if sombreado_suave else GL_FLAT)

    if not luz_activa:
        glDisable(GL_LIGHTING)
        return

    glEnable(GL_LIGHTING)
    atm = ATMOSFERA.get(escenario)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (*(atm["ambiente"] if atm else (0.18, 0.18, 0.20)), 1.0))

    # Luz principal
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 16.0, 8.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (*(atm["amb0"] if atm else (0.15, 0.15, 0.15)), 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (*(atm["difusa"] if atm else (0.85, 0.80, 0.75)), 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.90, 0.90, 0.90, 1.0))

    glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 180.0)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.04)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.004)

    if escenario == 0:
        # Corazón: luz roja que late
        pulso = 0.55 + 0.45 * pulso_latido(t)
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (0.0, 7.2, 0.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.90 * pulso, 0.15 * pulso, 0.20 * pulso, 1.0))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (0.80 * pulso, 0.20 * pulso, 0.20 * pulso, 1.0))
    elif escenario == 1:
        # Vaso sanguíneo: foco azul-cian que acompaña al jugador
        fx_, fz_ = foco if foco else (0.0, 0.0)
        k = 0.85 + 0.15 * math.sin(t * 2.0)
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (fx_, 14.0, fz_ + 3.0, 1.0))
        glLightfv(GL_LIGHT1, GL_SPOT_DIRECTION, (0.0, -1.0, -0.25))
        glLightf(GL_LIGHT1, GL_SPOT_CUTOFF, 42.0)
        glLightf(GL_LIGHT1, GL_SPOT_EXPONENT, 8.0)
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.01)
        glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.0)
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.25 * k, 0.95 * k, 1.00 * k, 1.0))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (0.70 * k, 1.00 * k, 1.00 * k, 1.0))
    elif escenario == 2:
        # Ganglio linfático: luz dorada que respira despacio
        k = 0.65 + 0.35 * math.sin(t * 1.5) ** 2
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, (0.0, 9.0, 0.0, 1.0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.0, 0.0, 0.0, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (1.00 * k, 0.85 * k, 0.30 * k, 1.0))
        glLightfv(GL_LIGHT1, GL_SPECULAR, (1.00 * k, 0.95 * k, 0.60 * k, 1.0))
        glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.02)
    else:
        glDisable(GL_LIGHT1)


#sombra circular
def dibujar_sombra(x, z, radio, altura=0.0):
    if not sombras_activas:
        return

    factor = max(0.25, 1.0 - altura * 0.15)
    con_luz = glIsEnabled(GL_LIGHTING)
    glDisable(GL_LIGHTING)

    glColor4f(0.0, 0.0, 0.0, 0.40 * factor)
    glBegin(GL_TRIANGLE_FAN)
    glVertex3f(x, 0.03, z)
    for grados in range(0, 361, 20):
        a = math.radians(grados)
        r = radio * (0.6 + 0.4 * factor)
        glVertex3f(x + math.cos(a) * r, 0.03, z + math.sin(a) * r)
    glEnd()

    if con_luz:
        glEnable(GL_LIGHTING)


#alternar luz
def alternar_luz():
    global luz_activa
    luz_activa = not luz_activa


#alternar sombreado plano
def alternar_sombreado():
    global sombreado_suave
    sombreado_suave = not sombreado_suave


#alternar sombras
def alternar_sombras():
    global sombras_activas
    sombras_activas = not sombras_activas
