import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from RESOURCES import visual as v

MAX_PARTICULAS = 320

# Cada partícula: p = [x, y, z], v = [vx, vy, vz], vida, max, color, tam, grav
particulas = []
# Cada anillo: x, z, y, r0, r1, vida, max, color
anillos = []


# Inicia: limpiar efectos
def limpiar():
    particulas.clear()
    anillos.clear()


# Inicia: partícula suelta
def particula(pos, vel, color, vida=0.8, tam=6.0, grav=0.0):
    if len(particulas) >= MAX_PARTICULAS:
        return
    particulas.append({"p": list(pos), "v": list(vel), "vida": vida, "max": vida,
                       "color": color, "tam": tam, "grav": grav})


# Inicia: explosión de partículas en todas direcciones
def explosion(pos, color, n=24, vel=5.0, vida=0.8, tam=7.0, grav=-4.0):
    for _ in range(n):
        z = random.uniform(-1.0, 1.0)
        a = random.uniform(0.0, 6.2832)
        r = math.sqrt(1.0 - z * z)
        s = vel * random.uniform(0.35, 1.0)
        particula(pos, (r * math.cos(a) * s, abs(z) * s * 0.8 + 0.5, r * math.sin(a) * s), color,
                  vida * random.uniform(0.6, 1.0), tam * random.uniform(0.6, 1.0), grav)


# Inicia: partículas que suben lento (polen, burbujas)
def flotar(pos, color, n=1, vida=1.4, tam=5.0):
    for _ in range(n):
        particula((pos[0] + random.uniform(-0.8, 0.8), pos[1] + random.uniform(-0.3, 0.3),
                   pos[2] + random.uniform(-0.8, 0.8)),
                  (random.uniform(-0.3, 0.3), random.uniform(0.6, 1.4), random.uniform(-0.3, 0.3)),
                  color, vida, tam, 0.0)


# Inicia: arco de partículas (ataque cuerpo a cuerpo)
def arco(x, z, ang, rango, mitad, color, y=1.6, n=22):
    for i in range(n):
        a = math.radians(ang - mitad + 2.0 * mitad * i / (n - 1))
        dx, dz = math.sin(a), math.cos(a)
        particula((x + dx * rango * 0.55, y, z + dz * rango * 0.55),
                  (dx * 7.0, random.uniform(-0.5, 1.0), dz * 7.0), color, 0.35, 8.0, 0.0)


# Inicia: anillo que se expande o se contrae en el piso
def anillo(x, z, r0, r1, vida, color, y=0.12):
    anillos.append({"x": x, "z": z, "y": y, "r0": r0, "r1": r1, "vida": vida, "max": vida, "color": color})


# Inicia: avanzar el tiempo de los efectos
def actualizar(dt):
    for i in range(len(particulas) - 1, -1, -1):
        q = particulas[i]
        q["vida"] -= dt
        if q["vida"] <= 0.0:
            particulas.pop(i)
            continue
        q["v"][1] += q["grav"] * dt
        q["p"][0] += q["v"][0] * dt
        q["p"][1] += q["v"][1] * dt
        q["p"][2] += q["v"][2] * dt
        if q["p"][1] < 0.05:
            q["p"][1] = 0.05
            q["v"][1] *= -0.3
    for i in range(len(anillos) - 1, -1, -1):
        anillos[i]["vida"] -= dt
        if anillos[i]["vida"] <= 0.0:
            anillos.pop(i)


# Inicia: dibujo aditivo de partículas y anillos
def dibujar():
    if not particulas and not anillos:
        return
    v.iniciar_aditivo()
    glEnable(GL_POINT_SMOOTH)
    for q in particulas:
        k = q["vida"] / q["max"]
        c = q["color"]
        glPointSize(max(2.0, q["tam"] * (0.4 + 0.6 * k)))
        glBegin(GL_POINTS)
        glColor4f(c[0], c[1], c[2], k)
        glVertex3f(*q["p"])
        glEnd()
    glLineWidth(3.0)
    for a in anillos:
        k = 1.0 - a["vida"] / a["max"]
        r = a["r0"] + (a["r1"] - a["r0"]) * k
        c = a["color"]
        glColor4f(c[0], c[1], c[2], 1.0 - k)
        glBegin(GL_LINE_LOOP)
        for i in range(40):
            ang = i * 0.15708
            glVertex3f(a["x"] + math.cos(ang) * r, a["y"], a["z"] + math.sin(ang) * r)
        glEnd()
    glLineWidth(1.0)
    v.terminar_transparencia()
