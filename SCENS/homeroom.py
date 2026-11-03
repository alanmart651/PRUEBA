from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_home_room():
    glPushMatrix()
    glScalef(1.8, 1.8, 1.8)

    
    #PISO
    glColor3f(0.25, 0.18, 0.12) 
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10)
    glVertex3f(10, 0, -10)
    glVertex3f(10, 0, 10)
    glVertex3f(-10, 0, 10)
    glEnd()
    
    glColor3f(0.15, 0.1, 0.05)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for z in range(-10, 11, 2):
        glVertex3f(-10, 0.01, z)
        glVertex3f(10, 0.01, z)
    for x in range(-8, 9, 4):
        glVertex3f(x, 0.01, -10)
        glVertex3f(x, 0.01, 10)
    glEnd()
    glLineWidth(1.0)

    #PAREDES
    color_pared = (0.75, 0.65, 0.5)
    
    glColor3f(color_pared[0]*0.8, color_pared[1]*0.8, color_pared[2]*0.8)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 6, -10); glVertex3f(10, 6, -10); glVertex3f(10, 0, -10)
    glEnd()
    
    glColor3f(*color_pared)
    glBegin(GL_QUADS)
    glVertex3f(-10, 0, -10); glVertex3f(-10, 6, -10); glVertex3f(-10, 6, 10); glVertex3f(-10, 0, 10)
    glVertex3f(10, 0, -10); glVertex3f(10, 6, -10); glVertex3f(10, 6, 10); glVertex3f(10, 0, 10)
    glEnd()

    #TAPETE
    glPushMatrix()
    glTranslatef(0.0, 0.02, 0.0)
    glColor3f(0.5, 0.4, 0.25)
    glScalef(6.0, 1.0, 4.5)
    glBegin(GL_QUADS)
    glVertex3f(-1, 0, -1); glVertex3f(1, 0, -1); glVertex3f(1, 0, 1); glVertex3f(-1, 0, 1)
    glEnd()
    glColor3f(0.4, 0.3, 0.2)
    glLineWidth(3.0)
    glBegin(GL_LINE_LOOP)
    glVertex3f(-1, 0.01, -1); glVertex3f(1, 0.01, -1); glVertex3f(1, 0.01, 1); glVertex3f(-1, 0.01, 1)
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()

    # CAMA
    glPushMatrix()
    glTranslatef(-6.0, 0.0, -5.5)
    
    # Colchón y sábanas
    glColor3f(0.9, 0.9, 0.9)
    glPushMatrix()
    glTranslatef(0.0, 0.8, 0.0)
    glScalef(2.5, 0.8, 4.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Cabecera de madera
    glColor3f(0.3, 0.2, 0.1)
    glPushMatrix()
    glTranslatef(0.0, 1.5, -2.0)
    glScalef(2.8, 2.5, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Pie de cama de madera
    glPushMatrix()
    glTranslatef(0.0, 1.0, 2.0)
    glScalef(2.8, 1.5, 0.4)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # Almohada gris
    glColor3f(0.6, 0.6, 0.6)
    glPushMatrix()
    glTranslatef(0.0, 1.3, -1.2)
    glScalef(1.8, 0.3, 1.0)
    glutSolidCube(1.0)
    glPopMatrix()
    
    glPopMatrix()

    #COFRE
    glPushMatrix()
    glTranslatef(-6.0, 0.6, 2.5)
    
    # Base del cofre
    glColor3f(0.85, 0.65, 0.1)
    glPushMatrix()
    glScalef(1.5, 1.0, 1.0)
    glutSolidCube(1.0)
    glColor3f(0.4, 0.3, 0.05)
    glutWireCube(1.02)
    glPopMatrix()
    
    # Tapa del cofre
    glColor3f(0.9, 0.7, 0.15)
    glPushMatrix()
    glTranslatef(0.0, 0.6, 0.0)
    glScalef(1.5, 0.3, 1.0)
    glutSolidCube(1.0)
    glColor3f(0.4, 0.3, 0.05)
    glutWireCube(1.02)
    glPopMatrix()
    
    # Cerradura
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glTranslatef(0.0, 0.45, 0.52)
    glutSolidCube(0.2)
    glPopMatrix()
    
    glPopMatrix()

    #PAREDES
    posiciones_dibujos = [
        (-9.9, 3.0, -3.0, 90),
        (-4.0, 3.5, -9.9, 0),
        (5.0, 3.0, -9.9, 0),
        (-3.0, 2.5, 9.9, 180),
    ]
    
    for px, py, pz, rot in posiciones_dibujos:
        glPushMatrix()
        glTranslatef(px, py, pz)
        glRotatef(rot, 0, 1, 0)
        
        # Papel blanco
        glColor3f(0.9, 0.9, 0.9)
        glBegin(GL_QUADS)
        glVertex3f(-0.5, -0.5, 0.0)
        glVertex3f(0.5, -0.5, 0.0)
        glVertex3f(0.5, 0.5, 0.0)
        glVertex3f(-0.5, 0.5, 0.0)
        glEnd()
        
        # Manchas/trazos en el papel
        glColor3f(0.1, 0.1, 0.1)
        glTranslatef(0.0, 0.0, 0.01)
        glPointSize(3.0)
        glBegin(GL_POINTS)
        glVertex3f(-0.2, 0.1, 0.0); glVertex3f(0.1, 0.2, 0.0); glVertex3f(0.0, -0.1, 0.0)
        glEnd()
        glPopMatrix()

    glPopMatrix()