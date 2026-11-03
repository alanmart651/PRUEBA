import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_planetarium_room():
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    t = time.time()
    quad = gluNewQuadric()

    #PAREDES
    color_fondo = (0.05, 0.05, 0.1)
    
    # Pared Trasera
    glColor3f(*color_fondo)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 6, -10); glVertex3f(10, 6, -10); glVertex3f(10, 0, -10)
    glEnd()
    
    # Paredes Laterales
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 6, -10); glVertex3f(-10, 6, 10); glVertex3f(-10, 0, 10)
    glVertex3f(10, 0, -10); glVertex3f(10, 6, -10); glVertex3f(10, 6, 10); glVertex3f(10, 0, 10)
    glEnd()
    glPointSize(2.0)
    glBegin(GL_POINTS)
    for i in range(40):
        px = (math.sin(i * 12.3) * 10)
        py = (math.cos(i * 7.7) * 3) + 3
        pz = (math.sin(i * 4.5) * 10)
        
        brillo = 0.5 + 0.5 * math.sin(t * 3.0 + i)
        glColor3f(brillo, brillo, brillo + 0.2)
        if abs(px) > 9.8 or abs(pz) > 9.8:
            glVertex3f(px, py, pz)
    glEnd()

    #PISO
    glColor3f(0.15, 0.2, 0.35)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(10, 0, -10); glVertex3f(10, 0, 10); glVertex3f(-10, 0, 10)
    glEnd()
    glColor3f(0.2, 0.25, 0.45)
    glPushMatrix()
    glTranslatef(0.0, 0.01, 0.0)
    glBegin(GL_QUADS)
    for i in range(-20, 20, 4):
        glVertex3f(i, 0, -10)
        glVertex3f(i+2, 0, -10)
        glVertex3f(i+2+20, 0, 10)
        glVertex3f(i+20, 0, 10)
    glEnd()
    glPopMatrix()

    glColor3f(0.6, 0.9, 0.8) 
    glLineWidth(4.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-9.5, 0.02, -9.5); glVertex3f(9.5, 0.02, -9.5)
    glVertex3f(9.5, 0.02, 9.5); glVertex3f(-9.5, 0.02, 9.5)
    glEnd()
    glLineWidth(1.0)

    glPointSize(3.0)
    glBegin(GL_POINTS)
    for i in range(20):
        px = math.sin(i * 3.1) * 8.0
        pz = math.cos(i * 5.2) * 8.0
        brillo = 0.6 + 0.4 * math.sin(t * 2.0 + i)
        glColor3f(brillo, brillo + 0.2, 1.0)
        glVertex3f(px, 0.02, pz)
    glEnd()

    #PEDESTALES
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    
    glColor3f(0.25, 0.25, 0.3)
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    gluCylinder(quad, 0.8, 0.7, 0.5, 15, 5)
    glTranslatef(0.0, 0.0, 0.5)
    gluDisk(quad, 0.0, 0.7, 15, 1)
    glPopMatrix()

    # Ítem flotante
    flote = math.sin(t * 3.0) * 0.2
    glTranslatef(0.0, 1.5 + flote, 0.0)
    glRotatef(t * 40.0, 0, 1, 0) 
    
    # Esfera del planeta
    glColor3f(0.8, 0.5, 0.3)
    glutSolidSphere(0.4, 20, 20)
    
    # Anillo del planeta
    glColor3f(0.9, 0.8, 0.5)
    glPushMatrix()
    glRotatef(30, 1, 0, 0)
    glScalef(1.0, 1.0, 0.05)
    glutSolidTorus(0.08, 0.6, 10, 30)
    glPopMatrix()
    
    glPopMatrix()

    #FOGATAS
    posiciones_fuego = [(-4.0, 0.0), (4.0, 0.0)]
    for i, (fx, fz) in enumerate(posiciones_fuego):
        glPushMatrix()
        glTranslatef(fx, 0.2, fz)
        
        # Leños de madera
        glColor3f(0.2, 0.15, 0.1)
        glPushMatrix(); glRotatef(45, 0, 1, 0); glScalef(1.0, 0.2, 0.3); glutSolidCube(1.0); glPopMatrix()
        glPushMatrix(); glRotatef(-45, 0, 1, 0); glScalef(1.0, 0.2, 0.3); glutSolidCube(1.0); glPopMatrix()
        
        # Fuego Azul Animado
        escala_fuego = 1.0 + abs(math.sin(t * 12.0 + i)) * 0.2
        glPushMatrix()
        glTranslatef(0.0, 0.8, 0.0)
        glScalef(0.6 * escala_fuego, 1.2 * escala_fuego, 0.6 * escala_fuego)
        
        # Color azul místico oscilante
        brillo_fuego = abs(math.sin(t * 15.0 + i))
        glColor3f(0.1, 0.5 + (brillo_fuego * 0.3), 1.0) 
        
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(1.0, 1.0, 10, 5)
        glPopMatrix()
        
        glPopMatrix()

    #PUERTA
    glPushMatrix()
    glTranslatef(0.0, 2.0, -9.9)
    glColor3f(0.1, 0.15, 0.2) 
    glPushMatrix()
    glScalef(2.5, 4.0, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Hueco negro
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0.0, -0.2, 0.11)
    glScalef(1.8, 3.6, 0.1)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glColor3f(0.2, 0.3, 0.4)
    glPushMatrix()
    glTranslatef(0.0, 2.0, 0.1)
    glutSolidSphere(0.5, 15, 15)
    glColor3f(0.6, 0.8, 1.0)
    glTranslatef(-0.1, 0.1, 0.3)
    glutSolidSphere(0.3, 10, 10)
    glPopMatrix()

    glPopMatrix()

    glPopMatrix()