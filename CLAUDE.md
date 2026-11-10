# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Educational 3D immunology game for a computer graphics course: the player picks one of six characters (Isaac, Azazel, Chispa, Mapi, Brote, Perno; each is a cell type with its own attack and limitation) and fights pathogens (viruses, bacteria, a boss) through three levels, the myocardium (scene `0`), the blood vessel (scene `1`) and the lymph node (scene `2`, with the boss), collecting erythrocytes (health), ATP (energy) and antibodies (mark pathogens). The other rooms (6, 7, 8, 9, y, u) are leftover exploration rooms with no enemies. It uses Python with legacy fixed-function OpenGL (immediate mode) through PyOpenGL and GLUT, and pygame only for audio. Code, comments and identifiers are in Spanish; follow that in new code.

## Commands

There is no requirements file, test suite or build step. `pyrightconfig.json` turns off only the wildcard-import warning, since `from OpenGL.X import *` is used everywhere; `# type: ignore` on `GL_*|GL_*` lines covers a false positive from PyOpenGL's constant types. Dependencies are `PyOpenGL` and either `pygame-ce` or `pygame` (working versions: PyOpenGL 3.1.10 with pygame-ce 2.5.8 on Python 3.14, or with pygame 2.6.1 on Python 3.12).

```bash
python main.py   # run from the repo root so package imports resolve
```

- If `python` resolves to the Microsoft Store stub, it fails; call the real interpreter by its full path.
- To smoke-test, run for a few seconds and check for tracebacks: `PYTHONDONTWRITEBYTECODE=1 timeout 6 <python> main.py` (exit 124 means it was still running). This opens a real window and only proves startup, so rendering changes need a visual check by the user.

## Building the .exe

`construir_exe.bat` builds a Windows executable with PyInstaller inside `.venv` (set `PYTHON=<full path>` first if `python` opens the Store stub). It runs `main.spec`: one file by default (`dist/JuegoInmunologico.exe`), or `construir_exe.bat carpeta` for a folder. `docs/` has the user `LEEME_USUARIO.txt` and the report (`REPORTE_DESPLIEGUE.md/.html/.pdf`).

- Resources must be located with `RESOURCES/rutas.py` (`ruta_recurso(...)`, which uses `sys._MEIPASS` when frozen), never with `__file__`. `UTILS/SOUNDS` is bundled by `main.spec`.
- The package folders have no `__init__.py`, so `main.spec` lists every module of `ACTIONS`, `CHARACTERS`, `RESOURCES` and `SCENS` as `hiddenimports` (except the four unused ones). A new `.py` is picked up automatically, but a new top-level folder must be added to the loop in the spec. The spec also bundles the freeglut DLLs and excludes numpy (PyOpenGL works without it; the game was verified both ways).
- The .exe has no console: when frozen, `main.configurar_registro()` writes everything to `juego_log.txt` next to the .exe. Always rebuild and run the .exe after code changes; check the line `Audio: 14 de 14 sonidos cargados`.
- `build/`, `dist/` and `juego_log.txt` are git-ignored.

## Repository gotchas

- `__pycache__/*.pyc` files are tracked even though `.gitignore` lists them, so running the app shows them as modified. Stage files by name and avoid `git add .` or `git add -A`.
- Some folder and module names have unusual spelling or capitalization: `SCENS`, `RESOURCES/HandLes.py`, `CHARACTERS/Issac.py`. Match them exactly in imports.
- Nothing imports `RESOURCES/camera.py`, `RESOURCES/colisiones.py`, `CHARACTERS/primitivas.py` or `CHARACTERS/Azazel_Lighting.py`. The live camera is in `HandLes.py`, and the live collision code is in `SCENS/objetos_biologicos.py`. Don't edit the unused modules expecting a behavior change.

## Architecture

`main.py` owns the GLUT setup and the frame. `display()` is registered as both the display and idle callback, so it redraws continuously. Each frame first calls `juego.actualizar(dt, t)` (all game logic, with `dt` clamped to 0.05 s), then draws; animations still use `time.time()`.

Frame order in `display()`: update → clear (per-scene background) → camera (orbit + soft follow of the player) → fog → lights → room → lights again → shadows → entities, exit portal, projectiles → player (rotated toward its facing, scaled by `ESCALA_JUGADOR`) → particles → HUD. Fog and the background color come from `AMBIENTES` (scenes `0`, `1` and `2`) and fog is turned off before the HUD. The light of each level (global ambient, main light color, and the second light: red pulse, cyan spotlight that follows the player, or breathing gold) is set per frame in `iluminacion.aplicar_luces(t, escenario, foco)` from the `ATMOSFERA` table; `main.display` calls it twice per frame and passes the player position as `foco`.

**Game modules.**
- `ACTIONS/juego.py`: the game state (`fase` = JUGANDO/VICTORIA/DERROTA, `nivel`, `jugador` dict, counters, held keys), the balance table `ESTADISTICAS`, movement, damage (the Perno frontal shield), pickups, exit and level change, `pose()`. It imports `HandLes` at top level, so `HandLes` must import `juego` lazily inside functions (it does).
- `ACTIONS/combate.py`: one attack per character (`ATAQUES`): Isaac tears (straight spheres), the Azazel blood ray (a red beam that follows the player for 0.5 s and burns in ticks), Chispa flash, Mapi homing antibodies, Brote weak lysis, Perno instant beam. Space triggers it (holding it repeats, limited by the cooldown and energy); it auto-faces the nearest pathogen within 12 units. `juego.VEL_FACTOR` scales every character speed in `ESTADISTICAS`.
- `SCENS/objetos_biologicos.py`: entity list (`entidades`) of pathogens, pickups and vesicle obstacles, per-type AI, the six collision methods (`COLISION`), lysis, drops, and drawing. Changes reach `juego` through an event queue (`tomar_eventos`), not callbacks.
- `SCENS/efectos.py` (particles and rings), `SCENS/heartroom.py` (level 1), `SCENS/vasos.py` (level 2, blood vessel with an animated floor current) and `SCENS/escenario_linfatico.py` (level 3, lymph node with follicles and floating gold ATP). The three build their static walls and floor once into an OpenGL display list (`visual.pared_relieve` builds the walls with a relief function and analytic normals) and animate the rest per frame; each sets its own wet-look `visual.material(...)`, `RESOURCES/visual.py` (primitives, halos, fog).

**Exiting.** Don't call `sys.exit()` from a GLUT callback: the exception is swallowed by ctypes and the app keeps running. Use `glutLeaveMainLoop()`; `main()` sets `GLUT_ACTION_CONTINUE_EXECUTION` so `glutMainLoop` returns and `shutdown_audio()` runs.

**Global state lives in `RESOURCES/HandLes.py`.** It holds the input callbacks, the GLUT menu and module-level state (`estado_escenario`, `estado_expresion`, `estado_movimiento`, camera angles, toggles). The player position lives in `juego.jugador`, not here. Other modules read it as `h.<name>`. Keep that form, because `from HandLes import x` would copy a stale value. Lighting toggles live separately in `RESOURCES/iluminacion.py`. Audio is loaded into `ACTIONS/state.py` and played by name with `play_sound`, which silently ignores unknown or failed sounds.

**Start menu.** `estado_escenario` starts as `"MENU"`. In that state `main.display()` calls `SCENS/menu_seleccion.py` (its own fixed camera, lighting and HUD) and returns early, so no room, collisions or player are drawn. While in the menu, `HandLes.keyboard` ignores everything except A/D (choose character), ENTER (confirm: `juego.iniciar_partida`, then scene `0`) and ESC; left/right arrows also choose, and the mouse and other arrows are ignored so the hidden game camera doesn't change. The right-click GLUT menu stays available.

**Controls and held keys.** `glutIgnoreKeyRepeat(1)` is on and `main()` registers key-up callbacks, so movement is per-frame with `dt`: A/D/W/S and the arrows add/remove directions in `juego.teclas` (`HandLes.keyboard`/`keyboard_up`/`special_keys`/`special_up`). The arrows no longer rotate the camera; the mouse orbits and zooms. Space attacks, `C` toggles the continuous jump (drains energy), F1, F2 and F3 (also `0` and `T` for levels 1 and 2) jump to a level through `HandLes.ir_a_escenario` (which respawns that level through `juego.ir_a_nivel`; the other scene keys just change the room), and ENTER/Backspace act on the victory and defeat screens. The old debug keys (expressions, movements, scenes, toggles) still work.

**Selected vs. displayed state.** `estado_expresion` and `estado_movimiento` are what the user selected. `juego.pose()` overrides them from game events (hurt, healed, attacking, low health, moving, end screens) when `reacciones_activas` is on, and `main.display` stores the result in `expresion_mostrada` and `movimiento_mostrado`, which the HUD reads.

**Character contract.** Every `draw_*` takes `(expresion, movimiento, t)` and handles the same Spanish strings, including `"guiño"` with the ñ; `CHARACTERS/personajes.py` maps each character name to its function in `DIBUJAR`, which both `main.display` and the menu use. Chispa, Mapi, Brote and Perno share poses in `CHARACTERS/chibi.py` (numeric pose IDs in `MOVIMIENTOS` and `EXPRESIONES`) and smooth them with `CHARACTERS/animacion.py`. `chispa.brillo_extra` is set by `combate` to make the Chispa bulb flash. A new expression or movement must be added to Isaac, Azazel and `chibi.py`. A new character also needs entries in `opciones_personaje` (HandLes), `DIBUJAR`, `ESTADISTICAS` (juego), `combate.ATAQUES`, and `SLOTS`, `NOMBRES` and `ROLES` in `menu_seleccion.py`.

**Coordinate quirks.**
- Character geometry is modeled around z = +7 (the pivot used for turning it), so `main.py` draws it at `jugador["z"] - 7`. Collisions, shadows and the player hitbox use `jugador["x"]`/`["z"]` directly as the world position. The facing angle `jugador["ang"]` is 0 toward +z (the camera); the attacks and the Perno shield use it.
- Each room is drawn inside `glScalef(1.8, 1.8, 1.8)`, so its ±10 walls are at ±18 in world units. Entities and the player are not scaled; `bio.resolver` clamps them to ±16.5 and pushes them out of the heart (circle at the origin in scene `0`) and the vesicle boxes.
- Entities belong to the current level only: `juego.en_nivel()` is false in any other scene, and then nothing is updated or drawn.

**GL state is shared across the frame.** Rooms and objects run in one global state machine, and only `draw_azazel`, `draw_chispa` and `draw_mapi` wrap themselves in `glPushAttrib`. Restore anything you change, such as lighting, blending, depth mask or the material emission (`visual.material()`; entities end with `_restaurar_material()`). Additive effects go between `visual.iniciar_aditivo()` and `terminar_transparencia()`. The pattern used here is `con_luz = glIsEnabled(GL_LIGHTING)` and re-enabling afterward. Create GLU quadrics once and cache them in a module global, as `_quadric()` does, rather than per frame.

## Extending

Changes span several files because the lookup tables are separate:

- **New room:** add a `draw_*` function in `SCENS/`, then update the dispatch in `main.display`, `ESCENARIOS` and `ETIQUETAS_ESCENARIO` in `HandLes.py`, and `NOMBRES_ESCENARIO` plus the instructions text in `hud.py`. Scene IDs are a mix of ints and strings (`0, 1, 2` are the playable levels, `6, 7, 8, 9, "y", "u"` the leftover rooms). Per-room lights go in `iluminacion.aplicar_luces`; a foggy room also needs an entry in `main.AMBIENTES`. To make it a playable level add it to `juego.NIVELES` and `NOMBRES_NIVEL`, a spawn branch in `objetos_biologicos.iniciar_nivel`, and an entry in `iluminacion.ATMOSFERA`. `juego.ir_a_nivel` starts a fade-in with the level title (`juego.transicion`, drawn by `hud._transicion`).
- **New entity type:** in `objetos_biologicos.py`, add it to `DATOS` (that fills `NOMBRES` and `METODOS` for the HUD panel), a collision function in `COLISION`, an AI branch in `_ia` if it is a pathogen (and add it to `PATOGENOS`), a draw function called from `dibujar`, and optionally a hitbox in `_dibujar_hitbox`. Pickup effects are handled in `juego._recoger`; contact damage uses `DATOS[tipo]["dano"]`.
- **New key or menu entry:** `HandLes.keyboard` checks an `elif` chain on lowercased keys, so check for conflicts first. Menu IDs are grouped by range in `menu_callback`: 100s character, 200s expression, 300s movement, 400s room, 500s actions. Update the instructions text in `hud.py` as well.
