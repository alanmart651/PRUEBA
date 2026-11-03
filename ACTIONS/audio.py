import os
import pygame
from ACTIONS import state

# ============================================================
# RUTAS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
SOUNDS_DIR = os.path.join(PROJECT_ROOT, "utils", "sounds")

# ============================================================
# ARCHIVOS DE SONIDO
# ============================================================
SOUND_FILES = {

    # FUNCIONES PRINCIPALES
    "reiniciar": "reiniciar.wav",
    "color": "cambiarcolor.wav",
    "salir": "salir.wav",
    "click": "click.wav",
    "general": "general.mp3",

    #FLECCHAS
    "derecha": "derecha.wav",
    "izquierda": "izquierda.wav",
    "abajo": "abajo.wav",
    "arriba": "arriba.wav",

    #MOVIMIENTOS
    "normal": "1.mp3",
    "saludar": "2.mp3",
    "agacharse": "3.mp3",
    "saltar": "4.mp3",
    "caminar": "5.mp3",

    
}

# ============================================================
# INICIALIZACIÓN
# ============================================================
def init_audio():
    """Inicializa el mixer de pygame y carga todos los sonidos en state."""
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
    except pygame.error as e:
        print("Error inicializando el audio:", e)
        return

    for name, filename in SOUND_FILES.items():
        path = os.path.join(SOUNDS_DIR, filename)
        try:
            state.sounds[name] = pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error cargando sonido '{name}': {e}")
            state.sounds[name] = None

# ============================================================
# REPRODUCIR Y DETENER SONIDOS
# ============================================================
def play_sound(name):
    # Leemos el sonido desde state.sounds
    sound = state.sounds.get(name)
    if sound is None:
        return
    try:
        sound.play()
        state.last_sound = name
    except pygame.error:
        pass

def stop_sound(name):
    sound = state.sounds.get(name)
    if sound is not None:
        try:
            sound.stop()
        except pygame.error:
            pass

def stop_all_sounds():
    try:
        pygame.mixer.stop()
        state.last_sound = None
    except pygame.error:
        pass

def play_ambient(name):
    sound = state.sounds.get(name)
    if sound is None:
        return
    try:
        pygame.mixer.stop()
        sound.play(loops=-1)
        state.last_sound = name
    except pygame.error:
        pass

# ============================================================
# VOLUMEN Y CIERRE
# ============================================================
def set_sound_volume(name, volume):
    sound = state.sounds.get(name)
    if sound is not None:
        sound.set_volume(max(0.0, min(1.0, volume)))

def set_master_volume(volume):
    volume = max(0.0, min(1.0, volume))
    try:
        pygame.mixer.music.set_volume(volume)
        for sound in state.sounds.values():
            if sound is not None:
                sound.set_volume(volume)
    except pygame.error:
        pass

def shutdown_audio():
    try:
        pygame.mixer.stop()
        pygame.mixer.quit()
    except pygame.error:
        pass
    # Limpiamos el estado global
    state.sounds.clear()
    state.last_sound = None