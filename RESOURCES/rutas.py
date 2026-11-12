import os
import sys



def es_ejecutable():
    return getattr(sys, "frozen", False)


def carpeta_base():
    if es_ejecutable():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ruta_recurso(*partes):
    return os.path.join(carpeta_base(), *partes)


def carpeta_ejecutable():
    if es_ejecutable():
        return os.path.dirname(sys.executable)
    return carpeta_base()
