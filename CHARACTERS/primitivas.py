from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def draw_axes():
    """Dibuja ejes coordenados XYZ"""
    glBegin(GL_LINES)
    # Eje X - rojo
    glColor3f(1,0,0)
    glVertex3f(0,0,0)
    glVertex3f(2,0,0,)

    #Eje Y - verde
    glColor3f(0,1,0)
    glVertex3f(0,0,0)
    glVertex3f(0,2,0,)

    # Eje Z - azul
    glColor3f(0,0,1)
    glVertex3f(0,0,0)
    glVertex3f(0,0,2,)

    glEnd()

def draw_shapes():
    """Dibuja figuras en distintos modos y posiciones"""
    # --------- cubo -------- #
    glPushMatrix()
    glTranslatef(-4, 2, 0)
    glColor3f(1, 0 ,0)
    glutSolidCube(1)
    glColor3f(1, 1, 1)
    glutWireCube(1.01)
    glPopMatrix()

    # ---------- piramide(tetraedro) --------- #
    glPushMatrix()
    glTranslatef(-2,2,0)
    glColor3f(0.8, 0.5, 0.1)
    glutSolidTetrahedron()
    glColor3f(1,1,1)
    glutWireTetrahedron()
    glPopMatrix()
    # ------- Esfera ---- #
    glPushMatrix()
    glTranslatef(0,2,0)
    glColor3f(0.8, 0.5, 1)
    glutSolidSphere(0.7,20,20)
    glColor3f(1,1,1)
    glutWireSphere(0.71,20,20)
    glPopMatrix()
    # --------- cilindro ---- #
    glPushMatrix()
    glTranslatef(2,2,0)
    glRotatef(-90 , 1, 0, 0)
    glColor3f(0.4 , 1 ,0.1 )
    quad = gluNewQuadric()
    gluQuadricDrawStyle(quad, GLU_FILL)
    gluCylinder(quad, 0.4, 0.4 , 1, 20 , 5)
    glColor3f(1, 1, 1)
    gluQuadricDrawStyle(quad, GLU_LINE)
    gluCylinder(quad, 0.4, 0.4, 1, 20 ,5)
    glPopMatrix()
    # ------- cono --------- #
    glPushMatrix()
    glTranslatef(4,2,0)
    glRotate(-90, 1, 0, 0)
    glColor3f(1, 0.4, 0.7)
    glutSolidCone(0.5,1.2,20, 10)
    glColor3f(1,1,1)
    glutWireCone(0.5 , 1.2 ,20, 10)
    glPopMatrix()
    # -------- Prisma rectangular ---------- #
    glPushMatrix()
    glTranslatef(-4, 0, 0)
    glScalef(1, 1.5, 0.5)
    glColor3f(0.2 , 0.8 , 0.9)
    glutSolidCube(1)
    glColor3f(1, 1, 1)
    glutWireCube(1.01)
    glPopMatrix()
