# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Interactive 3D demo for a computer graphics course: a player character (Isaac, Azazel, Chispa or Mapi) moves through switchable rooms and collides with biological objects. It uses Python with legacy fixed-function OpenGL (immediate mode) through PyOpenGL and GLUT, and pygame only for audio. Code, comments and identifiers are in Spanish; follow that in new code.

## Commands

There is no requirements file, test suite or build step. `pyrightconfig.json` turns off only the wildcard-import warning, since `from OpenGL.X import *` is used everywhere; `# type: ignore` on `GL_*|GL_*` lines covers a false positive from PyOpenGL's constant types. Dependencies are `PyOpenGL` and either `pygame-ce` or `pygame` (working versions: PyOpenGL 3.1.10 with pygame-ce 2.5.8 on Python 3.14, or with pygame 2.6.1 on Python 3.12).

```bash
python main.py   # run from the repo root so package imports resolve
```

- If `python` resolves to the Microsoft Store stub, it fails; call the real interpreter by its full path.
- To smoke-test, run for a few seconds and check for tracebacks: `PYTHONDONTWRITEBYTECODE=1 timeout 6 <python> main.py` (exit 124 means it was still running). This opens a real window and only proves startup, so rendering changes need a visual check by the user.

## Repository gotchas

- `__pycache__/*.pyc` files are tracked even though `.gitignore` lists them, so running the app shows them as modified. Stage files by name and avoid `git add .` or `git add -A`.
- Some folder and module names have unusual spelling or capitalization: `SCENS`, `RESOURCES/HandLes.py`, `CHARACTERS/Issac.py`. Match them exactly in imports.
- Nothing imports `RESOURCES/camera.py`, `RESOURCES/colisiones.py`, `CHARACTERS/primitivas.py` or `CHARACTERS/Azazel_Lighting.py`. The live camera is in `HandLes.py`, and the live collision code is in `SCENS/objetos_biologicos.py`. Don't edit the unused modules expecting a behavior change.

## Architecture

`main.py` owns the GLUT setup and the frame. `display()` is registered as both the display and idle callback, so it redraws continuously, and animation is driven by `time.time()` rather than by frame deltas. Collision checks also run inside `display()`; there is no separate update step.

Frame order in `display()`: camera transform → lights → room → lights again → shadows → collision checks and biological objects → reaction resolution → character → HUD.

**Exiting.** Don't call `sys.exit()` from a GLUT callback: the exception is swallowed by ctypes and the app keeps running. Use `glutLeaveMainLoop()`; `main()` sets `GLUT_ACTION_CONTINUE_EXECUTION` so `glutMainLoop` returns and `shutdown_audio()` runs.

**Global state lives in `RESOURCES/HandLes.py`.** It holds the input callbacks, the GLUT menu and module-level state (`estado_escenario`, `estado_expresion`, `estado_movimiento`, `player_x`, `player_z`, camera angles, toggles). Other modules read it as `h.<name>`. Keep that form, because `from HandLes import x` would copy a stale value. Lighting toggles live separately in `RESOURCES/iluminacion.py`. Audio is loaded into `ACTIONS/state.py` and played by name with `play_sound`, which silently ignores unknown or failed sounds.

**Start menu.** `estado_escenario` starts as `"MENU"`. In that state `main.display()` calls `SCENS/menu_seleccion.py` (its own fixed camera, lighting and HUD) and returns early, so no room, collisions or player are drawn. While in the menu, `HandLes.keyboard` ignores everything except A/D (choose character), ENTER (confirm, switches to scene `0`) and ESC; left/right arrows also choose, and the mouse and other arrows are ignored so the hidden game camera doesn't change. The right-click GLUT menu stays available.

**Selected vs. displayed state.** `estado_expresion` and `estado_movimiento` are what the user selected. While the player touches an object, `main.reaccion_actual` overrides them using `PRIORIDAD` and `REACCIONES`, and the result is stored in `expresion_mostrada` and `movimiento_mostrado`, which the HUD reads. Characters receive the resolved values.

**Character contract.** `draw_isaac`, `draw_azazel`, `draw_chispa` and `draw_mapi` all take `(expresion, movimiento, t)` and handle the same Spanish strings, including `"guiño"` with the ñ. Chispa and Mapi share poses in `CHARACTERS/chibi.py`, which maps those strings to numeric pose IDs in `MOVIMIENTOS` and `EXPRESIONES`, and they smooth poses with `CHARACTERS/animacion.py`. A new expression or movement must be added to Isaac, Azazel and `chibi.py`. A new character also needs entries in `opciones_personaje` and the GLUT menu in `HandLes.py`, plus `SLOTS`, `NOMBRES` and the dispatch in `menu_seleccion.py` and `main.display`.

**Coordinate quirks.**
- Character geometry is modeled at z ≈ +7, so `main.py` draws it at `player_z - 7`. Chispa and Mapi are modeled at z = 0 and add the +7 themselves. Collisions, shadows and the player hitbox use `player_z` directly as the world position.
- Each room is drawn inside `glScalef(1.8, 1.8, 1.8)`, so its ±10 walls are at ±18 in world units. Biological objects and the player are not scaled, and player movement is not clamped to the walls.
- Biological objects are the same in every room, and their state is not per-room.

**GL state is shared across the frame.** Rooms and objects run in one global state machine, and only `draw_azazel`, `draw_chispa` and `draw_mapi` wrap themselves in `glPushAttrib`. Restore anything you change, such as lighting, blending or depth mask. The pattern used here is `con_luz = glIsEnabled(GL_LIGHTING)` and re-enabling afterward. Create GLU quadrics once and cache them in a module global, as `_quadric()` does, rather than per frame.

## Extending

Changes span several files because the lookup tables are separate:

- **New room:** add a `draw_*` function in `SCENS/`, then update the dispatch in `main.display`, `ESCENARIOS` and `ETIQUETAS_ESCENARIO` in `HandLes.py`, and `NOMBRES_ESCENARIO` plus the instructions text in `hud.py`. Scene IDs are a mix of ints and strings (`6, 7, 8, 9, 0, "y", "u"`). Per-room lights go in `iluminacion.aplicar_luces`.
- **New biological object:** in `objetos_biologicos.py`, add the state dict, its entries in `OBJETOS`, `NOMBRES` and `METODOS`, a `verificar_*` and `draw_*` pair, and optionally an entry in `sombras()`. Then update `verificar_y_dibujar_biologicos`, `PRIORIDAD` and `REACCIONES` in `main.py`. A missing `PRIORIDAD` entry means the object triggers no reaction.
- **New key or menu entry:** `HandLes.keyboard` checks an `elif` chain on lowercased keys, so check for conflicts first. Menu IDs are grouped by range in `menu_callback`: 100s character, 200s expression, 300s movement, 400s room, 500s actions. Update the instructions text in `hud.py` as well.
