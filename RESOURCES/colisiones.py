import math

def check_aabb(px, pz, radio, bx, by, bz, bw, bh, bd):
    # Detección para Vesículas plano XZ
    overlap_x = (px + radio >= bx - bw/2) and (px - radio <= bx + bw/2)
    overlap_z = (pz + radio >= bz - bd/2) and (pz - radio <= bz + bd/2)
    return overlap_x and overlap_z

def check_sphere(px, py, pz, pradio, ox, oy, oz, oradio):
    # Detección para el Virus
    dx = px - ox
    dy = py - oy
    dz = pz - oz
    dist_cuadrada = dx*dx + dy*dy + dz*dz
    return dist_cuadrada <= ((pradio + oradio) ** 2)

def check_manhattan_rombo(px, pz, ox, oz, umbral):
    # Detección para la molécula de ATP
    dist_manhattan = abs(px - ox) + abs(pz - oz)
    return dist_manhattan <= umbral