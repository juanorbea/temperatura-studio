"""The 26 data graphics of «China y la IA #1» (G1-G26 of the direction plan), blueprint theme.

Every figure, date and quote comes from the direction plan (checked there against Concordia AI's
briefs #31 and #30, sources [1] and [2]) or the script v3. Nothing is invented: where the plan
says a fact is missing (the text of the catalogue entries, a count by type, the Chinese title of
the catalogue, the 2020 code of TikTok's entry) the graphic shows grey bars or leaves it out.
Each function returns the overlay of one shot; arguments pick the state of a graphic that is
built up shot by shot. CHARTS lists every state, for scripts/render_charts.py.
Source of each graphic in the docstring: [1] brief #31 (29 oct 2026), [2] brief #30 (15 oct 2026).
"""
from studio.graphics import opener

J = {"big": "J", "lines": ["禁 jìn", "PROHIBIDO"], "ink": "j"}
X = {"big": "X", "lines": ["限 xiàn", "RESTRINGIDO"], "ink": "x"}
ARGUED = {"lines": ["ARGUMENTADA"], "ink": "ink"}
NUANCE = {"lines": ["MATIZ"], "ink": "copper"}
CATALOGUE = "Catálogo de tecnologías prohibidas o restringidas para la exportación"
CONCORDIA_EN = "traducción desde la versión inglesa de Concordia AI"


def g01_catalogue(rows=2, focus=False, heading=False, seals=0, tag="BORRADOR"):
    """G1 + G2. Catalogue rows 266402J / 266404X [1]. The entries' descriptions are not in the
    sources (the annex is an image): grey bars. seals: 0, 1 (J) or 2 (J and X) stamped in the row."""
    codes = [("266402J", J), ("266404X", X)][:rows]
    level = [{"seals": [{**seal, "size": 66}]} if i < seals else "" for i, (_, seal) in enumerate(codes)]
    return dict(doc=CATALOGUE if heading else "", tag=tag if heading else "",
                columns=[{"label": "Código", "width": 520}, {"label": "Tecnología", "width": 700}, {"label": "Nivel"}],
                rows=[[{"code": c, "focus": 1 if focus else 0}, None, lv] for (c, _), lv in zip(codes, level)])


def g02_seals(which="both"):
    """G2. The two levels as big stamps [1]: J = 禁 jìn, prohibido; X = 限 xiàn, restringido."""
    return dict(stamp={"j": [J], "x": [X], "both": [J, X]}[which])


def g02_doors(step=2):
    """Hook: what each letter means [1]. J: cannot leave China; X: can leave with a state licence."""
    return dict(kicker="Lo que significa cada letra", title="Una letra decide si sale", show=step, people=[
        {"name": "J", "org": "Prohibido", "note": "No puede salir de China. Puerta cerrada.",
         "seal": {"lines": ["NO SALE"], "ink": "j"}},
        {"name": "X", "org": "Restringido", "note": "Puede salir, pero con una licencia del Estado. Ventanilla.",
         "seal": {"lines": ["CON LICENCIA"], "ink": "x"}}])


def g04_bars(step=1):
    """G4. The proposal [1]: 40 entries = 23 AI + 17 biomedicine and photovoltaics; 23 = 6 J + 17 X."""
    if step == 1:
        return dict(kicker="Borrador del 16 de octubre de 2026", title="40 entradas nuevas", max=40, highlight=1, bars=[
            {"label": "Total", "value": 40, "text": "40"},
            {"label": "IA", "value": 23, "text": "23"},
            {"label": "Resto", "note": "biomedicina y fotovoltaica", "value": 17, "text": "17"}])
    return dict(kicker="Las 23 de IA", title="6 prohibidas, 17 restringidas", max=23, highlight=-1, bars=[
        {"label": "IA", "value": 23, "text": "23"},
        {"label": "Prohibidas (J)", "value": 6, "text": "6", "ink": "j"},
        {"label": "Restringidas (X)", "value": 17, "text": "17"}])


def g05_types(step=2, date_stamp=True):
    """G5. 40 technologies, 23 of them AI, and the kinds of AI entries [1]. There is no count by
    kind in the sources, so the kinds are only listed."""
    o = dict(kicker="Catálogo · borrador", title="40 tecnologías; 23 son de IA", figures=[
        {"value": "40", "label": "tecnologías que Pekín propone añadir"},
        {"value": "23", "label": "de IA: modelos de lenguaje · agentes · diseños de chips · clústeres de cómputo · "
                              "herramientas de ciberataque"}][:step], highlight=step - 1)
    if step == 1:
        o["title"] = "40 tecnologías"
    if date_stamp:
        o["seals"] = [{"lines": ["16 OCT 2026"], "ink": "ink", "size": 70, "at": [1500, 210]}]
    return o


def g06_who(step=1):
    """G6. Who regulates what [1]. 1: CAC; 2: + MOFCOM and MOST at the border; 3: + NDRC (Manus);
    4: MOFCOM also hosts the consultation mechanism with the US."""
    cards = [
        {"name": "CAC", "org": "Administración del Ciberespacio", "note": "La IA como servicio dentro de China"},
        {"name": "MOFCOM + MOST", "org": "Comercio · Ciencia y Tecnología",
         "note": "La tecnología cuando sale de China: pesos · puntos de control · arquitectura · software del agente"},
        {"name": "NDRC", "org": "Desarrollo y Reforma", "note": "Seguridad de inversión extranjera (Manus)"}]
    if step == 4:
        cards[1] = {**cards[1], "note": "Habla con Washington (mecanismo de consultas) y decide qué IA sale"}
    return dict(kicker="¿Quién regula qué?", title="Tres organismos", people=cards, show=min(step, 3),
                highlight={1: 0, 2: 1, 3: 2, 4: 1}[step])


def g07_precedents(state=1):
    """G7. Precedents. 2020 the catalogue and TikTok [1]; 2022 US chip controls (no source in
    sources.md, given as common knowledge); 2023 gallium and germanium [1].
    state 1: 2022 and 2023 lit, 2020 grey; state 2: 2020 and 2023 lit, 2022 grey."""
    steps = [{"date": "2020", "label": "China revisa su catálogo (TikTok)"},
             {"date": "2022", "label": "EE. UU. restringe chips y máquinas"},
             {"date": "2023", "label": "China controla galio y germanio"}]
    return dict(kicker="Controles de exportación", title="De dónde venimos", steps=steps, highlight=2,
                muted=[0] if state == 1 else [1])


def g08_cctv():
    """G8. Commentary linked to CCTV [1], in Spanish, with Concordia's English translation under it."""
    return dict(kicker="Comentario vinculado a CCTV · traducción al inglés de Concordia AI", size=50,
                title="«A medida que China llega a la frontera en más campos, gestionar su propia tecnología se ha "
                      "convertido en una nueva prioridad, después de años defendiéndose de bloqueos extranjeros.»",
                body="«As China reaches the frontier in more fields, managing its own technology has become a new "
                     "priority after years of defending against foreign blockades.»")


MOFCOM_SECURITY = [
    "«Tecnologías como la generación y mutación autónoma de código malicioso impulsada por IA pueden usarse "
    "para atacar infraestructuras críticas de información,",
    "la industria de defensa y militar, asuntos clave del Gobierno y otros sistemas sensibles […].",
    "Si las adquirieran actores no estatales o entidades maliciosas, podrían dañar la seguridad nacional y la "
    "seguridad común de la humanidad.»"]


def g09_mofcom_security(part=1):
    """G9. MOFCOM on security [1], in three shots, with two phrases highlighted."""
    return dict(kicker=f"MOFCOM · {CONCORDIA_EN}", size=56, title=MOFCOM_SECURITY[part - 1],
                highlight=["actores no estatales o entidades maliciosas", "la seguridad común de la humanidad"])


def g10_manus(hi=2):
    """G10. Meta and Manus [1]: Jan 2026 MOFCOM will review; Apr 2026 NDRC blocks it (foreign
    investment security review); 16 Oct 2026 draft catalogue."""
    return dict(kicker="Meta y Manus", title="Una compra frenada", highlight=hi, steps=[
        {"date": "Ene 2026", "label": "El MOFCOM anuncia que revisará la compra"},
        {"date": "Abr 2026", "label": "La NDRC la bloquea (revisión de seguridad de inversión extranjera)"},
        {"date": "16 oct 2026", "label": "Borrador del catálogo"}])


def g11_tiktok(hi=2):
    """G11. TikTok [1]: 2020 ByteDance asks for the licence; never granted; early 2026 the algorithm
    is licensed to a joint venture in the US. More than five years."""
    return dict(kicker="TikTok", title="Lo que pesa una licencia", highlight=hi, span="Más de cinco años",
                steps=[{"date": "2020", "label": "ByteDance pide la licencia"},
                       {"date": "…", "label": "…nunca se concede…"},
                       {"date": "Principios de 2026", "label": "Licencia del algoritmo a una empresa conjunta en EE. UU."}])


def g12_register(step=1):
    """G12. Register is not a licence [1]. 1: the two procedures; 2: dates. The exact day of the
    registration is not known: «less than two weeks after the draft»."""
    if step == 1:
        return dict(kicker="Registro ≠ licencia", title="Dos trámites distintos", highlight=0, people=[
            {"name": "Registro", "org": "Ya en vigor · temporal",
             "note": "Para que los reguladores recojan información hasta que el catálogo sea definitivo"},
            {"name": "Licencia", "org": "Cuando el catálogo sea definitivo", "note": "El proceso que vendrá después"}])
    return dict(kicker="Ya en vigor", title="Registrados «sin problemas»", highlight=1, steps=[
        {"date": "16 oct 2026", "label": "Se publica el borrador. Empieza el registro"},
        {"date": "Menos de 2 semanas", "label": "DeepSeek y MiniMax ya constan como registrados «sin problemas»"}])


MOFCOM_OPEN = [
    "«Para apoyar la construcción de un ecosistema de innovación de código abierto en IA, se aplicarán "
    "medidas de facilitación como la licencia automática […].",
    "Se propone no incluir en el ámbito de la gestión de exportaciones las tecnologías que ya hayan entrado "
    "en el dominio público",
    "mediante el código abierto, la publicación de artículos académicos y medios similares.»"]


def g13_mofcom_open(part=1):
    """G13. MOFCOM on open source [1], three shots, «licencia automática» and «dominio público» highlighted."""
    return dict(kicker=f"MOFCOM · {CONCORDIA_EN}", size=56, title=MOFCOM_OPEN[part - 1],
                highlight=["licencia automática", "dominio público"])


def g14_lockers(show=3):
    """G14. Three lockers [1]: already published = exempt; X not yet published = automatic licence
    即报即出 «presentar y salir» (a promise of the draft); J = not exported."""
    return dict(kicker="Modelos abiertos", title="Tres casilleros", show=show, highlight=show - 1, people=[
        {"name": "Ya publicado", "org": "Exento", "note": "La norma no se aplica hacia atrás"},
        {"name": "X por publicar", "org": "Licencia automática",
         "note": "即报即出 «presentar y salir» (promesa del borrador)"},
        {"name": "J", "org": "No se exporta", "note": "Ni en abierto ni de ninguna otra forma",
         "seal": {"lines": ["NO SE EXPORTA"], "ink": "j"}}])


def g15_three_ways():
    """G15. What has to be registered, from a footnote of [1]; the second one lit (MIT, Apache)."""
    return dict(kicker="¿Publicar en abierto es exportar?", title="Lo que hay que registrar", highlight=1,
                caption="Nota al pie del boletín #31 de Concordia AI", people=[
                    {"name": "1", "org": "Cesión", "note": "Ceder la titularidad de la tecnología"},
                    {"name": "2", "org": "Licencia", "note": "Licenciar para uso en el extranjero (MIT · Apache)"},
                    {"name": "3", "org": "Control", "note": "Cambio de titular o controlador"}])


def g16_lawyer():
    """G16. A lawyer to Caixin, via [1]."""
    return dict(kicker="Un abogado, vía Caixin · traducción", size=56, highlight=["callejón sin salida"],
                title="«Si los modelos abiertos de frontera se trataran como prohibidos para la exportación, la vía "
                      "de la licencia automática que fomenta la cooperación en código abierto llegaría a un "
                      "callejón sin salida.»")


def g16_scale(level="x"):
    """G16 (balance). The promise only holds if frontier models are in X [1]."""
    return dict(kicker="La promesa", title="Solo vale si están en la X", highlight=0 if level == "x" else 1, people=[
        {"name": "En la X", "org": "Restringido", "note": "La licencia automática tiene sentido", "seal": X},
        {"name": "En la J", "org": "Prohibido", "note": "La promesa llega a un callejón sin salida", "seal": J}])


WAYS = [
    ["1. Umbrales cuantitativos", "Casi seguro para varios modelos", "No hay umbral"],
    ["2. Datos importantes o esenciales", "Datos importantes 重要数据", "Datos esenciales 核心数据 (improbable, no imposible)"],
    ["3. Agentes en ámbitos sensibles", "Agentes generalistas, posible", "Solo agentes en ámbitos sensibles"],
    ["4. Contramedidas informáticas 信息对抗技术", "Descubrimiento de vulnerabilidades asistido por IA",
     "Generación y mutación de código malicioso + 2 de evasión"]]


def g17_ways(reveal=0, conclusion=False):
    """G17. Four ways a frontier model or agent could fall in X or J [1]; one row per shot."""
    o = dict(kicker="Concordia AI", doc="Cuatro caminos hacia la X o la J",
             columns=[{"label": "Camino", "width": 560}, {"label": "X · restringido", "width": 520},
                      {"label": "J · prohibido", "ink": "j"}],
             rows=WAYS, reveal=reveal, highlight=reveal - 1 if reveal and not conclusion else -1)
    if conclusion:
        o["foot"] = ["Conclusión", "Muy probable", "Poco probable, no descartado"]
    return o


def g18_map():
    """G18. Beijing (116.4 E, 39.9 N) and Washington (77.0 W, 38.9 N), summit 24-25 Sep 2026 [2]. Land only."""
    return dict(kicker="24-25 de septiembre de 2026", title="Cumbre en Estados Unidos", link=True,
                lit=[{"name": "Pekín", "lon": 116.4, "lat": 39.9}, {"name": "Washington", "lon": -77.0, "lat": 38.9}])


def g18_names():
    """Name cards, never portraits [2]."""
    return dict(kicker="24-25 de septiembre de 2026", title="La cumbre", people=[
        {"name": "Xi Jinping", "org": "Presidente de China", "note": ""},
        {"name": "Donald Trump", "org": "Presidente de EE. UU.", "note": ""}])


def g19_summit(step=1):
    """G19. What came out of the summit [2]: an AI dialogue (next meeting in November, no exact
    date) and a bilateral channel for AI incidents; two years without formal talks."""
    if step == 1:
        return dict(kicker="Confirmado por los dos gobiernos", title="Dos cosas concretas", people=[
            {"name": "Diálogo sobre IA", "org": "Riesgos y beneficios",
             "quote": "intercambiar opiniones sobre los riesgos y beneficios relacionados con la IA",
             "when": "Próxima reunión: noviembre"},
            {"name": "Canal bilateral", "org": "Incidentes de IA", "note": "Un canal de comunicación para incidentes de IA"}])
    return dict(kicker="EE. UU. y China", title="Parece poco", figures=[
        {"value": "2 años", "label": "sin conversaciones formales bilaterales sobre IA"}],
        caption="Concordia AI: el resultado superó sus expectativas")


def g20_notes(step=1):
    """G20. The two official notes [2], then the spokesman's answer."""
    if step == 1:
        return dict(kicker="Dos notas oficiales", title="¿Superinteligencia o IA?", people=[
            {"name": "EE. UU.", "org": "Nota de la Casa Blanca", "note": "«Super Intelligence (SI) Dialogue» · «SI incidents»"},
            {"name": "China", "org": "Nota china", "note": "«Inteligencia artificial», en todo momento"}])
    return dict(kicker="Portavoz del Ministerio de Exteriores de China",
                title="«Valora la posición de EE. UU. y respeta la formulación estadounidense»")


def g21_agenda(show=3):
    """G21. The agenda proposed by Yuyuan Tantian 玉渊谭天 (WeChat account linked to CCTV; not an
    official position) [2]. No TC260 in v3."""
    return dict(kicker="Yuyuan Tantian 玉渊谭天 · cuenta ligada a CCTV · no es una postura oficial",
                title="Una agenda para noviembre", show=show, highlight=show - 1, people=[
                    {"name": "1", "org": "Canal de incidentes",
                     "note": "Qué se comunica · en cuánto tiempo · qué información · qué pasa si alguien no avisa"},
                    {"name": "2", "org": "Definiciones comunes", "note": "¿Qué cuenta como un riesgo grave?"},
                    {"name": "3", "org": "Lo peor primero",
                     "note": "Que las capacidades más peligrosas no caigan en manos de terroristas"}])


def g22_folders():
    """G22. Two folders [2]: common risks (open) and a separate «list of differences» (export controls, chips)."""
    return dict(kicker="Propuesta de expertos chinos", title="Dos carpetas", highlight=0, people=[
        {"name": "Riesgos comunes", "org": "Abierta", "note": "Terroristas, incidentes"},
        {"name": "Lista de diferencias", "org": "Cerrada", "note": "Controles de exportación, chips"}])


def g23_rules(step=1):
    """G23. Regulations vs a law [2]; the State Council's legislative plan of May 2026."""
    if step == 1:
        return dict(kicker="Cómo regula China la IA", title="Reglamento frente a ley", highlight=0, people=[
            {"name": "Reglamentos", "org": "Ministerios", "note": "Rápidos y flexibles. Así se regula hoy"},
            {"name": "Ley general", "org": "Asamblea Popular Nacional",
             "note": "Un proceso mucho más lento. Como la ley de IA de la UE"}])
    return dict(kicker="Plan legislativo del Consejo de Estado · mayo de 2026",
                title="«Acelerar la legislación integral sobre el desarrollo sano de la IA»")


def g24_drafts(hi=-1):
    """G24. Two new unofficial drafts of a national AI law, mid-October 2026 [2]."""
    no = {"lines": ["NO OFICIAL"], "ink": "muted"}
    return dict(kicker="Mediados de octubre de 2026", title="Dos borradores no oficiales", highlight=hi, people=[
        {"name": "Universidad de Zhejiang", "org": "Gobernanza por idoneidad",
         "note": "Capacidad de ejecución · madurez cognitiva · naturaleza de la tarea", "seal": no},
        {"name": "Lin Qianduo", "org": "Universidad Tecnológica de Wenzhou",
         "note": "Ciberseguridad · art. 22: controles a modelos abiertos con capacidad de ciberataque", "seal": no}])


def g25_jurists(show=2):
    """G25. Jurists who contradict each other in public [2] (v3: Zhang Wenxian and Shou Bu)."""
    return dict(kicker="¿Habrá ley de IA?", title="Juristas en desacuerdo", show=show, highlight=show - 1, people=[
        {"name": "Zhang Wenxian", "org": "Jurista veterano", "quote": "avanza en todos los frentes y se acelera"},
        {"name": "Shou Bu", "org": "Universidad Jiao Tong de Shanghái",
         "note": "Lee el plan como una renuncia a una ley de IA independiente"}])


def g26_columns(show=2):
    """G26, the two columns of the closing [1] (v3): left TikTok, a licence asked for in 2020 and never
    granted, the algorithm licensed early 2026, more than five years. Right: open models at level X,
    automatic licence «presentar y salir» (a promise of the draft); DeepSeek and MiniMax passed the
    provisional registration, which is not the licence yet, in less than two weeks."""
    return dict(kicker="El mismo catálogo", title="Cinco años o «presentar y salir»", show=show, highlight=show - 1,
                people=[{"name": "TikTok", "org": "Licencia",
                         "note": "Pedida en 2020 · nunca concedida · algoritmo licenciado a principios de 2026",
                         "when": "Más de cinco años"},
                        {"name": "Modelos abiertos del nivel X", "org": "Licencia automática (promesa del borrador)",
                         "note": "«Presentar y salir» · DeepSeek y MiniMax: registro provisional, aún no es la licencia",
                         "when": "Menos de dos semanas"}])


def g26_scale(stamp=True):
    """G26, the two waits to scale: more than 60 months against less than half a month (2 weeks)."""
    o = dict(kicker="El mismo catálogo", title="La espera, a escala", max=62, highlight=1, bars=[
        {"label": "TikTok", "note": "licencia", "value": 62, "text": "Más de 5 años"},
        {"label": "Nivel X", "note": "registro provisional", "value": 0.45, "text": "Menos de 2 semanas"}])
    if stamp:
        o["seals"] = [{"lines": ["MISMO CATÁLOGO"], "ink": "ink", "size": 54, "at": [1560, 190]}]
    return o


IDEAS = ["De defenderse de los controles a imponer los suyos",
         "La seguridad es un motivo real, pero no el único",
         "Los modelos abiertos, protegidos. Por ahora",
         "Washington y Pekín vuelven a hablar: poco y en concreto",
         "Más plural y más discutido de lo que creemos"]


def g03_card(shown=5, argued=0, nuances=0, footer=""):
    """G3. Juan's five ideas (script v3) with their state: PENDIENTE, ARGUMENTADA (one per idea as
    the video argues it) and MATIZ (six: one per idea and a sixth on idea 5)."""
    rows = []
    for i, idea in enumerate(IDEAS):
        seals = [ARGUED] if i < argued else []
        n = 1 if i < nuances else 0
        if i == 4 and nuances >= 6:
            n = 2
        seals += [NUANCE] * n
        rows.append([str(i + 1), idea, {"seals": seals} if seals else {"label": "Pendiente"}])
    o = dict(kicker="Mi lectura", doc="Expediente 01 · Ficha de lectura", opinion=True, reveal=shown,
             columns=[{"label": "Nº", "width": 110}, {"label": "Idea", "width": 1000}, {"label": "Estado"}],
             rows=rows, highlight=shown - 1 if 0 < shown < 5 and not argued else -1, caption=footer)
    return o


CHARTS = {
    "G01-a-tecleo": g01_catalogue(rows=1), "G01-b-dos-filas": g01_catalogue(rows=2),
    "G01-c-ultima-letra": g01_catalogue(focus=True), "G01-d-cabecera": g01_catalogue(focus=True, heading=True),
    "G02-a-sello-j": g01_catalogue(focus=True, heading=True, seals=1),
    "G02-b-sellos-j-x": g01_catalogue(focus=True, heading=True, seals=2),
    "G02-c-sellos-grandes": g02_seals(), "G02-d-puertas": g02_doors(),
    "G03-a-pendientes": g03_card(), "G03-b-idea-1": g03_card(argued=1),
    "G03-c-cinco-argumentadas": g03_card(argued=5), "G03-d-seis-matices": g03_card(argued=5, nuances=6,
                                                                                  footer="Misma dirección, camino más lento"),
    "G04-a-40": g04_bars(1), "G04-b-6-17": g04_bars(2), "G05-a-40": g05_types(1), "G05-b-tipos": g05_types(2),
    "G06-a-cac": g06_who(1), "G06-b-frontera": g06_who(2), "G06-c-ndrc": g06_who(3), "G06-d-washington": g06_who(4),
    "G07-a": g07_precedents(1), "G07-b": g07_precedents(2), "G08-cctv": g08_cctv(),
    "G09-1": g09_mofcom_security(1), "G09-2": g09_mofcom_security(2), "G09-3": g09_mofcom_security(3),
    "G10-a": g10_manus(2), "G10-b-abril": g10_manus(1), "G11-tiktok": g11_tiktok(),
    "G12-a-registro": g12_register(1), "G12-b-fechas": g12_register(2),
    "G13-1": g13_mofcom_open(1), "G13-2": g13_mofcom_open(2), "G13-3": g13_mofcom_open(3),
    "G14-a": g14_lockers(1), "G14-c": g14_lockers(3), "G15-vias": g15_three_ways(),
    "G16-a-abogado": g16_lawyer(), "G16-b-balanza": g16_scale(),
    "G17-a-gris": g17_ways(0), "G17-b-fila-2": g17_ways(2), "G17-c-conclusion": g17_ways(4, conclusion=True),
    "G18-a-mapa": g18_map(), "G18-b-nombres": g18_names(),
    "G19-a": g19_summit(1), "G19-b": g19_summit(2), "G20-a": g20_notes(1), "G20-b": g20_notes(2),
    "G21-agenda": g21_agenda(3), "G22-carpetas": g22_folders(), "G23-a": g23_rules(1), "G23-b": g23_rules(2),
    "G24-borradores": g24_drafts(), "G25-juristas": g25_jurists(2),
    "G26-a-columnas": g26_columns(2), "G26-b-escala": g26_scale(),
    "ident-expediente-01": opener(1), "cierre-expediente-01": opener(1, "cerrado"),
    "pantalla-final-expediente-02": opener(2, "próximamente"),
}
