"""The pictures of «La carrera del billón» (direction plan v2, § 5): one locked style for all of them,
the AI character in white archival gloves, and the scene of each picture. Every picture is a still
(no AI video); each is generated once and reused across shots (with a different crop or move).

PICTURES maps a file name in assets/images/carrera-del-billon/pictures/ to (scene, character).
The full prompt of a picture is scene + CHARACTER (if character) + STYLE, the same text the
storyboards keep in each shot's prompt.
"""

STYLE = ("Cinematic photorealistic still, 16:9, shot on 35 mm film, natural practical lighting, cool slate-blue "
         "shadows and warm amber sodium highlights, low saturation, slightly lifted blacks, fine film grain, light "
         "atmospheric haze, calm and quiet mood, generous negative space. No text, no letters, no numbers, no logos, "
         "no brand marks, no recognisable products, no real people.")

# The character block of storyboards/anthropic/, with the hands changed (plan § 5): white gloves, always.
CHARACTER = ("The recurring AI character from the reference image: a person whose head is a faceless smooth matte "
             "white mannequin head with no eyes, no mouth and no facial features; charcoal bespoke suit in a fine "
             "birdseye weave; burgundy silk tie with a small gold-cream paisley pattern; burgundy and antique-gold "
             "ornate paisley silk pocket square in the left breast pocket of the jacket (the wearer's left, which is "
             "the viewer's right); under the jacket a vivid koi fish watercolour Hawaiian shirt in blue, gold and "
             "orange. Hands always in plain white cotton archival gloves, or kept out of frame; never bare skin on "
             "the hands.")

LEFT = " Main subject in the right two thirds, calm empty area on the left third."
WIDE = " 24 mm wide establishing shot, low horizon."
MACRO = " 100 mm macro, shallow depth of field, single point of focus."
MEDIUM = " 35 mm medium shot, eye level."

PICTURES = {
    # El almacén (Google)
    "b16-almacen-exterior.jpg": ("A large anonymous warehouse exterior at blue hour, wet asphalt, a single amber light "
                                 "over a loading dock, light fog, no signage." + WIDE + LEFT, False),
    "b01-almacen-vacio.jpg": ("Long modern warehouse interior, symmetrical aisle, the warehouse almost empty: a few "
                              "unmarked wooden crates on a polished concrete floor, soft cool overhead light, one amber "
                              "lamp at the far end." + LEFT, False),
    "b02-almacen-lleno.jpg": ("Long modern warehouse interior, symmetrical aisle, rows of unmarked wooden crates "
                              "stacked high with server racks visible through the slats, cool overhead light, one amber "
                              "lamp at the far end." + LEFT, False),
    "b27-etiquetas.jpg": ("Blank paper shipping tags tied with string to wooden crates, one tag in focus, the rest "
                          "soft, the tags completely blank." + MACRO + LEFT, False),
    "b04-placa.jpg": ("An unmarked accelerator circuit board resting in grey foam inside an open wooden crate, no "
                      "silkscreen, no labels, top light." + LEFT, False),
    "b07-muelle.jpg": ("Loading dock at dusk, unmarked wooden crates lined up waiting, one truck bay open, no logos, "
                       "no signage." + LEFT, False),
    # La plataforma (SpaceX)
    "b05-plataforma.jpg": ("An unmarked generic rocket standing on a launch pad at night, low fog rolling across the "
                           "pad, sodium floodlights, launch tower, no insignia, no flags, no flames, no smoke." + WIDE
                           + LEFT, False),
    "b19-torre.jpg": ("Detail of a launch tower's steel umbilical arms emerging from fog at night, amber work lights, "
                      "no markings." + MACRO + LEFT, False),
    # La nave de cómputo
    "b21-pasillo.jpg": ("Symmetrical one-point perspective down a very long data-centre aisle at night between rows "
                        "of unmarked server racks, cool blue indicator glow, one warm amber light at the end, no "
                        "screens with text." + WIDE, False),
    "b11-nave-mitad.jpg": ("A vast data hall at night seen from one end: half of the aisles lit with cool light and "
                           "half dark, unmarked server racks, no screens." + WIDE + LEFT, False),
    "b09-racks.jpg": ("Two unmarked server racks facing each other in a clean bright lab, cables neatly dressed, no "
                      "labels." + LEFT, False),
    "b14-campus.jpg": ("Aerial view at dusk of a generic data-centre campus, long flat grey halls, fog between the "
                       "buildings, amber road lights, no signage." + WIDE + LEFT, False),
    # La energía
    "b22-torres.jpg": ("High-voltage transmission towers marching into morning fog over flat fields, low sun." + WIDE
                       + LEFT, False),
    "b12-subestacion.jpg": ("An electrical substation at night lit by sodium lamps, faint vapour, transformers and "
                            "insulators, no people, no signs." + LEFT, False),
    "b10-antenas.jpg": ("Generic ground-station parabolic dishes at sunset on a plain, large white dishes on "
                        "pedestals, no logos, not flat-panel user terminals." + WIDE + LEFT, False),
    # La obra
    "b13-obra-amanecer.jpg": ("A data centre under construction at dawn, tower cranes against a pale sky, bare steel "
                              "frame, no signage, no people." + WIDE + LEFT, False),
    "b23-obra-noche.jpg": ("A data-centre construction site at night under tall work lights, cable trays and "
                           "trenches, steel frame, no people, no signage." + WIDE + LEFT, False),
    # La órbita (the haiku)
    "b17-orbita.jpg": ("Earth from low orbit at dawn, the day-night terminator across clouds and ocean, a small "
                       "solitary generic satellite with two solar panels in the right third, black space, no "
                       "recognisable spacecraft, no markings, no flags.", False),
    "b17b-orbita-sol.jpg": ("Earth from low orbit at dawn, the sun just breaking over the curved limb of the Earth "
                            "and touching the solar panels of a small solitary generic satellite in the right third, "
                            "black space, no recognisable spacecraft, no markings.", False),
    "b18-limbo.jpg": ("The thin blue limb of the Earth against black space, a tiny generic satellite in the right "
                      "third, very calm, no markings.", False),
    "b18b-orbita-noche.jpg": ("A tiny generic satellite above the night side of the Earth, faint diffuse city lights "
                              "far below, thin blue airglow on the horizon, black space, no markings.", False),
    # El abismo y otros
    "b24-desfiladero.jpg": ("An empty deep gorge at dawn, mist at the bottom, sheer cliffs on both sides, no bridge."
                            + WIDE, False),
    "b06-informes.jpg": ("A stack of plain unmarked bound quarterly reports on a wooden desk in morning window light, "
                         "blank covers." + LEFT, False),
    "b08-carpetas.jpg": ("Five plain unlabelled manila folders fanned out on a desk, soft light, blank covers." + LEFT,
                         False),
    "b15-imprenta.jpg": ("An old cast-iron printing press in a clean quiet workshop, morning light, no type visible, "
                         "no posters." + LEFT, False),
    "b26-sala-control.jpg": ("An empty control room at night, rows of empty chairs, dark switched-off monitors with "
                             "faint amber reflections, no text on any screen, no people." + WIDE + LEFT, False),
    # El personaje (P)
    "p01-albaran.jpg": ("The character stands in the aisle of a warehouse full of unmarked wooden crates, checking a "
                        "blank delivery note on a clipboard; cool overhead light, an amber lamp far behind."
                        + MEDIUM + LEFT, True),
    "p02-libro.jpg": ("The character sits at a walnut desk by a window before dawn and opens a large ledger with "
                      "blank pages." + MEDIUM + LEFT, True),
    "p03-lupa.jpg": ("The character turns the pages of a thick unmarked report with a magnifying glass under an "
                     "amber desk lamp." + MEDIUM + LEFT, True),
    "p04-calculadora.jpg": ("The character at a drafting table with a desktop calculator with a blank display and a "
                            "pencil, working on a blank sheet." + MEDIUM + LEFT, True),
    "p05-pizarra.jpg": ("The character stands before a whiteboard with a single tall bar drawn on it, no writing, and "
                        "nods calmly." + MEDIUM + LEFT, True),
    "p06-balanza.jpg": ("The character beside an antique brass balance scale on a table, window backlight."
                        + MEDIUM + LEFT, True),
    "p07-contrato.jpg": ("The character signs a very long contract with a fountain pen, pages fanned out on the desk, "
                         "no readable text." + MEDIUM + LEFT, True),
    "p08-ajedrez.jpg": ("The character sits at a chessboard; from the other side of the frame only a single white "
                        "gloved hand reaches in to move a piece, no other person visible." + MEDIUM + LEFT, True),
    "p09-lapiz-rojo.jpg": ("The character turns a page of a large ledger with blank columns, a red pencil in the "
                           "gloved hand." + MEDIUM + LEFT, True),
    "p10-nave-gpu.jpg": ("Wide shot: the character, silhouetted, walks across a vast GPU data hall at night against a "
                         "lit aisle, hands out of frame or at the sides." + WIDE + LEFT, True),
    "p11-anclas.jpg": ("The character at a drafting table with three small brass paperweights shaped like ship "
                       "anchors on a blank sheet." + MEDIUM + LEFT, True),
    "p12-palancas.jpg": ("The character adjusts two brass levers on an old control desk, no labels, no screens."
                         + MEDIUM + LEFT, True),
    "p13-cuentas.jpg": ("The character before an open account book with blank columns, a fountain pen beside it."
                        + MEDIUM + LEFT, True),
    "p14-plano.jpg": ("The character stands before a huge architectural blueprint of a data centre pinned to a wall, "
                      "no readable text, a stack of account books on the table in front." + MEDIUM + LEFT, True),
    "p15-puente.jpg": ("The character stands, seen from behind, on a half-built bridge over a deep gorge at dawn, "
                       "looking at the far side, mist below." + WIDE, True),
    "p16-tableta.jpg": ("The character types on a tablet with a blank screen, the gloved fingers on the glass."
                        + MEDIUM + LEFT, True),
    "p17-oficina.jpg": ("The character in a bright office with an unmarked laptop; colleagues out of focus, seen "
                        "only from behind." + MEDIUM + LEFT, True),
    "p18-se-aleja.jpg": ("Seen from behind, the character walks away down the aisle of a warehouse full of unmarked "
                         "wooden crates, a ledger under one arm." + WIDE, True),
    "p19-escala.jpg": ("Wide symmetrical shot: the character, tiny, stands at the far end of a huge aisle of server "
                       "racks at night, hands at the sides." + WIDE, True),
}


def prompt(name: str) -> str:
    scene, character = PICTURES[name]
    return " ".join(" ".join([scene] + ([CHARACTER] if character else []) + [STYLE]).split())
