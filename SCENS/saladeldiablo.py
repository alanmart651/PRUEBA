import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_devil_room():
    quad = gluNewQuadric()
    t = time.time()
    
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)
    
    #PISO Y PENTAGRAMA
    glPushMatrix()
    glColor3f(0.08, 0.08, 0.09)
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glVertex3f(10.0, 0.0, 10.0)
    glVertex3f(-10.0, 0.0, 10.0)
    glEnd()
    glColor3f(0.04, 0.04, 0.05)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(-10, 11, 2):
        glVertex3f(i, 0.01, -10)
        glVertex3f(i, 0.01, 10)
        glVertex3f(-10, 0.01, i)
        glVertex3f(10, 0.01, i)
    glEnd()
    glLineWidth(1.0)

#fuego
    for x in [-8.5, 8.5]:
            glPushMatrix()
            glTranslatef(x, 0.0, -8.5)
            
            glPushMatrix()
            glRotatef(-90, 1, 0, 0)
            glColor3f(0.2, 0.2, 0.2)
            gluCylinder(quad, 0.7, 0.7, 0.5, 10, 2)
            glPopMatrix()
            
            # Llama
            glPushMatrix()
            glTranslatef(0.0, 0.5, 0.0)
            escala_y = 1.0 + 0.25 * math.sin(t * 6.0 + x) 
            escala_xz = 1.0 + 0.1 * math.cos(t * 12.0 + x)
            glScalef(escala_xz, escala_y, escala_xz)
            glRotatef(-90, 1, 0, 0)
            glRotatef(t * 50.0, 0, 0, 1) 
            
            glColor3f(0.47, 0.02, 0.02)
            glutSolidCone(0.6, 2.0, 3, 1) 
            glTranslatef(0.0, 0.0, 0.1)
            glColor3f(0.47, 0.02, 0.02)
            glutSolidCone(0.3, 1.0, 3, 1)
            glPopMatrix()
            glPopMatrix()


    #columnas
    for px in [-9.5, 9.5]:
            for pz in [-9.5, 9.5]:
                glPushMatrix()
                glTranslatef(px, 0.0, pz)
                glRotatef(-90, 1, 0, 0)
                glColor3f(0.0, 0.0, 0.0)
                gluCylinder(quad, 0.8, 0.8, 6.0, 15, 5)
                glPopMatrix()
                
    # Círculo de invocacion
    glPushMatrix()
    glTranslatef(0.0, 0.02, -2.0)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.15, 0.0, 0.0)
    gluDisk(quad, 3.8, 4.2, 30, 1)

    # Estrella interior
    glBegin(GL_LINE_LOOP)
    for i in range(5):
        angle = i * (4.0 * math.pi / 5.0) - (math.pi / 2.0)
        glVertex3f(math.cos(angle) * 3.8, math.sin(angle) * 3.8, 0.01)
    glEnd()
    glPopMatrix()
    glPopMatrix()

    #PAREDES
    glColor3f(0.05, 0.05, 0.06)
    # Trasera
    glPushMatrix()
    glBegin(GL_QUADS)
    glVertex3f(-10.0, 0.0, -10.0)
    glVertex3f(-10.0, 6.0, -10.0)
    glVertex3f(10.0, 6.0, -10.0)
    glVertex3f(10.0, 0.0, -10.0)
    glEnd()
    glPopMatrix()
    # Laterales
    glPushMatrix()
    glColor3f(0.04, 0.04, 0.05)
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

    #PUERTA DEL DIABLO
    glPushMatrix()
    glTranslatef(0.0, 2.0, -9.9)
    glScalef(2.5, 4.0, 0.2)
    glColor3f(0.0, 0.0, 0.0)
    glutSolidCube(1.0)
    glColor3f(0.3, 0.05, 0.05)
    glutWireCube(1.05)
    glPopMatrix()

    #CABEZAS DE GÁRGOLA
    for x in [-5.0, 5.0]:
        glPushMatrix()
        glTranslatef(x, 4.0, -9.5)
        # Cabeza
        glColor3f(0.1, 0.1, 0.1)
        glutSolidSphere(0.8, 15, 15)
        # Cuernos
        for cx in [-0.5, 0.5]:
            glPushMatrix()
            glTranslatef(cx, 0.4, 0.2)
            glRotatef(-90, 1, 0, 0)
            glRotatef(-20 if cx < 0 else 20, 0, 1, 0)
            glColor3f(0.05, 0.05, 0.05)
            glutSolidCone(0.2, 0.8, 10, 2)
            glPopMatrix()
        # Ojos
        brillo = 0.8 + 0.2 * math.sin(t * 5.0)
        glColor3f(1.0 * brillo, 0.5 * brillo, 0.0) 
        for ox in [-0.3, 0.3]:
            glPushMatrix()
            glTranslatef(ox, 0.1, 0.7)
            glutSolidSphere(0.15, 10, 10)
            glPopMatrix()
        glPopMatrix()

 #Ítems y Pedestales
    posiciones_items = [(-3.0, "pacto"), (3.0, "pacto"), (0.0, "corazon")]
    for px, tipo in posiciones_items:
        glPushMatrix()
        glTranslatef(px, 0.0, -2.0 if tipo == "pacto" else 0.0)
        
        # Pedestales pactos
        if tipo == "pacto":
            glPushMatrix()
            glRotatef(-90, 1, 0, 0)
            glColor3f(0.08, 0.08, 0.08)
            gluCylinder(quad, 0.8, 0.5, 0.8, 15, 5)
            glTranslatef(0.0, 0.0, 0.8)
            glColor3f(0.15, 0.1, 0.1)
            gluDisk(quad, 0.0, 0.5, 15, 1)
            glPopMatrix()

        # Animación de flotar
        glPushMatrix()
        altura = 1.4 + 0.15 * math.sin(t * 3.0 + px)
        if tipo == "corazon": altura -= 0.6
        glTranslatef(0.0, altura, 0.0)
        glRotatef(t * 50.0, 0, 1, 0)
        
        if tipo == "pacto":
            # Item rojo
            glColor3f(0.6, 0.0, 0.0)
            glutSolidCube(0.6)
            glColor3f(0.9, 0.2, 0.2)
            glutWireCube(0.62)
        else:
            # Corazón
            glColor3f(0.05, 0.05, 0.05)
            glScalef(1.0, 1.0, 0.5)
            glutSolidSphere(0.4, 15, 15)
            # Aura morada
            glColor3f(0.4, 0.0, 0.6)
            glutWireSphere(0.42, 10, 10)
            
        glPopMatrix()
        glPopMatrix()

    #ESTATUA DE SATÁN
    glPushMatrix()
    glTranslatef(0.0, 0.0, -4.5) 
    glScalef(0.75, 0.75, 0.75) 
    
    # Cuerpo 
    glPushMatrix()
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.12, 0.12, 0.12)
    gluCylinder(quad, 2.0, 1.2, 3.5, 20, 5)
    glPopMatrix()
    
    # Cabeza
    glPushMatrix()
    glTranslatef(0.0, 4.2, 0.0)
    glColor3f(0.12, 0.12, 0.12)
    glutSolidSphere(1.2, 20, 20)
    
    # Cuernos
    for angulo, pos_x in [(30, -0.8), (-30, 0.8)]:
        glPushMatrix()
        glTranslatef(pos_x, 0.8, 0.0)
        glRotatef(-90, 1, 0, 0)
        glRotatef(angulo, 0, 1, 0)
        glColor3f(0.08, 0.08, 0.08)
        glutSolidCone(0.4, 1.8, 15, 5)
        glPopMatrix()
        
    # Ojos
    glColor3f(1.0, 0.0, 0.0)
    for ox in [-0.4, 0.4]:
        glPushMatrix()
        glTranslatef(ox, 0.2, 1.1)
        glutSolidSphere(0.2, 10, 10)
        glPopMatrix()
    glPopMatrix()
    
    # Alas puntiagudas
    for rot_z, pos_x in [(30, -1.8), (-30, 1.8)]:
        glPushMatrix()
        glTranslatef(pos_x, 3.5, -0.5)
        glRotatef(rot_z, 0, 0, 1)
        glScalef(2.0, 1.5, 0.2)
        glColor3f(0.08, 0.08, 0.08)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(-1.0 if pos_x < 0 else 1.0, 1.0, 0.0)
        glVertex3f(-1.5 if pos_x < 0 else 1.5, -0.5, 0.0)
        glEnd()
        glPopMatrix()
        
    glPopMatrix() 
    glPopMatrix()