import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_puzzle_room():
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    t = time.time()
    color_piso = (0.35, 0.25, 0.2)
    color_pared = (0.3, 0.2, 0.15) 
    
    # Piso
    glColor3f(*color_piso)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(10, 0, -10); glVertex3f(10, 0, 10); glVertex3f(-10, 0, 10)
    glEnd()
    
    #paredes
    glColor3f(color_pared[0]*0.8, color_pared[1]*0.8, color_pared[2]*0.8)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 6, -10); glVertex3f(10, 6, -10); glVertex3f(10, 0, -10)
    glEnd()
    glColor3f(color_pared[0]*0.6, color_pared[1]*0.6, color_pared[2]*0.6)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 6, -10); glVertex3f(-10, 6, 10); glVertex3f(-10, 0, 10)
    glVertex3f(10, 0, -10); glVertex3f(10, 6, -10); glVertex3f(10, 6, 10); glVertex3f(10, 0, 10)
    glEnd()

    glColor3f(0.2, 0.15, 0.1)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(-10, 11, 2):
        glVertex3f(i, 0.01, -10); glVertex3f(i, 0.01, 10)
        glVertex3f(-10, 0.01, i); glVertex3f(10, 0.01, i)
    glEnd()
    glLineWidth(1.0)

#BOTONES
    posiciones_botones = [(-8.0, -8.0), (8.0, 8.0)]
    
    for bx, bz in posiciones_botones:
        glPushMatrix()
        glTranslatef(bx, 0.1, bz)
        
        glColor3f(0.5, 0.5, 0.5)
        glPushMatrix()
        glScalef(1.5, 0.2, 1.5)
        glutSolidCube(1.0)
        glPopMatrix()
        
        glColor3f(0.3, 0.3, 0.3)
        glPushMatrix()
        glTranslatef(0.0, 0.1, 0.0)
        glRotatef(-90, 1, 0, 0)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.5, 0.4, 0.2, 15, 5)
        glTranslatef(0.0, 0.0, 0.2)
        gluDisk(quad, 0.0, 0.4, 15, 1)
        glPopMatrix()
        
        glPopMatrix()

    posiciones_rocas = [
        (-6.0, -6.0), (-6.0, -4.0), (-6.0, -2.0), (-6.0, 0.0), (-6.0, 2.0), (-6.0, 4.0), (-6.0, 6.0),
        (6.0, -6.0), (6.0, -4.0), (6.0, -2.0), (6.0, 0.0), (6.0, 2.0), (6.0, 4.0), (6.0, 6.0),
        (0.0, -2.0), (0.0, 0.0), (0.0, 2.0), (-2.0, 0.0), (2.0, 0.0)
    ]
    
    for rx, rz in posiciones_rocas:
        glPushMatrix()
        glTranslatef(rx, 0.5, rz)
        glColor3f(0.25, 0.25, 0.25)
        glScalef(1.2, 1.0, 1.2)
        glutSolidCube(1.0)
        glColor3f(0.1, 0.1, 0.1)
        glutWireCube(1.02)
        glPopMatrix()

    #FOGATAS
    posiciones_fuego = [
        (-5.0, -4.0), (-5.0, 0.0), (-5.0, 4.0),
        (5.0, -4.0), (5.0, 0.0), (5.0, 4.0)
    ]
    
    for i, (fx, fz) in enumerate(posiciones_fuego):
        glPushMatrix()
        glTranslatef(fx, 0.2, fz)
        
        glColor3f(0.3, 0.15, 0.05)
        glPushMatrix(); glRotatef(45, 0, 1, 0); glScalef(1.2, 0.2, 0.3); glutSolidCube(1.0); glPopMatrix()
        glPushMatrix(); glRotatef(-45, 0, 1, 0); glScalef(1.2, 0.2, 0.3); glutSolidCube(1.0); glPopMatrix()
        escala_fuego = 1.0 + abs(math.sin(t * 10.0 + i)) * 0.3
        
        glPushMatrix()
        glTranslatef(0.0, 0.8, 0.0)
        glScalef(0.6 * escala_fuego, 1.2 * escala_fuego, 0.6 * escala_fuego)
        
        brillo_fuego = abs(math.sin(t * 15.0 + i))
        glColor3f(1.0, 0.4 + (brillo_fuego * 0.4), 0.0) 
        
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(1.0, 1.0, 10, 5)
        glPopMatrix()
        
        glPopMatrix()

    #PUERTAS
    pos_puertas = [(0.0, 2.0, -9.9, 0), (0.0, 2.0, 9.9, 180)]
    
    for px, py, pz, rot in pos_puertas:
        glPushMatrix()
        glTranslatef(px, py, pz)
        glRotatef(rot, 0, 1, 0)
        glScalef(2.5, 4.0, 0.2)
        glColor3f(0.4, 0.4, 0.4)
        glutSolidCube(1.0)
        glTranslatef(0.0, 0.0, 0.1)
        glScalef(0.8, 0.9, 1.0)
        glColor3f(0.0, 0.0, 0.0)
        glutSolidCube(1.0)
        glPopMatrix()

    glPopMatrix()