import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_dark_room():
    quad = gluNewQuadric()
    t = time.time()
    
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)
    
    #VACÍO MORADO
    glPushMatrix()
    brillo_vacio = 0.1 + 0.05 * math.sin(t * 2.0)
    glColor3f(brillo_vacio, 0.0, brillo_vacio * 1.5) 
    glTranslatef(0.0, -0.5, 0.0)
    glBegin(GL_QUADS)
    glVertex3f(-15.0, 0.0, -15.0)
    glVertex3f(15.0, 0.0, -15.0)
    glVertex3f(15.0, 0.0, 15.0)
    glVertex3f(-15.0, 0.0, 15.0)
    glEnd()
    glPopMatrix()

    #piso
    glPushMatrix()
    glColor3f(0.08, 0.08, 0.08)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, 10.0)
    glVertex3f(-10.0, 0.0, 10.0)
    glEnd()
    
    #Grietas
    glColor3f(0.02, 0.02, 0.02)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(-10, 11, 2):
        glVertex3f(i, 0.01, -10)
        glVertex3f(i, 0.01, 10)
        glVertex3f(-10, 0.01, i)
        glVertex3f(10, 0.01, i)
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()

    #PAREDES
    # Trasera
    glPushMatrix()
    glColor3f(0.05, 0.05, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(-10.0, 6.0, -10.0)
    glVertex3f(10.0, 6.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glEnd()
    glPopMatrix()
    # Laterales
    glPushMatrix()
    glColor3f(0.04, 0.04, 0.04)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, 10.0)
    glVertex3f(-10.0, 6.0, 10.0)
    glVertex3f(-10.0, 6.0, -10.0)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glVertex3f(10.0, 6.0, -10.0)
    glVertex3f(10.0, 6.0, 10.0)
    glVertex3f(10.0, 0.0, 10.0)
    glEnd()
    glPopMatrix()

    #PUESTAS
    posiciones_puertas = [
        (-9.9, 2.0, 0.0, 90),
        (9.9, 2.0, 0.0, -90),
    ]
    for px, py, pz, rot in posiciones_puertas:
        glPushMatrix()
        glTranslatef(px, py, pz)
        glRotatef(rot, 0, 1, 0)
        glScalef(2.5, 4.0, 0.2)
        glColor3f(0.1, 0.1, 0.1)
        glutSolidCube(1.0)
        glTranslatef(0.0, 0.0, 0.1)
        glScalef(0.8, 0.9, 1.0)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidCube(1.0)
        glPopMatrix()

    #PUERTA MEGA SATÁN
    glPushMatrix()
    glTranslatef(0.0, 3.0, -9.8)
    glColor3f(0.9, 0.7, 0.1)
    glPushMatrix()
    glScalef(4.0, 6.0, 0.4)
    glutSolidCube(1.0)
    glColor3f(0.6, 0.4, 0.0)
    glutWireCube(1.05)
    glPopMatrix()

    #CHAPA
    glPushMatrix()
    glTranslatef(0.0, 0.5, 0.21)
    glColor3f(0.0, 0.0, 0.0)
    gluDisk(quad, 0.0, 0.7, 20, 1)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(-0.5, -1.2, 0.0)
    glVertex3f(0.5, -1.2, 0.0)
    glEnd()
    glPopMatrix()
    glPopMatrix()

    #COFRES
    for cx, cz in [(-4.0, -3.0), (4.0, -3.0), (-4.0, 3.0), (4.0, 3.0)]:
        glPushMatrix()
        glTranslatef(cx, 0.5, cz)
        glColor3f(0.6, 0.1, 0.1)
        glPushMatrix()
        glScalef(1.5, 1.0, 1.2)
        glutSolidCube(1.0)
        glColor3f(0.1, 0.05, 0.05)
        glutWireCube(1.02)
        glPopMatrix()
        glColor3f(0.5, 0.05, 0.05)
        glPushMatrix()
        glTranslatef(0.0, 0.6, 0.0)
        glScalef(1.5, 0.3, 1.2)
        glutSolidCube(1.0)
        glColor3f(0.1, 0.05, 0.05)
        glutWireCube(1.02)
        glPopMatrix()
        #CANDADO
        glColor3f(0.6, 0.6, 0.6)
        glPushMatrix()
        glTranslatef(0.0, 0.4, 0.65)
        glutSolidCube(0.25)
        glPopMatrix()
        
        glPopMatrix()

    glPopMatrix()