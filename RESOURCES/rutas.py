import os
import sys


# Inicia: ¿el programa corre como ejecutable empaquetado con PyInstaller?
def es_ejecutable():
    return getattr(sys, "frozen", False)


# Inicia: carpeta donde están los recursos (UTILS, etc.)
# En el .exe PyInstaller los descomprime en sys._MEIPASS; en desarrollo es la raíz del proyecto
def carpeta_base():
    if es_ejecutable():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Inicia: ruta absoluta de un recurso, por ejemplo ruta_recurso("UTILS", "SOUNDS", "click.wav")
def ruta_recurso(*partes):
    return os.path.join(carpeta_base(), *partes)


# Inicia: carpeta donde está el .exe (o la raíz del proyecto), útil para guardar el registro
def carpeta_ejecutable():
    if es_ejecutable():
        return os.path.dirname(sys.executable)
    return carpeta_base()
