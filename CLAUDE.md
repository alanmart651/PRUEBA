# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Interactive 3D demo for a computer graphics course: a player character (Isaac or Azazel) moves through switchable rooms and collides with biological objects. It uses Python with legacy fixed-function OpenGL (immediate mode) through PyOpenGL and GLUT, and pygame only for audio. Code, comments and identifiers are in Spanish; follow that in new code.

## Commands

There is no requirements file, test suite, linter or build step. Dependencies are `PyOpenGL` and `pygame-ce` (working versions: 3.1.10 and 2.5.8 on Python 3.14).

```bash
python main.py   # run from the repo root so package imports resolve
```

- On this machine, `python` resolves first to the Microsoft Store stub, which fails. Use `C:\Users\ratad\AppData\Local\Python\bin\python.exe`.
- To smoke-test, run for a few seconds and check for tracebacks: `PYTHONDONTWRITEBYTECODE=1 timeout 6 <python> main.py` (exit 124 means it was still running). This opens a real window and only proves startup, so rendering changes need a visual check by the user.

## Repository gotchas

- `__pycache__/*.pyc` files are tracked even though `.gitignore` lists them, so running the app shows them as modified. Stage files by name and avoid `git add .` or `git add -A`.
- Some folder and module names have unusual spelling or capitalization: `SCENS`, `RESOURCES/HandLes.py`, `CHARACTERS/Issac.py`. Match them exactly in imports.
- `ACTIONS/audio.py` builds its sound path as `utils/sounds`, while the folder is `UTILS/SOUNDS`. This only works on case-insensitive filesystems. The usage note in `ACTIONS/state.py` also uses a stale lowercase `actions.audio` import.
- Nothing imports `RESOURCES/camera.py`, `RESOURCES/colisiones.py`, `CHARACTERS/primitivas.py` or `CHARACTERS/Azazel_Lighting.py`. The live camera is in `HandLes.py`, and the live collision code is in `SCENS/objetos_biologicos.py`. Don't edit the unused modules expecting a behavior change.

## Architecture

`main.py` owns the GLUT setup and the frame. `display()` is registered as both the display and idle callback, so it redraws continuously, and animation is driven by `time.time()` rather than by frame deltas. Collision checks also run inside `display()`; there is no separate update step.

Frame order in `display()`: camera transform → lights → room → lights again → shadows → collision checks and biological objects → reaction resolution → character → HUD.

**Global state lives in `RESOURCES/HandLes.py`.** It holds the input callbacks, the GLUT menu and module-level state (`estado_escenario`, `estado_expresion`, `estado_movimiento`, `player_x`, `player_z`, camera angles, toggles). Other modules read it as `h.<name>`. Keep that form, because `from HandLes import x` would copy a stale value. Lighting toggles live separately in `RESOURCES/iluminacion.py`. Audio is loaded into `ACTIONS/state.py` and played by name with `play_sound`, which silently ignores unknown or failed sounds.

**Selected vs. displayed state.** `estado_expresion` and `estado_movimiento` are what the user selected. While the player touches an object, `main.reaccion_actual` overrides them using `PRIORIDAD` and `REACCIONES`, and the result is stored in `expresion_mostrada` and `movimiento_mostrado`, which the HUD reads. Characters receive the resolved values.

**Character contract.** `draw_isaac` and `draw_azazel` both take `(expresion, movimiento, t)` and branch on the same Spanish strings, including `"guiño"` with the ñ. A new expression or movement must be added to both characters.

**Coordinate quirks.**
- Character geometry is modeled at z ≈ +7, so `main.py` draws it at `player_z - 7`. Collisions, shadows and the player hitbox use `player_z` directly as the world position.
- Each room is drawn inside `glScalef(1.8, 1.8, 1.8)`, so its ±10 walls are at ±18 in world units. Biological objects and the player are not scaled, and player movement is not clamped to the walls.
- Biological objects are the same in every room, and their state is not per-room.

**GL state is shared across the frame.** Rooms and objects run in one global state machine, and only `draw_azazel` wraps itself in `glPushAttrib`. Restore anything you change, such as lighting, blending or depth mask. The pattern used here is `con_luz = glIsEnabled(GL_LIGHTING)` and re-enabling afterward. Create GLU quadrics once and cache them in a module global, as `_quadric()` does, rather than per frame.

## Extending

Changes span several files because the lookup tables are separate:

- **New room:** add a `draw_*` function in `SCENS/`, then update the dispatch in `main.display`, `ESCENARIOS` and `ETIQUETAS_ESCENARIO` in `HandLes.py`, and `NOMBRES_ESCENARIO` plus the instructions text in `hud.py`. Scene IDs are a mix of ints and strings (`6, 7, 8, 9, 0, "y", "u"`). Per-room lights go in `iluminacion.aplicar_luces`.
- **New biological object:** in `objetos_biologicos.py`, add the state dict, its entries in `OBJETOS`, `NOMBRES` and `METODOS`, a `verificar_*` and `draw_*` pair, and optionally an entry in `sombras()`. Then update `verificar_y_dibujar_biologicos`, `PRIORIDAD` and `REACCIONES` in `main.py`. A missing `PRIORIDAD` entry means the object triggers no reaction.
- **New key or menu entry:** `HandLes.keyboard` checks an `elif` chain on lowercased keys, so check for conflicts first. Menu IDs are grouped by range in `menu_callback`: 100s character, 200s expression, 300s movement, 400s room, 500s actions. Update the instructions text in `hud.py` as well.
