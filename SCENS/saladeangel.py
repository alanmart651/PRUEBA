from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import time
import math


def draw_angel_room():
    quad = gluNewQuadric()
    t = time.time()
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)
    
    #PISO
    glPushMatrix()
    glColor3f(0.15, 0.2, 0.25)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, 10.0)
    glVertex3f(-10.0, 0.0, 10.0)
    glEnd()
    
    glColor3f(0.1, 0.15, 0.2)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(-10, 11, 2):
        glVertex3f(i, 0.01, -10)
        glVertex3f(i, 0.01, 10)
        glVertex3f(-10, 0.01, i)
        glVertex3f(10, 0.01, i)
    glEnd()
    glLineWidth(1.0)
    
    # Circulo
    glPushMatrix()
    glTranslatef(0.0, 0.02, -2.0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.12, 0.16, 0.2)
    gluDisk(quad, 0.0, 4.5, 30, 1)
    glColor3f(0.08, 0.1, 0.15)
    gluDisk(quad, 4.5, 4.8, 30, 1)
    glPopMatrix()
    glPopMatrix()

    #PAREDES
    # PARED ATRAS
    glPushMatrix()
    glColor3f(0.1, 0.15, 0.2)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(-10.0, 6.0, -10.0)
    glVertex3f(10.0, 6.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glEnd()
    glPopMatrix()

    #PAREDES LATERALES
    glPushMatrix()
    glColor3f(0.08, 0.12, 0.18)
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
    
    #COLUMNAS
    for px in [-9.5, 9.5]:
        for pz in [-9.5, 9.5]:
            glPushMatrix()
            glTranslatef(px, 0.0, pz)
            glRotatef(-90, 1, 0, 0)
            glColor3f(0.12, 0.16, 0.22)
            gluCylinder(quad, 0.8, 0.8, 6.0, 15, 5)
            glPopMatrix()

    # Puerta Trasera
    glPushMatrix()
    glTranslatef(0.0, 2.0, -9.9)
    glScalef(2.5, 4.0, 0.2)
    glColor3f(2, 2, 2)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Cruz
    glPushMatrix()
    glTranslatef(0.0, 5.0, -9.8)
    glColor3f(0.6, 0.6, 0.6)
    glPushMatrix()
    glScalef(0.4, 1.5, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0.0, 0.2, 0.0)
    glScalef(1.2, 0.4, 0.2)
    glutSolidCube(1.0)
    glPopMatrix()
    glPopMatrix()
    
    # Vitrales
    for wx in [-6.0, 6.0]:
        glPushMatrix()
        glTranslatef(wx, 3.5, -9.9)
        glColor3f(0.9, 0.6, 0.1)
        glScalef(1.2, 2.5, 0.1)
        glutSolidCube(1.0)
        glColor3f(0.1, 0.1, 0.1)
        glutWireCube(1.05)
        glPopMatrix()

    #ÍTEMS FLOTANTES
    for x in [-3.5, 3.5]:
        glPushMatrix()
        glTranslatef(x, 0.0, -2.0)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.35, 0.3, 0.3)
        gluCylinder(quad, 1.0, 0.8, 0.8, 15, 5)
        glTranslatef(0.0, 0.0, 0.8)
        glColor3f(0.3, 0.25, 0.25)
        gluDisk(quad, 0.0, 0.8, 15, 1)
        glPopMatrix()
        
        glPushMatrix()
        altura = 1.6 + 0.2 * math.sin(t * 3.0 + x)
        glTranslatef(0.0, altura, 0.0)
        glRotatef(t * 60.0, 0, 1, 0)
        
        if x < 0:
            glColor3f(0.3, 0.6, 1.0)
            glutSolidSphere(0.4, 15, 15)
        else:
            glColor3f(1.0, 0.8, 0.1)
            glutSolidCube(0.6)
            glColor3f(1.0, 1.0, 1.0)
            glutWireCube(0.62)
            
        glPopMatrix()
        glPopMatrix()


    #FUEGO
    for x in [-8.5, 8.5]:
        glPushMatrix()
        glTranslatef(x, 0.0, -8.5)
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.2, 0.2, 0.2)
        gluCylinder(quad, 0.7, 0.7, 0.5, 10, 2)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.0, 0.5, 0.0)
        escala_y = 1.0 + 0.25 * math.sin(t * 6.0 + x) 
        escala_xz = 1.0 + 0.1 * math.cos(t * 12.0 + x)
        glScalef(escala_xz, escala_y, escala_xz)
        glRotatef(-90, 1, 0, 0)
        glRotatef(t * 50.0, 0, 0, 1) 
        
        glColor3f(0.2, 0.6, 1.0)
        glutSolidCone(0.6, 2.0, 3, 1) 
        glTranslatef(0.0, 0.0, 0.1)
        glColor3f(0.7, 0.9, 1.0)
        glutSolidCone(0.3, 1.0, 3, 1)
        glPopMatrix()
        glPopMatrix()

    #ESTATUA DEL ÁNGEL
    glPushMatrix()
    glTranslatef(0.0, 0.0, -4.5) 
    glScalef(0.75, 0.75, 0.75) 
    
    # Cuerpo
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.9, 0.9, 0.9)
    gluCylinder(quad, 1.8, 1.0, 3.5, 20, 5)
    glPopMatrix()
    
    # Cabeza
    glPushMatrix()
    glTranslatef(0.0, 4.2, 0.0)
    glColor3f(0.9, 0.8, 0.7)
    glutSolidSphere(1.2, 20, 20)
    glPopMatrix()
    
    # Alas
    for rot_z, pos_x in [(20, -1.8), (-20, 1.8)]:
        glPushMatrix()
        glTranslatef(pos_x, 3.0, -0.5)
        glRotatef(rot_z, 0, 0, 1)
        glScalef(1.5, 2.5, 0.2)
        glColor3f(0.8, 0.9, 1.0)
        glutSolidSphere(0.8, 15, 15)
        glPopMatrix()
        
    glPopMatrix()
    
    glPopMatrix() # Fin escalado habitacion

    #Alfombra, Ventanas y Luz
    
    glPushMatrix()
    glTranslatef(0.0, 0.04, -5.5)
    glColor3f(0.4, 0.05, 0.05)
    glBegin(GL_QUADS)
    glVertex3f(-1.5, 0.0, -4.5)
    glVertex3f(1.5, 0.0, -4.5)
    glVertex3f(1.5, 0.0, 3.5)
    glVertex3f(-1.5, 0.0, 3.5)
    glEnd()
    glColor3f(0.8, 0.6, 0.1)
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-1.5, 0.0, -4.5)
    glVertex3f(1.5, 0.0, -4.5)
    glVertex3f(1.5, 0.0, 3.5)
    glVertex3f(-1.5, 0.0, 3.5)
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()

  
    #RALLOS Y VENTANAS
    for lado in [-17.9, 17.9]:
        glPushMatrix()
        glTranslatef(lado, 7.0, -4.0)
        if lado < 0:
            glRotatef(90, 0, 1, 0)
        else:
            glRotatef(-90, 0, 1, 0)
        
        glColor3f(0.9, 0.8, 0.2)
        glScalef(3.0, 4.5, 0.2)
        glutSolidCube(1.0)
        glColor3f(0.1, 0.1, 0.1)
        glutWireCube(1.05)
        glPopMatrix()
        
        glPushMatrix()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        
        glColor4f(1.0, 0.9, 0.5, 0.15) 
        glBegin(GL_POLYGON)
        if lado < 0:
            glVertex3f(-17.8, 9.0, -5.4)
            glVertex3f(-17.8, 5.0, -2.6)
            glVertex3f(-12.0, 0.05, -2.6)
            glVertex3f(-12.0, 0.05, -5.4)
        else:
            glVertex3f(17.8, 9.0, -5.4) 
            glVertex3f(17.8, 5.0, -2.6) 
            glVertex3f(12.0, 0.05, -2.6)
            glVertex3f(12.0, 0.05, -5.4)
        glEnd()
        
        # GL_BLEND queda activo: las sombras de todas las salas dependen de él
        glDepthMask(GL_TRUE)
        glPopMatrix()