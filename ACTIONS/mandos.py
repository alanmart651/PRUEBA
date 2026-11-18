import os

# Mandos (gamepads) con pygame. El juego usa GLUT para la ventana, así que pygame solo inicia
# su subsistema de video para poder leer los eventos (no abre ninguna ventana). Si no hay
# pygame o falla algo, los mandos se desactivan y el teclado sigue funcionando igual.
#
# Cada mando se traduce a las mismas acciones que el teclado (HandLes.accion):
#   stick izquierdo o cruceta = moverse / elegir   A = atacar o confirmar   X = hablar
#   B = cerrar el diálogo   START = aceptar (menú y pantallas finales)
# Asignación: con un jugador, el primer mando es del J1. Con dos jugadores, si hay un solo
# mando es del J2 (el J1 usa el teclado); si hay dos, el primero es del J1 y el segundo del J2.

os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")   # leer aunque la ventana activa sea la de GLUT
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

try:
    import pygame
except ImportError:
    pygame = None

ZONA_MUERTA = 0.45
BOTONES = {0: "atacar", 1: "cerrar", 2: "hablar", 7: "aceptar"}   # numeración de SDL para mandos tipo Xbox

_listo = False
_mandos = {}       # id de instancia -> pygame.joystick.Joystick
_previo = {}       # id de instancia -> acciones que estaban presionadas en el cuadro anterior


# Inicia: preparar pygame para leer mandos (se llama una vez al arrancar)
def iniciar():
    global _listo
    if pygame is None:
        return
    try:
        pygame.display.init()
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            _agregar(i)
        _listo = True
        print(f"Mandos: {len(_mandos)} conectados")
    except Exception as ex:
        print("Mandos desactivados:", ex)


def _agregar(indice):
    mando = pygame.joystick.Joystick(indice)
    mando.init()
    _mandos[mando.get_instance_id()] = mando
    _previo[mando.get_instance_id()] = set()


# Inicia: a qué jugador pertenece cada mando, según el modo de juego
def _asignacion(dos_jugadores):
    ids = sorted(_mandos)
    if not ids:
        return {}
    if not dos_jugadores:
        return {ids[0]: 0}
    if len(ids) == 1:
        return {ids[0]: 1}
    return {ids[0]: 0, ids[1]: 1}


# Inicia: acciones presionadas ahora mismo en un mando
def _leer_mando(mando):
    activas = set()
    ejes_x = mando.get_axis(0) if mando.get_numaxes() > 0 else 0.0
    ejes_y = mando.get_axis(1) if mando.get_numaxes() > 1 else 0.0
    cruz_x, cruz_y = mando.get_hat(0) if mando.get_numhats() > 0 else (0, 0)
    if ejes_x < -ZONA_MUERTA or cruz_x < 0:
        activas.add("izq")
    if ejes_x > ZONA_MUERTA or cruz_x > 0:
        activas.add("der")
    if ejes_y < -ZONA_MUERTA or cruz_y > 0:     # en la cruceta, arriba es +1
        activas.add("arr")
    if ejes_y > ZONA_MUERTA or cruz_y < 0:
        activas.add("aba")
    for boton, nombre in BOTONES.items():
        if boton < mando.get_numbuttons() and mando.get_button(boton):
            activas.add(nombre)
    return activas


# Inicia: leer todos los mandos y enviar los cambios como acciones (llamar en cada cuadro)
def leer():
    if not _listo:
        return
    from RESOURCES import HandLes as h
    try:
        # se vacía toda la cola (si no, los eventos de ejes se acumularían) y solo se usan las conexiones
        for ev in pygame.event.get():
            if ev.type == pygame.JOYDEVICEADDED:
                if not any(m.get_id() == ev.device_index for m in _mandos.values()):
                    _agregar(ev.device_index)
            elif ev.type == pygame.JOYDEVICEREMOVED and ev.instance_id in _mandos:
                # al desconectar, se sueltan las acciones que tenía presionadas
                jugador = _asignacion(h.dos_jugadores).get(ev.instance_id)
                if jugador is not None:
                    for nombre in _previo[ev.instance_id]:
                        h.accion(jugador, nombre, False)
                del _mandos[ev.instance_id]
                del _previo[ev.instance_id]
        for id_mando, jugador in _asignacion(h.dos_jugadores).items():
            ahora = _leer_mando(_mandos[id_mando])
            antes = _previo[id_mando]
            for nombre in ahora - antes:
                h.accion(jugador, nombre, True)
            for nombre in antes - ahora:
                h.accion(jugador, nombre, False)
            _previo[id_mando] = ahora
    except Exception as ex:
        print("Error al leer mandos:", ex)
