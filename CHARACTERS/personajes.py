from CHARACTERS import Issac as issac
from CHARACTERS import azazel as azazel
from CHARACTERS import chispa as chispa
from CHARACTERS import mapi as mapi
from CHARACTERS import brote as brote
from CHARACTERS import perno as perno

# Función de dibujo de cada personaje: todas reciben (expresion, movimiento, t)
DIBUJAR = {
    "isaac": issac.draw_isaac,
    "azazel": azazel.draw_azazel,
    "chispa": chispa.draw_chispa,
    "mapi": mapi.draw_mapi,
    "brote": brote.draw_brote,
    "perno": perno.draw_perno,
}
