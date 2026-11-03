import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

_quad = None

def _quadric():
    global _quad
    if _quad is None:
        _quad = gluNewQuadric()
        gluQuadricDrawStyle(_quad, GLU_FILL)
    return _quad


def draw_axes():
    glBegin(GL_LINES)
    glColor3f(1, 0, 0); glVertex3f(0, 0, 0); glVertex3f(2, 0, 0)
    glColor3f(0, 1, 0); glVertex3f(0, 0, 0); glVertex3f(0, 2, 0)
    glColor3f(0, 0, 1); glVertex3f(0, 0, 0); glVertex3f(0, 0, 2)
    glEnd()


def draw_azazel(expresion="normal", movimiento="reposo", t=0.0):
    glPushAttrib(GL_ALL_ATTRIB_BITS)

    quad = _quadric()
    DEMON_SKIN = (0.09, 0.09, 0.1)
    HORN_COLOR = (0.04, 0.04, 0.04)
    desplazamiento_y = 0.0
    escala_y = 1.0
    brazo_izq_ang_x = 0
    brazo_der_ang_x = 0
    brazo_der_ang_z = 20
    pierna_izq_ang_x = 0
    pierna_der_ang_x = 0
    rotacion_x = 0.0

    frecuencia_aleteo = 5.0

    if movimiento == "caminar":
        frecuencia_aleteo = 12.0
        brazo_izq_ang_x = math.sin(t * 10) * 40
        brazo_der_ang_x = -math.sin(t * 10) * 40
        pierna_izq_ang_x = -math.sin(t * 10) * 40
        pierna_der_ang_x = math.sin(t * 10) * 40
    elif movimiento == "saltar":
        frecuencia_aleteo = 18.0
        desplazamiento_y = abs(math.sin(t * 8)) * 2.0
    elif movimiento == "agacharse":
        frecuencia_aleteo = 2.0
        escala_y = 0.7
        desplazamiento_y = -1.5
    elif movimiento == "saludar":
        frecuencia_aleteo = 6.0
        brazo_der_ang_z = -140 + math.sin(t * 15) * 30
        brazo_der_ang_x = 0
    elif movimiento == "elevar_brazos":
        frecuencia_aleteo = 6.0
        brazo_izq_ang_x = -90 + math.sin(t * 6) * 90
        brazo_der_ang_x = -90 + math.sin(t * 6) * 90
    elif movimiento == "doblar_piernas":
        frecuencia_aleteo = 3.0
        escala_y = 0.85 + math.sin(t * 6) * 0.15
        desplazamiento_y = -0.5 + math.sin(t * 5) * 0.2
    elif movimiento == "inclinarse":
        frecuencia_aleteo = 4.0
        rotacion_x = math.sin(t * 5) * 7.0
    elif movimiento == "flotar":
        frecuencia_aleteo = 25.0
        desplazamiento_y = 3.0 + math.sin(t * 4) * 0.5
        rotacion_x = -45.0
        brazo_izq_ang_x = -180
        brazo_der_ang_x = 0
        pierna_izq_ang_x = 20
        pierna_der_ang_x = 20

    angulo_aleteo = math.sin(t * frecuencia_aleteo) * 25.0

    #CUERPO
    glPushMatrix()
    glTranslatef(0.0, desplazamiento_y, 0.0)
    glRotatef(rotacion_x, 1, 0, 0)
    glScalef(1.0, escala_y, 1.0)

    # CABEZA
    glPushMatrix()
    glTranslatef(0, 4.0, 7.0)
    glScalef(2.8, 2.2, 2.5)
    glColor3f(*DEMON_SKIN)
    glutSolidSphere(1.0, 30, 30)
    glPopMatrix()

    #CUERNOS
    glPushMatrix()
    glTranslatef(-1.7, 5.4, 8.2)
    glRotatef(30, 0, 0, 1)
    glRotatef(-15, 1, 0, 0)
    glColor3f(*HORN_COLOR)
    glutSolidSphere(0.5, 15, 15)
    gluCylinder(quad, 0.5, 0.45, 0.9, 15, 5)
    glTranslatef(0.0, 0.0, 0.9)
    gluDisk(quad, 0.0, 0.45, 15, 1)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.7, 5.4, 8.2)
    glRotatef(-30, 0, 0, 1)
    glRotatef(-15, 1, 0, 0)
    glColor3f(*HORN_COLOR)
    glutSolidSphere(0.55, 15, 15)
    gluCylinder(quad, 0.55, 0.4, 0.9, 15, 5)
    glTranslatef(0.0, 0.2, 0.8)
    glutSolidSphere(0.4, 15, 15)
    glRotatef(-25, 1, 0, 0)
    glutSolidCone(0.4, 1.5, 15, 5)
    glPopMatrix()

    #ALAS
    glDisable(GL_CULL_FACE)

    for lado in [-1, 1]:
        glPushMatrix()
        glTranslatef(1.0 * lado, 1.6, 6.2)
        #ALETEO
        glRotatef(40 * lado + (angulo_aleteo * lado), 0, 1, 0)
        glRotatef(-15, 1, 0, 0)

        glColor3f(0.12, 0.12, 0.14)
        for offset_z in [-0.03, 0.0, 0.03]:
            glPushMatrix()
            glTranslatef(0.0, 0.0, offset_z)
            glNormal3f(0.0, 0.0, 1.0)
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(1.8 * lado, 1.3, -0.2)
            glVertex3f(2.4 * lado, 0.8, -0.3)
            glVertex3f(2.1 * lado, -0.2, -0.2)
            glVertex3f(1.6 * lado, -0.9, -0.1)
            glVertex3f(0.8 * lado, -0.8, 0.0)
            glVertex3f(0.3 * lado, -0.4, 0.0)
            glEnd()
            glPopMatrix()

        glPopMatrix()

    # TORSO
    glPushMatrix()
    glTranslatef(0, 1.2, 7.0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(*DEMON_SKIN)
    gluCylinder(quad, 1.2, 1.2, 1.0, 20, 5)
    glPopMatrix()

    # PIERNAS
    glPushMatrix()
    glTranslatef(-0.6, 0, 7.0)
    glRotatef(-90 + pierna_izq_ang_x, 1, 0, 0)
    glColor3f(*DEMON_SKIN)
    gluCylinder(quad, 0.45, 0.45, 1.2, 20, 5)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.6, 0, 7.0)
    glRotatef(-90 + pierna_der_ang_x, 1, 0, 0)
    glColor3f(*DEMON_SKIN)
    gluCylinder(quad, 0.45, 0.45, 1.2, 20, 5)
    glPopMatrix()

    # BRAZOS
    glPushMatrix()
    glTranslatef(-1.2, 2.0, 7.0)
    glRotatef(-20, 0, 0, 1)
    glRotatef(90 + brazo_izq_ang_x, 1, 0, 0)
    glColor3f(*DEMON_SKIN)
    gluCylinder(quad, 0.3, 0.3, 0.8, 15, 5)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.2, 2.0, 7.0)
    glRotatef(brazo_der_ang_z, 0, 0, 1)
    glRotatef(90 + brazo_der_ang_x, 1, 0, 0)
    glColor3f(*DEMON_SKIN)
    gluCylinder(quad, 0.3, 0.3, 0.8, 15, 5)
    glPopMatrix()

#EXPRESIONES
    if expresion == "normal":
        dibujar_ojos(1.0, 1.0)
        dibujar_boca_normal()

    elif expresion == "feliz":
        dibujar_ojos(1.0, 1.0)
        glPushMatrix()
        glTranslatef(0.0, 3.7, 9.4)
        glRotatef(180, 0, 0, 1)
        glTranslatef(0.0, -3.7, -9.4)
        dibujar_boca_normal()
        glPopMatrix()

    elif expresion == "triste":
        dibujar_ojos(1.0, 0.8)
        glPushMatrix()
        glTranslatef(0.0, 3.7, 9.4)
        glScalef(0.7, 0.7, 0.7)
        glTranslatef(0.0, -3.7, -9.4)
        dibujar_boca_normal()
        glPopMatrix()
        dibujar_lagrimas(t)

    elif expresion == "enojado":
        dibujar_ojos(1.0, 1.0)
        dibujar_cejas_enojo()
        glPushMatrix()
        glTranslatef(0.0, 3.5, 9.4)
        glScalef(1.0, 0.15, 0.5)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidCube(0.8)
        glPopMatrix()

    elif expresion == "asombro":
        dibujar_ojos(1.3, 1.3)
        glPushMatrix()
        glTranslatef(0.0, 3.2, 9.6)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidSphere(0.5, 20, 20)
        glPopMatrix()

    elif expresion == "guiño":
        dibujar_ojos_guino()
        dibujar_boca_normal()

    elif expresion == "miedo":
        dibujar_ojos(0.7, 0.7)
        dibujar_cejas_miedo()
        glPushMatrix()
        glTranslatef(math.sin(t*50)*0.05, 3.4, 9.5)
        glScalef(0.8, 0.4, 0.5)
        glColor3f(0, 0, 0)
        glutSolidSphere(0.4, 15, 15)
        glPopMatrix()

    glPopMatrix()
    glPopAttrib()


def dibujar_ojos(escala_x, escala_y):
    glColor3f(0.85, 0.0, 0.0) # Rojo
    for x in [-1.1, 1.1]:
        glPushMatrix()
        glTranslatef(x, 4.2, 9.2)
        glScalef(escala_x, escala_y, 1.0)
        glutSolidSphere(0.75, 20, 20)
        glPopMatrix()

    # Brillos
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(-1.3, 4.5, 9.7)
    glutSolidSphere(0.25, 15, 15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.9, 4.5, 9.7)
    glutSolidSphere(0.25, 15, 15)
    glPopMatrix()


def dibujar_ojos_guino():
    glColor3f(0.85, 0.0, 0.0)
    # Ojo Izquierdo normal
    glPushMatrix()
    glTranslatef(-1.1, 4.2, 9.2)
    glutSolidSphere(0.75, 20, 20)
    glPopMatrix()
    # Ojo Derecho (Guiño)
    glPushMatrix()
    glTranslatef(1.1, 4.2, 9.2)
    glScalef(1.0, 0.1, 1.0)
    glutSolidSphere(0.75, 20, 20)
    glPopMatrix()
    glColor3f(1.0, 1.0, 1.0)
    glPushMatrix()
    glTranslatef(-1.3, 4.5, 9.7)
    glutSolidSphere(0.25, 15, 15)
    glPopMatrix()


def dibujar_boca_normal():
    quad = _quadric()
    glPushMatrix()
    glTranslatef(0.0, 3.7, 9.4)
    glPushMatrix()
    glEnable(GL_CLIP_PLANE0)
    glClipPlane(GL_CLIP_PLANE0, (0.0, 1.0, 0.0, 0.0))
    glColor3f(0.0, 0.0, 0.0)
    glutSolidSphere(0.45, 20, 20)
    glDisable(GL_CLIP_PLANE0)
    glPopMatrix()
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    glColor3f(0.0, 0.0, 0.0)
    gluDisk(quad, 0.0, 0.45, 20, 1)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, 0.06, 0.4)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.0, 0.15, 1.0)
    glColor3f(1.0, 1.0, 1.0)
    gluCylinder(quad, 0.34, 0.26, 0.12, 20, 5)
    gluDisk(quad, 0.0, 0.34, 20, 1)
    glPopMatrix()
    glPopMatrix()


def dibujar_cejas_enojo():
    glColor3f(0.0, 0.0, 0.0)
    # Ceja Izquierda
    glPushMatrix()
    glTranslatef(-1.1, 5.2, 9.5)
    glRotatef(-30, 0, 0, 1)
    glScalef(0.8, 0.15, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    # Ceja Derecha
    glPushMatrix()
    glTranslatef(1.1, 5.2, 9.5)
    glRotatef(30, 0, 0, 1)
    glScalef(0.8, 0.15, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()


def dibujar_cejas_miedo():
    glColor3f(0.0, 0.0, 0.0)
    # Cejas caídas
    glPushMatrix()
    glTranslatef(-1.1, 5.1, 9.5)
    glRotatef(20, 0, 0, 1)
    glScalef(0.8, 0.15, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(1.1, 5.1, 9.5)
    glRotatef(-20, 0, 0, 1)
    glScalef(0.8, 0.15, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()


def dibujar_lagrimas(t):
    glColor3f(0.3, 0.75, 0.95)
    anim = math.sin(t * 5) * 0.3

    glPushMatrix()
    glTranslatef(-1.3, 3.3 + anim, 9.3)
    glutSolidSphere(0.35, 15, 15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-1.4, 2.5 + anim, 9.1)
    glutSolidSphere(0.25, 15, 15)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(1.3, 3.3 + anim, 9.3)
    glutSolidSphere(0.35, 15, 15)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(1.4, 2.5 + anim, 9.1)
    glutSolidSphere(0.25, 15, 15)
    glPopMatrix()
