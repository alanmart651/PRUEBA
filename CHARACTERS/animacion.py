import math
import time

_estados = {}


# ---------- transicion suave entre poses ----------
def suavizar(nombre, objetivo, velocidad=9.0, directos=()):
    ahora = time.time()
    est = _estados.setdefault(nombre, {"t": ahora, "pose": dict(objetivo)})
    dt = min(ahora - est["t"], 0.1)
    est["t"] = ahora
    k = 1.0 - math.exp(-velocidad * dt)
    pose = est["pose"]
    for clave, valor in objetivo.items():
        if clave in directos or clave not in pose:
            pose[clave] = valor
        else:
            pose[clave] += (valor - pose[clave]) * k
    return pose


# ---------- parpadeo ----------
def parpadeo(periodo=3.6, desfase=0.0):
    fase = (time.time() + desfase) % periodo
    if fase < 0.16:
        return max(0.08, abs(fase - 0.08) / 0.08)
    return 1.0


# ---------- respiracion ----------
def respiracion(velocidad=2.2, amplitud=0.018):
    return 1.0 + math.sin(time.time() * velocidad) * amplitud
