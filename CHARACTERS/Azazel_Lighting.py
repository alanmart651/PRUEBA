import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

sombreado_suave = True 
modo_iluminacion = True 

def configurar_luz_phong():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    posicion_luz = [5.0, 8.0, 10.0, 1.0]
    luz_ambiental = [0.2, 0.2, 0.2, 1.0]
    luz_difusa    = [0.9, 0.85, 0.8, 1.0]
    luz_especular = [1.0, 1.0, 1.0, 1.0]

    glLightfv(GL_LIGHT0, GL_POSITION, posicion_luz)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiental)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.15, 0.15, 0.15, 1.0])

def aplicar_material(difusa, especular, brillo, ambiental=None):
    if ambiental is None:
        ambiental = [difusa[0] * 0.2, difusa[1] * 0.2, difusa[2] * 0.2, 1.0]
        
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambiental)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, difusa)
    glMaterialfv(GL_FRONT, GL_SPECULAR, especular)
    glMaterialf(GL_FRONT, GL_SHININESS, brillo)

def draw_azazel_iluminado(expresion="normal", movimiento="reposo", t=0.0):
    glPushAttrib(GL_ALL_ATTRIB_BITS)
    
    if sombreado_suave:
        glShadeModel(GL_SMOOTH)
    else:
        glShadeModel(GL_FLAT)
        
    if modo_iluminacion:
        configurar_luz_phong()
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    else:
        glDisable(GL_LIGHTING)

    quad = gluNewQuadric()
    gluQuadricNormals(quad, GLU_SMOOTH)

    MAT_PIEL_AZAZEL = [0.12, 0.12, 0.14, 1.0]
    MAT_CUERNOS     = [0.05, 0.05, 0.05, 1.0]
    MAT_ESPECULAR_BRILLANTE = [0.9, 0.9, 0.9, 1.0]
    MAT_ESPECULAR_MATE      = [0.1, 0.1, 0.1, 1.0]

    desplazamiento_y = 0.0
    if movimiento == "saltar":
        desplazamiento_y = abs(math.sin(t * 8)) * 2.5

    glPushMatrix()
    glTranslatef(0.0, desplazamiento_y, 0.0)

    # Cabeza
    glPushMatrix()
    glTranslatef(0, 4.0, 7.0)
    glScalef(2.8, 2.2, 2.5)
    aplicar_material(MAT_PIEL_AZAZEL, MAT_ESPECULAR_MATE, brillo=16.0)
    glColor3f(*MAT_PIEL_AZAZEL[:3])
    glutSolidSphere(1.0, 30, 30)
    glPopMatrix()

    for lado, x_pos, rot_z in [(-1, -1.7, 30), (1, 1.7, -30)]:
        glPushMatrix()
        glTranslatef(x_pos, 5.4, 8.2)
        glRotatef(rot_z, 0, 0, 1)
        aplicar_material(MAT_CUERNOS, MAT_ESPECULAR_BRILLANTE, brillo=64.0)
        glColor3f(*MAT_CUERNOS[:3])
        glutSolidSphere(0.5, 15, 15)
        gluCylinder(quad, 0.5, 0.4, 0.9, 15, 5)
        glPopMatrix()

    # Ojos reflectantes
    aplicar_material([0.9, 0.0, 0.0, 1.0], [1.0, 1.0, 1.0, 1.0], brillo=128.0)
    glColor3f(0.9, 0.0, 0.0)
    for x in [-1.1, 1.1]:
        glPushMatrix()
        glTranslatef(x, 4.2, 9.2)
        glutSolidSphere(0.75, 20, 20)
        glPopMatrix()

    glPopMatrix()
    glPopAttrib()


#STANDALONE
def keyboard_practica(key, x, y):
    global sombreado_suave, modo_iluminacion
    if key == b'1':
        modo_iluminacion = False
        print("-> Modo: SIN Iluminación")
    elif key == b'2':
        modo_iluminacion = True
        sombreado_suave = False
        print("-> Modo: Sombreado PLANO (GL_FLAT)")
    elif key == b'3':
        modo_iluminacion = True
        sombreado_suave = True
        print("-> Modo: Sombreado SUAVE / GOURAUD (GL_SMOOTH)")
    glutPostRedisplay()

if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # type: ignore
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Azazel")
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.1, 0.1, 0.12, 1.0)

    def display():
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        glLoadIdentity()
        gluLookAt(0, 4, 20,  0, 3, 7,  0, 1, 0)
        
        # Renderizado de Azazel
        draw_azazel_iluminado(expresion="normal", movimiento="reposo", t=time.time())
        glutSwapBuffers()

    def reshape(w, h):
        if h == 0: h = 1
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / h, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(glutPostRedisplay)
    glutKeyboardFunc(keyboard_practica)

    glutMainLoop()