# Datos de los NPC (personajes no jugables) de cada nivel.
#
# Este archivo solo describe a los NPC; la lógica vive en ACTIONS/npcs.py.
# Para agregar un NPC basta con añadir un diccionario a la lista de su nivel.
#
# Estructura de un NPC:
#   "id"          identificador único (guarda su estado: misión, opciones usadas)
#   "nombre", "celula"   lo que se muestra sobre su cabeza y en el diálogo
#   "pos"         (x, z) en coordenadas del mundo (la sala va de -16.5 a 16.5)
#   "apariencia"  cuerpo (radios x, y, z), colores, núcleos y un detalle de forma
#   "mision"      opcional: {"descripcion", "tipos" que cuentan, "meta", "premio"}
#   "entrada"     lista de (condición, nodo): el diálogo empieza en el primer nodo cuya condición se cumpla
#   "dialogo"     nodos {"texto", "opciones"}; cada opción puede tener:
#                   "ir"      nodo siguiente (si falta, la conversación se cierra)
#                   "accion"  nombre de una acción de npcs.ACCIONES (curar, comerciar, ayudas...)
#                   "si"      condición de npcs.CONDICIONES para mostrar la opción ("!" la niega)
#                   "una_vez" la opción desaparece después de usarse con éxito
#   En los textos, {progreso} y {meta} se reemplazan con el avance de la misión.

NPCS_POR_NIVEL = {
    # ------------------------------------------------------------ NIVEL 1: MIOCARDIO
    0: [
        {
            "id": "lupe", "nombre": "Lupe", "celula": "Cardiomiocito", "pos": (-13.0, 9.0),
            "apariencia": {"cuerpo": (1.25, 0.85, 0.8), "color": (1.0, 0.45, 0.5),
                           "nucleo": [(0.0, 0.0, 0.0, 0.32)], "color_nucleo": (0.55, 0.08, 0.2),
                           "detalle": "estrias"},
            "entrada": [(None, "inicio")],
            "dialogo": {
                "inicio": {
                    "texto": "¡Hola, defensor! Soy Lupe, un cardiomiocito: me contraigo sin descanso para que "
                             "el corazón bombee. Unos patógenos están dañando el tejido.",
                    "opciones": [
                        {"texto": "¿Qué debo hacer?", "ir": "objetivo"},
                        {"texto": "Estoy agotado, ¿me ayudas?", "accion": "dar_energia", "una_vez": True},
                        {"texto": "Adiós."},
                    ],
                },
                "objetivo": {
                    "texto": "Elimina a todos los patógenos de la sala; entonces se abrirá la salida luminosa. "
                             "Los eritrocitos te curan y el ATP te da energía.",
                    "opciones": [{"texto": "Entendido.", "ir": "inicio"}, {"texto": "Adiós."}],
                },
            },
        },
        {
            "id": "nico", "nombre": "Nico", "celula": "Neutrófilo", "pos": (13.0, 9.0),
            "apariencia": {"cuerpo": (1.0, 1.0, 1.0), "color": (0.75, 0.8, 1.0),
                           "nucleo": [(-0.3, 0.15, 0.0, 0.26), (0.0, -0.1, 0.0, 0.28), (0.3, 0.15, 0.0, 0.26)],
                           "color_nucleo": (0.35, 0.25, 0.75), "detalle": None},
            "mision": {"descripcion": "Elimina 3 virus", "tipos": ("virus_a", "virus_b"), "meta": 3,
                       "premio": "premio_reservas"},
            "entrada": [("mision_lista", "entregar"), ("mision_activa", "en_curso"),
                        ("mision_entregada", "despedida"), (None, "inicio")],
            "dialogo": {
                "inicio": {
                    "texto": "Soy Nico, un neutrófilo: siempre llego primero a una infección, pero los virus "
                             "son demasiado rápidos para mí. ¿Me ayudas a eliminar 3 virus?",
                    "opciones": [
                        {"texto": "¡Claro que sí!", "accion": "aceptar_mision", "ir": "aceptada"},
                        {"texto": "Ahora no."},
                    ],
                },
                "aceptada": {
                    "texto": "¡Gracias! Vuelve conmigo cuando hayas eliminado 3 virus.",
                    "opciones": [{"texto": "Adiós."}],
                },
                "en_curso": {
                    "texto": "Llevas {progreso} de {meta} virus. ¡Sigue así!",
                    "opciones": [{"texto": "Voy en camino."}],
                },
                "entregar": {
                    "texto": "¡Lo lograste! Como premio te comparto mis reservas.",
                    "opciones": [{"texto": "Recibir premio", "accion": "entregar_mision"}],
                },
                "despedida": {
                    "texto": "Los neutrófilos vivimos pocos días, pero lo damos todo en cada infección. ¡Suerte!",
                    "opciones": [{"texto": "Adiós."}],
                },
            },
        },
    ],

    # ------------------------------------------------------------ NIVEL 2: VASO SANGUÍNEO
    1: [
        {
            "id": "pia", "nombre": "Pía", "celula": "Plaqueta", "pos": (-13.0, 10.0),
            "apariencia": {"cuerpo": (1.15, 0.5, 1.15), "color": (0.95, 0.75, 0.95),
                           "nucleo": [(0.0, 0.0, 0.0, 0.2)], "color_nucleo": (0.7, 0.3, 0.6),
                           "detalle": "puntas"},
            "entrada": [(None, "inicio")],
            "dialogo": {
                "inicio": {
                    "texto": "Soy Pía, una plaqueta. Cuando un vaso se rompe formamos un tapón para cerrar la "
                             "herida. Puedo repararte a cambio de energía.",
                    "opciones": [
                        {"texto": "Cambiar 30 de energía por 35 de salud", "accion": "comerciar_salud",
                         "ir": "inicio"},
                        {"texto": "¿Qué es una plaqueta?", "ir": "info"},
                        {"texto": "Adiós."},
                    ],
                },
                "info": {
                    "texto": "Somos fragmentos de una célula gigante de la médula ósea, el megacariocito. "
                             "Vivimos unos 10 días.",
                    "opciones": [{"texto": "Volver", "ir": "inicio"}],
                },
            },
        },
        {
            "id": "max", "nombre": "Max", "celula": "Macrófago residente", "pos": (13.0, 10.0),
            "apariencia": {"cuerpo": (1.3, 1.1, 1.2), "color": (0.95, 0.8, 0.45),
                           "nucleo": [(0.15, 0.1, 0.0, 0.38)], "color_nucleo": (0.6, 0.4, 0.15),
                           "detalle": "seudopodos"},
            "entrada": [(None, "inicio")],
            "dialogo": {
                "inicio": {
                    "texto": "Soy Max, un macrófago residente: me como todo lo que estorba. ¿Quieres que "
                             "devore las vesículas que bloquean el paso?",
                    "opciones": [
                        {"texto": "Sí, despeja el camino.", "accion": "devorar_vesiculas", "si": "hay_vesiculas",
                         "una_vez": True},
                        {"texto": "¿Por qué no peleas tú?", "ir": "consejo"},
                        {"texto": "Adiós."},
                    ],
                },
                "consejo": {
                    "texto": "Ya estoy viejo para perseguir virus. Un consejo: los virus de espículas largas "
                             "embisten en línea recta, así que muévete de lado.",
                    "opciones": [{"texto": "Volver", "ir": "inicio"}],
                },
            },
        },
    ],

    # ------------------------------------------------------------ NIVEL 3: GANGLIO LINFÁTICO
    2: [
        {
            "id": "ada", "nombre": "Ada", "celula": "Célula plasmática", "pos": (-13.0, 9.0),
            "apariencia": {"cuerpo": (1.0, 1.15, 0.9), "color": (0.55, 0.85, 1.0),
                           "nucleo": [(0.35, -0.25, 0.0, 0.34)], "color_nucleo": (0.2, 0.35, 0.7),
                           "detalle": "anticuerpos"},
            "mision": {"descripcion": "Elimina 2 bacilos", "tipos": ("bacilo",), "meta": 2,
                       "premio": "debilitar_jefe"},
            "entrada": [("mision_lista", "entregar"), ("mision_activa", "en_curso"),
                        ("mision_entregada", "despedida"), (None, "inicio")],
            "dialogo": {
                "inicio": {
                    "texto": "Soy Ada, una célula plasmática: fabrico miles de anticuerpos por segundo. Si "
                             "eliminas 2 bacilos, estudiaré sus antígenos y debilitaré a la biopelícula.",
                    "opciones": [
                        {"texto": "Acepto la misión.", "accion": "aceptar_mision", "ir": "aceptada"},
                        {"texto": "Fabrica anticuerpos ya (40 de energía)", "accion": "fabricar_anticuerpos",
                         "si": "hay_patogenos"},
                        {"texto": "Adiós."},
                    ],
                },
                "aceptada": {
                    "texto": "Perfecto. Tráeme noticias de 2 bacilos eliminados.",
                    "opciones": [{"texto": "Adiós."}],
                },
                "en_curso": {
                    "texto": "Llevas {progreso} de {meta} bacilos. También puedo marcar a los patógenos ahora.",
                    "opciones": [
                        {"texto": "Fabrica anticuerpos (40 de energía)", "accion": "fabricar_anticuerpos",
                         "si": "hay_patogenos"},
                        {"texto": "Sigo en ello."},
                    ],
                },
                "entregar": {
                    "texto": "¡Ya conozco sus antígenos! Voy a cubrir a la biopelícula con anticuerpos.",
                    "opciones": [{"texto": "¡Hazlo!", "accion": "entregar_mision"}],
                },
                "despedida": {
                    "texto": "Mis anticuerpos seguirán en la sangre por meses. ¡Termina el trabajo!",
                    "opciones": [{"texto": "Adiós."}],
                },
            },
        },
        {
            "id": "teo", "nombre": "Teo", "celula": "Linfocito T colaborador", "pos": (13.0, 9.0),
            "apariencia": {"cuerpo": (0.95, 0.95, 0.95), "color": (0.7, 1.0, 0.65),
                           "nucleo": [(0.0, 0.0, 0.0, 0.62)], "color_nucleo": (0.2, 0.5, 0.25),
                           "detalle": None},
            "entrada": [(None, "inicio")],
            "dialogo": {
                "inicio": {
                    "texto": "Soy Teo, un linfocito T colaborador. No ataco directamente: coordino a las demás "
                             "células con señales llamadas citocinas.",
                    "opciones": [
                        {"texto": "Reanima a mi compañero", "accion": "reanimar_companero", "si": "hay_caido"},
                        {"texto": "Dame ánimos (salud completa)", "accion": "curar_completo", "una_vez": True},
                        {"texto": "¿Cómo venzo al jefe?", "ir": "jefe"},
                        {"texto": "Adiós."},
                    ],
                },
                "jefe": {
                    "texto": "La biopelícula embiste más seguido cuando pierde la mitad de su salud. Márcala con "
                             "anticuerpos: así recibe 1.8 veces más daño.",
                    "opciones": [{"texto": "Volver", "ir": "inicio"}],
                },
            },
        },
    ],
}
