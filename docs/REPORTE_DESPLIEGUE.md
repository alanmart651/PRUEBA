<div class="portada">

**INSTITUTO TECNOLÓGICO DE TOLUCA**

**Tópicos Avanzados de Programación**

# Generación y distribución de un videojuego 3D en PyOpenGL como ejecutable de Windows

Reporte de práctica

| | |
|---|---|
| **Alumno(s):** | [Nombre completo y número de control] |
| **Docente:** | [Nombre del docente] |
| **Proyecto:** | Juego inmunológico 3D (Python, PyOpenGL, GLUT y pygame-ce) |
| **Fecha:** | [Fecha de entrega] |

</div>

<div class="salto"></div>

## 2. Índice y requisitos previos del sistema

### 2.1 Índice

1. Portada
2. Índice y requisitos previos del sistema
3. Guía paso a paso: generación del ejecutable
4. Manual de instalación y ejecución (usuario final)
5. Solución de problemas comunes
6. Conclusiones y anexos
    - Anexo A. Estructura de carpetas resultante en `dist/`
    - Anexo B. Resumen de comandos de compilación

### 2.2 Requisitos de hardware

El juego usa el *pipeline* de función fija de OpenGL (modo inmediato, iluminación con `GL_LIGHTING`, niebla con `GL_FOG` y listas de visualización), por lo que no requiere *shaders* ni una GPU moderna. Los valores siguientes son recomendaciones; el programa se probó únicamente en el equipo descrito al final de esta sección.

| Componente | Mínimo recomendado | Observaciones |
|---|---|---|
| GPU | Compatible con OpenGL 2.1 o superior | Basta con los gráficos integrados (Intel, AMD o NVIDIA) con controlador del fabricante. Un controlador genérico de Windows solo ofrece OpenGL 1.1 por software y el juego iría muy lento. |
| Memoria RAM | 2 GB | El ejecutable de un solo archivo se descomprime en memoria y en disco temporal al arrancar. |
| Almacenamiento | 100 MB libres | El `.exe` pesa 29.2 MB; al ejecutarse extrae unos 50 MB en una carpeta temporal. |
| Sistema operativo | Windows 10 u 11, 64 bits | El ejecutable se generó para Windows x64. |
| Audio | Opcional | Sin dispositivo de audio el juego sigue funcionando sin sonido. |

**Equipo de pruebas de este reporte:** Windows 11 de 64 bits, GPU Intel(R) UHD Graphics con controlador 31.0.101.5186 (OpenGL 4.6 con perfil de compatibilidad).

### 2.3 Entorno de desarrollo

| Herramienta | Versión utilizada | Función |
|---|---|---|
| Python | 3.14.7 (64 bits) | Intérprete del proyecto. |
| PyOpenGL | 3.1.10 | Enlace de Python con OpenGL, GLU y GLUT. |
| pygame-ce | 2.5.8 (SDL 2.32.10) | Reproducción de audio (`pygame.mixer`). |
| PyInstaller | 6.22.3 | Empaquetado del programa en un ejecutable. |
| pyinstaller-hooks-contrib | 2026.10 | Reglas ("hooks") que indican a PyInstaller qué archivos necesitan PyOpenGL y pygame. |

El proyecto incluye dos archivos de dependencias: `requirements.txt` (solo lo necesario para ejecutar el juego: `PyOpenGL==3.1.10` y `pygame-ce==2.5.8`) y `requirements-build.txt` (lo anterior más `pyinstaller>=6.16`; la versión usada fue la 6.22.3, que soporta Python 3.14).

<div class="salto"></div>

## 3. Guía paso a paso: generación del ejecutable

### 3.1 Cómo funciona PyInstaller

Python es un lenguaje interpretado: el código fuente se traduce a *bytecode* (archivos `.pyc`) que ejecuta la máquina virtual de Python. PyInstaller **no convierte el programa a código de máquina**; lo que hace es reunir en un solo lugar todo lo que el programa necesita para funcionar y construir un lanzador ejecutable. El proceso tiene cuatro etapas:

1. **Análisis (`Analysis`).** Parte del script principal (`main.py`) y recorre recursivamente las instrucciones `import` para construir un grafo de dependencias. También rastrea las DLL que necesitan los módulos binarios encontrados (por ejemplo `SDL2.dll` para pygame).
2. **Archivo `PYZ`.** Los módulos de Python encontrados se compilan a *bytecode* y se guardan comprimidos en un archivo con formato propio.
3. **Archivo `PKG`.** Se agrupan el script, el `PYZ`, las bibliotecas dinámicas y los archivos de datos (en este proyecto, los sonidos).
4. **Ejecutable (`EXE`).** Se toma un programa muy pequeño llamado *bootloader* (`runw.exe`, la variante sin consola) y se le adjunta el `PKG`.

Al ejecutar el `.exe` el *bootloader* prepara el entorno, carga el intérprete de Python incluido (`python314.dll`) y lanza el script. Existen dos modalidades de distribución:

| Modalidad | Resultado | Ventajas | Desventajas |
|---|---|---|---|
| **Un solo archivo** (`onefile`) | `dist/JuegoInmunologico.exe` (29.2 MB) | Se entrega un único archivo. | En cada arranque se descomprime en `%TEMP%\_MEIxxxxx` (arranque más lento) y los antivirus lo marcan con más frecuencia. |
| **Carpeta** (`onedir`) | `dist/JuegoInmunologico/` (50.6 MB) | Arranca más rápido y es más fácil de depurar. | Hay que entregar toda la carpeta. |

Dos propiedades de un programa empaquetado importan para el código fuente: PyInstaller define `sys.frozen = True` y, en la modalidad de un solo archivo, `sys._MEIPASS` apunta a la carpeta temporal donde se extrajeron los recursos.

### 3.2 Preparación del código fuente

**a) Rutas dinámicas de recursos.** El único módulo que leía archivos del disco era `ACTIONS/audio.py`, y calculaba la ruta con `__file__`. Dentro del ejecutable esa ruta ya no existe, así que se creó el módulo `RESOURCES/rutas.py`:

```python
def es_ejecutable():
    return getattr(sys, "frozen", False)

def carpeta_base():
    if es_ejecutable():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ruta_recurso(*partes):
    return os.path.join(carpeta_base(), *partes)
```

Y `audio.py` pasó de usar `__file__` a:

```python
SOUNDS_DIR = rutas.ruta_recurso("UTILS", "SOUNDS")
```

La misma línea funciona en desarrollo (raíz del proyecto), en el `.exe` de un solo archivo (`sys._MEIPASS`) y en la carpeta (`dist/JuegoInmunologico/_internal`).

**b) Registro de mensajes.** El ejecutable se construye sin ventana de consola (`console=False`), por lo que cualquier error sería invisible. `main.py` incluye la función `configurar_registro()`, que dentro del `.exe` redirige `stdout` y `stderr` al archivo `juego_log.txt` (junto al `.exe`, o en la carpeta temporal si no hay permiso de escritura). Además, `init_audio()` escribe cuántos sonidos se cargaron, lo que permite comprobar de inmediato que los recursos se encontraron:

```
Recursos en: C:\Users\...\Temp\_MEI000034302
Audio: 14 de 14 sonidos cargados desde C:\Users\...\_MEI000034302\UTILS\SOUNDS
```

### 3.3 El archivo `main.spec`

El archivo `.spec` es el "plano" de la compilación: es un script de Python que PyInstaller ejecuta. Sus partes principales son:

1. **Módulos propios (`hiddenimports`).** Las carpetas `ACTIONS`, `CHARACTERS`, `RESOURCES` y `SCENS` no tienen `__init__.py` (son paquetes de espacio de nombres), así que el análisis automático puede omitirlas. El `.spec` lista cada `.py` de esas carpetas, excepto cuatro módulos que el juego no usa (`camera`, `colisiones`, `primitivas` y `Azazel_Lighting`).
2. **Recursos (`datas`).** Se copia la carpeta `UTILS/SOUNDS` (23 archivos, 14 MB) conservando su ruta relativa.
3. **DLL de GLUT.** PyOpenGL carga `freeglut` mediante `ctypes` en tiempo de ejecución, por lo que el análisis de importaciones no la ve. El `.spec` agrega explícitamente `freeglut64*.dll` en `OpenGL/DLLS` (el *hook* de PyOpenGL también las incluye; la doble indicación es una medida de seguridad).
4. **Exclusiones.** Se excluyen `numpy`, `tkinter`, `PIL` y otros módulos que el juego no usa. Sin numpy, PyOpenGL emplea sus propias matrices de `ctypes` y escribe en el registro un aviso informativo (`Unable to import OpenGL.arrays.numpymodule.NumpyHandler`) que **no es un error**.
5. **Modalidad.** La variable de entorno `ONEFILE` decide entre un solo archivo (por defecto) y carpeta (`ONEFILE=0`).

### 3.4 Comando de compilación

Desde la raíz del proyecto se ejecuta el script `construir_exe.bat`, que crea un entorno virtual limpio (`.venv`), instala las dependencias y llama a PyInstaller:

```
construir_exe.bat            :: un solo archivo  -> dist\JuegoInmunologico.exe
construir_exe.bat carpeta    :: carpeta          -> dist\JuegoInmunologico\
```

Si el comando `python` abre la Microsoft Store (alias de Windows sin Python instalado), se indica el intérprete real antes de ejecutar el script:

```
set PYTHON=C:\ruta\a\python.exe
```

El comando que ejecuta el script en su último paso, y que puede usarse directamente, es:

```
.venv\Scripts\python.exe -m PyInstaller main.spec --noconfirm --clean
```

La compilación tardó unos 30 segundos y terminó sin errores (`Build complete!`).

### 3.5 Verificación del resultado

1. **Contenido de `dist/`.** Se obtuvo `JuegoInmunologico.exe` (29.2 MB) y, con la modalidad carpeta, `JuegoInmunologico/` (50.6 MB). La estructura completa está en el Anexo A.
2. **Ejecución.** Se lanzaron ambas modalidades y se comprobó que la ventana "Isaac" se abre y muestra el menú de selección con los seis personajes.
3. **Partida completa dentro del ejecutable.** Se enviaron teclas a la ventana (elegir personaje, `ENTER`, `F2`, `F3`) y se verificó que se dibujan el nivel del vaso sanguíneo y el del ganglio linfático, con iluminación, niebla, HUD y enemigos.
4. **Recursos.** El registro confirmó `Audio: 14 de 14 sonidos cargados`, tanto desde `sys._MEIPASS` (un solo archivo) como desde `_internal` (carpeta).
5. **Sin Python en la máquina de destino.** El ejecutable no depende del Python instalado: incluye `python314.dll`, `SDL2.dll` y `freeglut64.vc14.dll`.

Una advertencia de la propia compilación ayudó a detectar un error de otra naturaleza: en una prueba intermedia el ejecutable dibujaba el nivel 3 sin escenario. La causa no fue PyInstaller sino que el editor de código había guardado una versión antigua de `main.py` encima de la actual. Se detectó comparando el resultado del ejecutable con la ejecución en modo desarrollo, y se corrigió reaplicando los cambios y recompilando. La lección práctica es **recompilar y volver a probar el ejecutable cada vez que cambia el código fuente**.

<div class="salto"></div>

## 4. Manual de instalación y ejecución (para el usuario final)

Esta sección está dirigida a quien recibe el juego. No se necesita Python ni ninguna librería.

### 4.1 Requisitos

- Windows 10 u 11 de 64 bits.
- Tarjeta gráfica o gráficos integrados con el controlador del fabricante actualizado (OpenGL 2.1 o superior).
- 100 MB libres en disco y 2 GB de RAM como mínimo recomendado.

### 4.2 Instalación

1. Descomprimir el archivo `JuegoInmunologico_Windows.zip` en una carpeta con permiso de escritura (Escritorio, Documentos). No se debe ejecutar desde dentro del `.zip`.
2. No hay instalador: la carpeta resultante contiene `JuegoInmunologico.exe` y `LEEME_USUARIO.txt`.

### 4.3 Ejecución

1. Hacer doble clic en `JuegoInmunologico.exe`. El primer arranque puede tardar unos segundos mientras el programa se descomprime en una carpeta temporal.
2. Si Windows muestra *"Windows protegió su PC"* (SmartScreen), pulsar **Más información** y después **Ejecutar de todas formas**. El ejecutable no está firmado digitalmente.
3. Elegir personaje con `A`/`D` o las flechas y confirmar con `ENTER`.

| Acción | Tecla |
|---|---|
| Mover | `A` `D` `W` `S` o flechas |
| Atacar (mantener = repetir) | `ESPACIO` |
| Saltar (gasta energía) | `C` |
| Cámara | Ratón: arrastrar para orbitar, rueda para acercar |
| Reiniciar cámara | `R` |
| Instrucciones / Acerca de | `I` / `H` |
| Cambiar de nivel | `F1`, `F2`, `F3` |
| Pantallas de victoria o derrota | `ENTER` reinicia o vuelve al menú, `RETROCESO` regresa al menú |
| Salir | `ESC` |

### 4.4 Controladores gráficos

El rendimiento depende del controlador de la GPU:

- **Intel, AMD y NVIDIA:** instalar el controlador más reciente desde el sitio del fabricante o desde Windows Update.
- **Equipos con dos GPU (portátiles):** en *Configuración > Sistema > Pantalla > Gráficos* asignar `JuegoInmunologico.exe` a la GPU de **alto rendimiento**.
- **Escritorio remoto o máquinas virtuales sin aceleración:** Windows ofrece solo OpenGL 1.1 por software; el juego puede abrir, pero irá muy lento.

<div class="salto"></div>

## 5. Solución de problemas comunes

Primer paso ante cualquier falla: abrir `juego_log.txt`, que se crea junto al `.exe`. Contiene los errores y la línea `Audio: N de 14 sonidos cargados`.

| Síntoma | Causa probable | Solución |
|---|---|---|
| Error `NullFunctionError: Attempt to call an undefined function glutInit` | PyOpenGL no encontró la DLL de **freeglut**. Las DLL antiguas `glut32.dll` y `freeglut.dll` ya no se usan: este proyecto usa `freeglut64.vc14.dll`, que viaja dentro del ejecutable. | Reconstruir con `main.spec` y comprobar que existe `OpenGL\DLLS\freeglut64.vc14.dll` en `_internal` (modalidad carpeta). Si se ejecuta el código fuente, `pip install PyOpenGL==3.1.10` la instala. |
| Aviso de DLL faltante `VCRUNTIME140.dll`, `MSVCP140.dll` | Falta el entorno de ejecución de Visual C++. | Instalar *Microsoft Visual C++ Redistributable 2015-2022 (x64)*. El ejecutable ya incluye `VCRUNTIME140.dll` y `VCRUNTIME140_1.dll`, pero algunos equipos necesitan el paquete completo. |
| Error por falta de `opengl32.dll` o `OpenGL.error.GLError` al crear la ventana | `opengl32.dll` es una biblioteca **de Windows**, no se incluye en el ejecutable. Su ausencia o un fallo suele indicar un controlador gráfico ausente o dañado, o una sesión remota sin aceleración. | Instalar o actualizar el controlador de la GPU; ejecutar en una sesión local. |
| `FileNotFoundError` o el registro dice `Audio: 0 de 14`, o `Error cargando sonido` | La carpeta `UTILS/SOUNDS` no se empaquetó o se movió. El juego no se cierra: continúa sin sonido. | Comprobar que `main.spec` contiene `datas = [(.../UTILS/SOUNDS, UTILS/SOUNDS)]` y reconstruir. Verificar que las rutas se obtienen con `rutas.ruta_recurso(...)` y no con `__file__`. |
| La ventana aparece y se cierra de inmediato | Excepción al arrancar; sin consola no se ve. | Leer `juego_log.txt`. Para depurar, poner `console=True` en `main.spec`, recompilar y ejecutar desde `cmd`. |
| Windows SmartScreen o el antivirus bloquean el archivo | El ejecutable no está firmado y los programas de un solo archivo de PyInstaller generan falsos positivos con frecuencia. | *Más información > Ejecutar de todas formas*; agregar una excepción; o distribuir la modalidad carpeta. |
| Arranque lento (varios segundos) | En un solo archivo se extrae cada vez a `%TEMP%\_MEIxxxxx`. | Es normal; la modalidad carpeta arranca más rápido. |
| Pantalla negra, parpadeo o menos de 15 FPS | Controlador sin aceleración o juego asignado a la GPU integrada. | Actualizar el controlador y asignar la GPU de alto rendimiento (sección 4.4). |
| `python` abre la Microsoft Store al ejecutar `construir_exe.bat` | Alias de Windows sin Python instalado. | `set PYTHON=C:\ruta\a\python.exe` y repetir. |
| `ERROR: Could not find a version that satisfies the requirement pyinstaller` | Versión de Python no soportada por PyInstaller. | Usar una versión reciente de PyInstaller (6.22.3 en este trabajo). |
| En el registro: `Unable to import OpenGL.arrays.numpymodule.NumpyHandler` | Numpy se excluyó a propósito. | Ninguna: es solo informativo. |

### 5.1 Compatibilidad con Linux

PyInstaller **no compila de forma cruzada**: el ejecutable de Windows no corre en Linux, y para obtener uno de Linux hay que compilar en un Linux. En esa plataforma hay que instalar las bibliotecas del sistema (`sudo apt install freeglut3 libglu1-mesa`), y los permisos de ejecución (`chmod +x`) y las sesiones sin servidor X pueden dar errores como `freeglut: failed to open display`. El código fuente no usa llamadas exclusivas de Windows, y el `.spec` tolera la ausencia de las DLL, pero **no se probó la compilación en Linux** en este trabajo.

<div class="salto"></div>

## 6. Conclusiones y anexos

### 6.1 Conclusiones

Empaquetar un videojuego procedural en PyOpenGL con PyInstaller resultó viable y rápido (una compilación de unos 30 segundos), pero reveló que el código debe prepararse para su distribución. La principal dificultad fue de diseño y no de la herramienta: un programa que lee recursos con rutas basadas en `__file__` deja de funcionar al empaquetarse, y la solución fue concentrar el cálculo de rutas en un único módulo (`rutas.py`) que distingue entre ejecución normal y ejecutable mediante `sys.frozen` y `sys._MEIPASS`. Esta es una ventaja de la arquitectura procedimental del proyecto: un cambio centralizado en una función bastó para toda la aplicación.

La segunda lección es que las dependencias cargadas dinámicamente, como la DLL de freeglut que PyOpenGL abre con `ctypes`, no son visibles para el análisis estático de importaciones, y deben declararse explícitamente en el `.spec`. Lo mismo ocurre con los paquetes de espacio de nombres sin `__init__.py`, que se resolvieron con `hiddenimports`.

La tercera lección es la importancia de **verificar el ejecutable ejecutándolo**, no solo comprobando que la compilación termine: la prueba real con partidas simuladas, el archivo de registro y la comparación con la ejecución en modo desarrollo permitieron descubrir un fallo que la compilación no reportaba. Un archivo de registro es indispensable en una aplicación sin consola.

Finalmente, la modalidad de un solo archivo es cómoda para entregar (29.2 MB), pero la de carpeta arranca más rápido y genera menos alertas de antivirus; la decisión depende de si se prioriza la comodidad de entrega o la experiencia de arranque. Como trabajo futuro quedan la firma digital del ejecutable, la compilación y prueba en Linux, y automatizar la verificación del ejecutable.

<div class="salto"></div>

### Anexo A. Estructura de carpetas resultante en `dist/`

**Modalidad un solo archivo:**

```
dist/
└── JuegoInmunologico.exe          (29.2 MB, ejecutable autónomo)
```

**Modalidad carpeta (`construir_exe.bat carpeta`):**

```
dist/JuegoInmunologico/             (50.6 MB en total)
├── JuegoInmunologico.exe           (2.9 MB, lanzador)
└── _internal/
    ├── base_library.zip            (biblioteca estándar de Python)
    ├── python314.dll               (intérprete de Python)
    ├── VCRUNTIME140.dll, VCRUNTIME140_1.dll, MSVCR100.dll
    ├── SDL2.dll, SDL2_mixer.dll, SDL2_image.dll, SDL2_ttf.dll   (audio y soporte de pygame)
    ├── libogg, libopus, libpng, libjpeg, libwebp, freetype ...  (códecs usados por SDL)
    ├── _ctypes.pyd, _decimal.pyd, _ssl.pyd, ...                 (módulos nativos de Python)
    ├── OpenGL/
    │   └── DLLS/
    │       ├── freeglut64.vc14.dll   (GLUT que usa PyOpenGL en Python 3.14 x64)
    │       ├── freeglut32.*, freeglut64.*, gle32.*, gle64.*      (variantes incluidas por el hook)
    │       └── freeglut_COPYING.txt, ...
    ├── pygame/
    │   └── SDL2.dll, ...
    └── UTILS/
        └── SOUNDS/                 (23 archivos .wav y .mp3; el juego usa 14)
```

Archivos del proyecto relacionados con la compilación (en la raíz del repositorio):

```
main.spec                  configuración de PyInstaller
construir_exe.bat          script de compilación
requirements.txt           dependencias de ejecución
requirements-build.txt     dependencias de ejecución + PyInstaller
RESOURCES/rutas.py         rutas dinámicas de recursos (sys._MEIPASS)
docs/LEEME_USUARIO.txt     instrucciones para el usuario final
```

### Anexo B. Resumen de comandos de compilación

| Objetivo | Comando |
|---|---|
| Compilar un solo archivo | `construir_exe.bat` |
| Compilar carpeta | `construir_exe.bat carpeta` |
| Indicar el intérprete de Python | `set PYTHON=C:\ruta\a\python.exe` |
| Crear el entorno virtual a mano | `python -m venv .venv` |
| Instalar dependencias de compilación | `.venv\Scripts\python.exe -m pip install -r requirements-build.txt` |
| Compilar a mano (un solo archivo) | `.venv\Scripts\python.exe -m PyInstaller main.spec --noconfirm --clean` |
| Compilar a mano (carpeta) | `set ONEFILE=0` y luego el comando anterior |
| Ejecutar desde el código fuente | `python main.py` (desde la raíz del proyecto) |
| Comprobar la integridad del `.exe` | `Get-FileHash dist\JuegoInmunologico.exe` (PowerShell) |
| Comprimir para entregar | `Compress-Archive -Path dist\JuegoInmunologico.exe, docs\LEEME_USUARIO.txt -DestinationPath JuegoInmunologico_Windows.zip` |
