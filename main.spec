# -*- mode: python ; coding: utf-8 -*-
# Configuración de PyInstaller para el juego 3D (PyOpenGL + GLUT + pygame-ce).
#
# Compilar:      python -m PyInstaller main.spec --noconfirm --clean
# Un solo .exe:  (por defecto)            -> dist/JuegoInmunologico.exe
# Carpeta:       set ONEFILE=0 antes de compilar -> dist/JuegoInmunologico/
import os
import glob
import OpenGL

RAIZ = os.path.abspath(SPECPATH)
NOMBRE = "JuegoInmunologico"
ONEFILE = os.environ.get("ONEFILE", "1") != "0"

# 1) Módulos propios. Las carpetas no tienen __init__.py (paquetes de espacio de nombres),
#    así que se listan a mano para que PyInstaller no se los pierda.
SIN_USO = {"camera", "colisiones", "primitivas", "Azazel_Lighting"}
hiddenimports = []
for paquete in ("ACTIONS", "CHARACTERS", "RESOURCES", "SCENS"):
    for ruta in sorted(glob.glob(os.path.join(RAIZ, paquete, "*.py"))):
        modulo = os.path.splitext(os.path.basename(ruta))[0]
        if not modulo.startswith("__") and modulo not in SIN_USO:
            hiddenimports.append(f"{paquete}.{modulo}")

# 2) Recursos: sonidos y la DLL de freeglut que PyOpenGL carga con ctypes.
datas = [(os.path.join(RAIZ, "UTILS", "SOUNDS"), os.path.join("UTILS", "SOUNDS"))]
dlls_opengl = os.path.join(os.path.dirname(OpenGL.__file__), "DLLS")
for dll in glob.glob(os.path.join(dlls_opengl, "freeglut64*.dll")):
    datas.append((dll, os.path.join("OpenGL", "DLLS")))

# 3) Lo que el juego no usa se excluye para reducir el tamaño.
excludes = ["tkinter", "numpy", "matplotlib", "PIL", "pyopengltk", "OpenGL_accelerate", "unittest", "pydoc"]

a = Analysis(
    [os.path.join(RAIZ, "main.py")],
    pathex=[RAIZ],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

if ONEFILE:
    exe = EXE(
        pyz, a.scripts, a.binaries, a.datas, [],
        name=NOMBRE,
        debug=False,
        strip=False,
        upx=False,
        console=False,      # sin ventana de consola; los mensajes van a juego_log.txt
        runtime_tmpdir=None,
    )
else:
    exe = EXE(
        pyz, a.scripts, [],
        exclude_binaries=True,
        name=NOMBRE,
        debug=False,
        strip=False,
        upx=False,
        console=False,
    )
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=NOMBRE)
