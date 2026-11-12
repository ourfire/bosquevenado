"""Genera index.html (es), en/index.html (en) y las páginas de gracias.

Uso: python3 src/build.py   (desde la raíz del repositorio; necesita node)
El plano sale de src/engine.js; el estado de los clusters de estado.json.
"""
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
TBD = '<span class="tbd">{}</span>'
CORREO = "info@bosquevenado.com"
WA = "999 991 0450"

TITULOS = {
    "es": {"detalle": "Plano de la etapa 3. Elige un cluster para cotizarlo.",
           "general": "Plano del predio",
           "general_desc": "Tablaje de 7 hectáreas. Las etapas 1 y 2, al oriente, están vendidas. La etapa 3, al poniente, tiene 2 hectáreas con clusters de lotes a los lados de una calle central ondulada."},
    "en": {"detalle": "Phase 3 plan. Choose a cluster to get a quote.",
           "general": "Site plan",
           "general_desc": "A 7-hectare parcel. Phases 1 and 2, on the east side, are sold. Phase 3, on the west side, covers 2 hectares with clusters of lots on both sides of a winding central street."},
}
GEO = json.loads(subprocess.run(["node", str(ROOT / "src" / "engine.js"), json.dumps(TITULOS)],
                                capture_output=True, text=True, check=True).stdout)
DAT = GEO["datos"]
N_LOTES = len(DAT["lotes"])
N_CL = len(DAT["clusters"])
COMUN = f'{DAT["comun"] / DAT["G"]["area"] * 100:.0f}%'
POR_TAM = {t: sum(1 for c in DAT["clusters"] if c["size"] == t) for t in (8, 4, 2)}


def li(items):
    return "".join(f"<li>{a}<small>{b}</small></li>" for a, b in items)


def pasos(items):
    return "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in items)


def capas(items):
    return "".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in items)


LOGO = ('<svg class="venado" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="miter" stroke-linecap="square" aria-hidden="true">'
        '<path d="M44,50 L38,36 L33,24 L31,10"/><path d="M56,50 L62,36 L67,24 L69,10"/><path d="M38,36 L26,31"/><path d="M62,36 L74,31"/><path d="M35,29 L41,16"/><path d="M65,29 L59,16"/><path d="M33,24 L21,17"/><path d="M67,24 L79,17"/><path d="M38,52 L24,47 L35,59"/><path d="M62,52 L76,47 L65,59"/><path d="M38,50 L62,50 L60,66 L50,90 L40,66 Z"/><circle cx="44.5" cy="63" r="1.6" fill="currentColor" stroke="none"/><circle cx="55.5" cy="63" r="1.6" fill="currentColor" stroke="none"/></svg>')


def pilares(items, pend):
    out = []
    for a, b, xs, foto in items:
        lis = "".join(f"<li>{x}</li>" for x in xs)
        out.append(f'<article class="panel"><div class="foto" role="img" aria-label="{foto}"><span class="pend">{pend}: {foto}</span></div>'
                   f'<div class="txt"><h3>{a}</h3><p>{b}</p><ul class="lista">{lis}</ul></div></article>')
    return "".join(out)


def cuatro(items):
    return "".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in items)


def reglas(items):
    return "".join(f'<div><h3>{a}</h3><ul>{"".join(f"<li>{x}</li>" for x in xs)}</ul></div>' for a, xs in items)


def gente(items, pend):
    out = []
    for nombre, rol in items:
        out.append(f'<div><div class="foto" role="img" aria-label="{nombre}"><span class="pend">{pend}</span></div><h3>{nombre}</h3><p>{rol}</p></div>')
    return "".join(out)


def referentes(items, voces):
    out = [f'<article><h3>{a}</h3><p class="lugar">{b}</p><p>{c}</p><p><a href="{u}" target="_blank" rel="noopener">{v}</a></p></article>' for a, b, c, u, v in items]
    out.append(f'<article class="voces"><h3>{voces[0]}</h3><p>{voces[1]}</p></article>')
    return "".join(out)


def faq(items):
    return "".join(f"<details><summary>{a}</summary><p>{b}</p></details>" for a, b in items)


ES = dict(
    lang="es-MX", alt_lang="en", alt_label="English", alt_href="en/",
    title="Bosque Venado, Acanceh, Yucatán",
    desc=f"Comunidad neorural en el monte de Acanceh, Yucatán, con agua de pozo, energía solar y comida propia. {N_LOTES} lotes de 200 m² que se compran desde uno, o en clusters de 2, 4 y 8, con uso vitalicio a través de una serie accionaria tokenizada por La Tokenizadora.",
    draft='Borrador de diseño. Los datos marcados <span class="tbd">así</span> están por definir.',
    home_label="Bosque Venado, inicio", nav_label="Secciones",
    nav_lugar="El lugar", nav_vida="Agua, energía y comida", nav_etapa="La etapa 3", nav_cotiza="Cotiza", nav_faq="Preguntas",
    canon="https://bosquevenado.com/", kicker="Preventa de la etapa 3",
    co_etq="La comunidad",
    com_h="Una comunidad intencional, no un fraccionamiento.",
    com_lede="Bosque Venado nace para construir comunidad alrededor de la economía solidaria y la resiliencia ante un futuro incierto. Queremos agua, energía, comida y lazos entre vecinos. Estamos en preventa: cada participación financia lo común.",
    com_items=cuatro([
        ("Agua, energía y comida", "Lo básico resuelto en común: pozo, sol y siembra. Es lo que nos sostiene si lo de afuera falla."),
        ("Economía solidaria", "Compartimos herramientas, trabajo y cosechas. Preferimos poner el dinero en la tierra y la comunidad que en trámites."),
        ("Confianza entre pares", "Todos nos conocemos. La comunidad aprueba quién entra y quién sale; nadie participa de forma anónima."),
        ("Rigor legal", "Confiar no significa improvisar. Todo está tokenizado y respaldado con acciones de una serie de una SAPI de C.V., con estatutos y reglamento."),
    ]),
    reg_etq="Convivencia", reg_h="Reglamento de convivencia, en esquema.",
    reg_lede="Lo básico para vivir juntos. La versión final se escribe y se vota en comunidad: " + TBD.format("por definir") + ".",
    reglas=reglas([
        ("Admisión y salida", ["Visita y conversación antes de entrar", "La comunidad aprueba a cada nuevo miembro", "Quien hereda o compra pasa por la misma admisión"]),
        ("Decisiones", ["Asamblea periódica de miembros", "Reglas y mejoras se votan", "Forma de voto: " + TBD.format("por definir")]),
        ("Monte y siembra", ["Ningún desmonte sin acuerdo común", "Especies nativas y frutales", "Los caminos verdes son de todos"]),
        ("Construcción", ["Materiales y alturas según el reglamento", "Se respeta la servidumbre de paso", "Área máxima construida: " + TBD.format("por definir")]),
        ("Agua y energía", ["Uso responsable del pozo y el tanque", "Cada casa puede sumar su propio sistema", "Lo común se mantiene con una cuota"]),
        ("Vida diaria", ["Silencio por la noche", "Mascotas bajo el cuidado de su dueño", "Visitas con aviso a la comunidad"]),
        ("Trabajo común", ["Jornadas en el huerto y los caminos", "Las cosechas comunes se reparten", "Cada quien aporta su oficio"]),
        ("Cuotas y conflictos", ["Cuota de mantenimiento: " + TBD.format("por definir"), "Primero se conversa, luego hay mediación", "Regla de impago: " + TBD.format("por definir")]),
    ]),
    qs_etq="Quiénes somos", qs_h="Quienes empujan Bosque Venado.",
    qs_lede="Los fundadores y primeros miembros de la comunidad. Cada quien aporta su oficio a lo común.",
    gente=gente([
        ("Juan Carlos", "Fundador. Semblanza: " + TBD.format("por definir")),
        ("María Cecilia", "Fundadora. Semblanza: " + TBD.format("por definir")),
        ("Alejandro", "Fundador. Semblanza: " + TBD.format("por definir")),
        ("Y más miembros", "Las familias de las etapas 1 y 2 forman parte de la comunidad desde el inicio."),
    ], "Foto pendiente"),
    in_etq="Referentes", in_h="Comunidades que nos inspiran.",
    in_lede="No son testimonios: son proyectos reales en México que llevan años mostrando que se puede vivir así.",
    referentes=referentes([
        ("Huehuecoyotl", "Sierra del Tepozteco, Morelos. Desde 1982.",
         "Ecoaldea donde cada familia construyó su casa y entre todos hicieron el camino, la captación de lluvia, un teatro y las tierras de cultivo. La tierra se maneja en común, por acuerdo entre sus miembros.",
         "https://ecovillage.org/resources-library/article/what-is-our-ecovillage/", "Leer su historia"),
        ("Las Cañadas", "Cerca de Huatusco, Veracruz.",
         "Cooperativa agroecológica y centro de permacultura que cuida una de las últimas islas de bosque de niebla del centro de Veracruz, con bosque comestible y formación en agroecología.",
         "https://source.ecoversities.org/Ecoversity:Cooperativa_Agroecologica_Las_Ca%C3%B1adas", "Conocer la cooperativa"),
    ], ("Voces de Bosque Venado", "Aquí irán los testimonios de quienes ya están en las etapas 1 y 2: " + TBD.format("por recopilar") + ".")),
    cta_visita="Agenda una visita", cta_clusters="Ver clusters disponibles",
    menu="Menú", cerrar="Cerrar", agenda="Agenda", wa_label="Escríbenos por WhatsApp", nav_visita="Visita",
    hero_tag="Agua, energía y comida propias, en el monte de Acanceh.",
    foto_pend="Foto pendiente", f_hero="Camino de sascab entre palmeras y monte",
    f_ceiba="Una ceiba de tronco claro y raíces anchas en medio del monte", f_ceiba_cap="La ceiba, el árbol sagrado maya, en el monte de Yucatán",
    predio_t="El predio completo",
    predio_p="El tablaje mide 7 hectáreas. Las etapas 1 y 2, al oriente, suman 5 hectáreas y ya están vendidas. La etapa 3 ocupa las 2 hectáreas del poniente, con frente a la calle del sur.",
    part_etq="Tu participación", en_etq="Cómo entrar", es_etq="Estructura",
    h1="Agua, energía y comida propias, en el monte.",
    hero_lede=f"Bosque Venado es una comunidad neorural en Acanceh, Yucatán. En la etapa 3 hay {N_LOTES} lotes de 200 m². Puedes comprar desde uno, o un cluster de 2, 4 u 8 con amigos o familia, con caminos de frutales entre ellos y un centro común de energía solar y agua de pozo.",
    plan_cap="Basado en el levantamiento topográfico del tablaje 3735. La distribución es esquemática y puede ajustarse en el proyecto definitivo.",
    d1_t="Predio", d1="7 hectáreas",
    d2_t="Etapa 3, a la venta", d2="2 hectáreas",
    d3_t="Lotes de 200 m²", d3=f"{N_LOTES} en {N_CL} clusters",
    d4_t="Áreas comunes", d4=f"{COMUN} de la etapa",
    lugar_h="Primero el monte, después todo lo demás.",
    lugar_lede="Ya hay vida en el predio: agua de pozo, energía solar y tres construcciones. Lo común se construye entre todos, con poco impacto y fuera de la red.",
    hoy_h="Lo que hay hoy",
    hoy_items=li([
        ("Agua de pozo", "A 27 metros de profundidad"),
        ("Energía solar", "Paneles y baterías en una de las casas habitadas"),
        ("Tres construcciones", "Ubicación en el plano: " + TBD.format("por confirmar")),
        ("Frente a la calle del sur", "Acceso directo a la etapa 3"),
        ("Cerca de Acanceh", "A unos 1.2 km por la calle 19, según el croquis del plano"),
    ]),
    juntos_h="Lo que construimos juntos",
    juntos_items=li([
        ("Calle central de sascab", "Fecha estimada: " + TBD.format("por definir")),
        ("Centro de energía y agua", "Paneles, baterías, pozo y tanque elevado. Fecha estimada: " + TBD.format("por definir")),
        ("Caminos verdes con frutales", "Entre cada cluster. Fecha estimada: " + TBD.format("por definir")),
        ("Bosque agroforestal y vivero", "Fecha estimada: " + TBD.format("por definir")),
        ("Palapa y bodega común", "Fecha estimada: " + TBD.format("por definir")),
    ]),
    vida_h="Lo común es lo que te sostiene.",
    vida_lede="Las amenidades de Bosque Venado no son un club ni una alberca. Son el agua, la energía y la comida que la comunidad produce y cuida en conjunto.",
    pilares=pilares([
        ("Agua", "El pozo ya da agua a 27 metros. Se bombea con energía solar a un tanque elevado y baja por gravedad a los clusters.",
         ["Pozo existente", "Tanque elevado común", "Cada casa puede captar lluvia"], "el pozo y el tanque"),
        ("Energía", "Un centro de paneles y baterías para lo común, y cada casa puede sumar su propio sistema. Sin depender de la red.",
         ["Paneles solares y baterías", "Bombeo de agua solar", "Iluminación de caminos"], "los paneles de la casa habitada"),
        ("Comida", "Entre cluster y cluster corre un camino verde con frutales, y los rincones libres se siembran como bosque agroforestal. La comida queda a pasos de cada casa.",
         ["Chaya, plátano, papaya, pitahaya, limón", "Milpa y huerto común", "Vivero de árboles nativos"], "frutales y milpa"),
    ], "Foto pendiente"),
    sin_show="Autosuficiencia sin show: sin búnker y sin alambre de púas. Agua, energía, comida y vecinos que se conocen.",
    e3_h="La etapa 3, cluster por cluster.",
    e3_lede=f"Dos hectáreas al poniente del predio. Una calle central ondulada de 6 m reparte {N_LOTES} lotes a los dos lados, agrupados en {N_CL} clusters: {POR_TAM[8]} de 8 lotes, {POR_TAM[4]} de 4 y {POR_TAM[2]} de 2. Toca un lote para cotizarlo solo, el chapoteadero de un cluster para cotizarlo completo, o un ícono i para saber qué es cada zona.",
    desliza="Desliza para ver todo el plano.",
    st_disp="Disponible", st_apar="Apartado", st_vend="Vendido",
    z_calle="Calle y huellas", z_agro="Bosque agroforestal", z_energia="Energía", z_agua="Aguada",
    co_h="Cotiza tu lote o tu cluster.",
    co_lede="Precio de preventa: $500 por m², o $100,000 por lote a 60 meses. Un cluster suma sus lotes y mientras más corto el plazo, menor el total. El precio sube 5% cada vez que se venden 4 lotes. Descarga la cotización en PDF o mándanosla por WhatsApp.",
    ficha_vacia="Elige un lote o un cluster en el plano, o cotiza por número de lotes.",
    co_tam="Número de lotes", co_plazo="Plazo",
    pr_eng="Enganche", pr_total="Precio total", pr_m2="Precio por m²", pr_ahorro="Ahorro contra 60 meses",
    co_pdf="Descargar cotización en PDF", co_pedir="Pedir informes",
    pr_th1="Plazo", pr_th2="Mensualidad", pr_th3="Total", pr_th4="Descuento",
    pr_letra="Enganche de $10,000 por lote en todos los plazos. Si liquidas antes, pagas el precio del plazo en que terminas. El precio de preventa sube 5% cada vez que se venden 4 lotes. La cuota de mantenimiento se paga aparte: " + TBD.format("monto por definir") + ". Precios en pesos mexicanos, sin intereses.",
    part_h="Qué te da tu participación, y qué no.",
    part_lede="Tu participación son acciones de una serie de la SAPI de C.V. de La Tokenizadora, representadas por un token. Con ellas recibes el uso vitalicio de uno o varios lotes de 200 m² y voz en cómo se cuida la tierra.",
    si_h="Incluye",
    si_items=li([
        ("Uso vitalicio de tus lotes", "Desde un lote de 200 m², o un cluster de 2, 4 u 8, en la etapa 3"),
        ("Agua, energía y comida comunes", "Pozo, centro solar, caminos verdes y bosque agroforestal, con cuota de mantenimiento"),
        ("Construir en tu cluster", "Tipo, materiales y tamaño según el reglamento: " + TBD.format("por definir")),
        ("Voto en las decisiones sobre la tierra", "Reglas, mejoras y admisión de nuevos miembros"),
        ("Herencia y reventa", "Tu derecho pasa a tus herederos o a quien compre, con admisión por la comunidad"),
    ]),
    no_h="No incluye",
    no_items=li([
        ("Escritura individual", "La tierra es de la sociedad; tu derecho queda en el registro de acciones"),
        ("Desmonte por tu cuenta", "Cualquier claro se decide en común y con permiso"),
        ("Renta o uso comercial", "Regla: " + TBD.format("por definir")),
        ("Promesa de rendimiento o plusvalía", "El valor está en el uso y la comunidad"),
    ]),
    part_nota="Los derechos se fijan en los estatutos, el reglamento de uso y tu contrato. Versión final de los documentos: " + TBD.format("por definir") + ".",
    en_h="Cómo entrar a la comunidad.",
    en_lede="Antes de pagar, nos conocemos. Una comunidad fuerte empieza por elegir bien a quién se suma.",
    pasos=pasos([
        ("Visita el predio", "Recorre el monte, el pozo y los clusters disponibles."),
        ("Conversa con la comunidad", "Hablamos de valores, expectativas y cómo quieres usar el lugar."),
        ("Aparta tu lote", "Recibes estatutos, reglamento y contrato para revisarlos con calma."),
        ("Firma y registro", "Firmas tu contrato y quedas inscrito en el registro de accionistas."),
        ("Recibe tu token", "La Tokenizadora emite tu token y se asignan tus lotes."),
    ]),
    es_h="La tierra, la sociedad y el token.",
    es_lede="Preferimos poner el dinero en agua, energía y comida que en trámites. Pero confiar entre pares no quita el rigor: cada participación está respaldada por acciones.",
    capas=capas([
        ("La tierra", "El predio pertenece a una serie accionaria de la SAPI de C.V. de La Tokenizadora, creada para Bosque Venado. Nadie lo puede dividir ni vender por partes."),
        ("Tu participación", "Son acciones de esa serie, inscritas en el registro de accionistas desde que firmas. Eso te da certeza jurídica inmediata, sin escriturar cada lote ni pagar notaría en cada operación."),
        ("El token", "Representa tus acciones y les da fluidez: puedes heredarlas, darlas en garantía o traspasarlas. No es anónimo: cada cambio de titular lo aprueba la comunidad."),
    ]),
    faq_h="Preguntas frecuentes.",
    faq=faq([
        ("¿Qué significa preventa?", "Que lo común se está construyendo con las primeras participaciones. Por eso el precio es más bajo ahora y sube 5% cada vez que se venden 4 lotes."),
        ("¿Por qué no se escritura cada lote?", "Porque la tierra es de la sociedad y tu derecho vive en tus acciones. Así no hay gastos notariales en cada compra, herencia o traspaso, y tienes certeza jurídica desde que quedas inscrito en el registro de accionistas."),
        ("¿Puedo dar mi participación en garantía?", "Sí, tus acciones pueden darse en garantía en los términos que fijen los estatutos. El token facilita el trámite, pero cualquier cambio de titular pasa por la comunidad."),
        ("¿Puedo comprar un solo lote?", "Sí. Puedes comprar desde un lote de 200 m². Los clusters de 2, 4 u 8 son para quien quiere más espacio o comprar con amigos o familia, con un camino verde de frutales alrededor."),
        ("Si compro un lote de atrás, ¿cómo entro?", "Cada lote de atrás tiene paso propio: por el camino verde que corre junto a su cluster, por la servidumbre de 3 m de los clusters de 8, por la calle del sur o por el centro de energía y agua. En el plano, cada lote dice cuál es su acceso."),
        ("¿Cómo entro en auto a los lotes de atrás?", "Por el camino verde que corre junto a cada cluster: tiene dos huellas de concreto para entrar a vuelta de rueda. En los clusters de 8 hay además una servidumbre de paso de 3 m al centro."),
        ("¿Puedo comprar un cluster con amigos o familia?", "Sí. Un cluster de 4 u 8 se puede compartir; cada quien tiene sus acciones y el reglamento fija el paso y el uso dentro del cluster."),
        ("¿Puedo construir?", "Sí, según el reglamento de construcción, que fija tipo, materiales y tamaño: " + TBD.format("por definir") + "."),
        ("¿Puedo vender o heredar mi participación?", "Sí. El derecho de uso se transmite con tus acciones, por herencia o por venta. Quien la reciba pasa por el mismo proceso de admisión que tú."),
        ("¿Hay agua y luz?", "Hay un pozo con agua a 27 metros. No hay red eléctrica: una de las casas habitadas funciona con paneles solares y baterías, y el centro de energía y agua da servicio a lo común."),
        ("¿Qué pasa con las etapas 1 y 2?", "Ya están vendidas. La etapa 3 es la única que está a la venta."),
        ("¿Cuánto es la cuota de mantenimiento?", "Cubre la calle, el agua, la energía común y el cuidado del bosque. Monto: " + TBD.format("por definir") + "."),
        ("¿Qué pasa si dejo de pagar?", "Lo que pasa con tus pagos y tu participación se fija en el contrato: " + TBD.format("regla por definir") + "."),
    ]),
    vi_h="Agenda una visita.",
    vi_lede="Cuéntanos quién eres y qué buscas. Te escribimos para coordinar el día y la hora.",
    vi_correo="Correo",
    form_action="/gracias",
    f_honey="No llenes este campo", f_nombre="Nombre", f_email="Correo",
    f_cluster="Lote o cluster que te interesa", f_cluster_ph="Opcional, por ejemplo lote 23 o cluster C",
    f_plazo="Plazo que te interesa",
    f_plazo_opts='<option value="">Aún no sé</option><option>60 meses</option><option>48 meses</option><option>36 meses</option><option>24 meses</option><option>12 meses</option><option>Contado</option>',
    f_uso="¿Cómo te imaginas usar el lugar?",
    f_uso_ayuda="Fines de semana, temporadas, vivir ahí, con amigos o familia…",
    f_enviar="Enviar solicitud de visita",
    pie_1="<strong>Bosque Venado</strong><br>Tablaje 3735, Seyé, Yucatán.<br>Tokenizado por La Tokenizadora.",
    pie_2="Esta página es informativa y no constituye una oferta pública de valores ni promesa de rendimiento. Las participaciones se ofrecen solo de forma privada, previa visita y admisión. Autorizaciones y documentos legales: " + TBD.format("por definir") + ". <a href=\"#\">Aviso de privacidad</a> (" + TBD.format("por definir") + ").",
    JS=dict(
        locale="es-MX", estado_url="estado.json", correo=CORREO,
        meses="{n} meses", contado="Contado", na="N/A", mens_etq="{n} mensualidades", unico="Pago único", al_mes="al mes", incluido="Incluido",
        cluster="Cluster", lote="Lote", lotes="lotes", lotes_t="Lotes", de="de", tam="Tamaño", medidas="Medidas", acceso_t="Acceso",
        acceso={"calle": "Frente a la calle central", "camino": "Por el camino verde", "serv": "Por la servidumbre de paso", "sur": "Por la calle del sur", "energia": "Por el centro de energía y agua"},
        ver_cl="Cotizar el cluster {c} completo ({n} lotes)",
        stc={"disponible": "Disponible completo", "parcial": "Con lotes disponibles", "apartado": "Apartado", "vendido": "Vendido"}, sup="Superficie", frente="Frente a la calle", fondo="Fondo", ubic="Ubicación", estado="Estado",
        banda={"poniente": "Lado poniente de la calle", "oriente": "Lado oriente de la calle"},
        st={"disponible": "Disponible", "apartado": "Apartado", "vendido": "Vendido"},
        cuenta="{d} de {t} lotes disponibles; {c} clusters completos.", quitar="Quitar selección", ficha_vacia="Elige un lote o un cluster en el plano, o cotiza por número de lotes.",
        t_cap="Todos los plazos para {u} ({m})", total_c="total",
        wa_txt="Hola, me interesa Bosque Venado.",
        co_plazo="Plazo", pr_eng="Enganche", pr_total="Precio total", pr_m2="Precio por m²", pr_ahorro="Ahorro contra 60 meses",
        pr_th1="Plazo", pr_th2="Mensualidad", pr_th3="Total", pr_th4="Descuento", mens_pdf="Mensualidad ({n} pagos)",
        pdf_sub="Cotización de la etapa 3. Tablaje 3735, Seyé, Yucatán.", pdf_folio="Folio", pdf_sin="{u}, por asignar",
        pdf_mapa="Etapa 3", pdf_calle="Calle al sur", pdf_contacto="Contacto", pdf_archivo="Cotizacion-Bosque-Venado",
        pdf_notas="Enganche de $10,000 por lote. Si liquidas antes, pagas el precio del plazo en que terminas. Precios en pesos mexicanos, sin intereses. La cuota de mantenimiento se paga aparte. El cluster se reserva solo con el apartado firmado; esta cotización no lo aparta. El precio de preventa sube 5% cada vez que se venden 4 lotes. Cuota de mantenimiento: por definir.",
        pdf_legal="Documento informativo. No constituye una oferta pública de valores ni promesa de rendimiento. Las participaciones son acciones de una serie de la SAPI de C.V. de La Tokenizadora y se ofrecen solo de forma privada, previa visita y admisión.",
        tramo_txt="Preventa, tramo {n}: {p} por m². Quedan {q} {l} a este precio; después sube 5%.", lote1="lote",
        pdf_gen="Generando el PDF…", pdf_ok="Listo. Revisa tus descargas.", pdf_err="No se pudo generar el PDF. Revisa tu conexión e inténtalo de nuevo.",
        vi_correo="Correo",
        info={
            "calle": {"t": "Calle central", "d": "6 m de sascab compactado, doble sentido a vuelta de rueda. La curva baja la velocidad y el ruido. Sale a la calle del sur."},
            "corredor": {"t": "Camino verde", "d": "Corredor de 4 m entre clusters. Dos huellas de concreto para entrar en auto a los lotes de atrás, y frutales de porte bajo a los lados. Es el sendero de recolección."},
            "energia": {"t": "Centro de energía y agua", "d": "Paneles solares, baterías y el pozo con su tanque elevado. Puede alojar un estacionamiento compartido."},
            "aguada": {"t": "Aguada", "d": "Un estanque que guarda el agua de lluvia, riega los frutales y da refugio a aves y fauna. Ubicación y tamaño ilustrativos."},
            "agro": {"t": "Bosque agroforestal", "d": "Los rincones que no completan un cluster se siembran como huerto común: frutales, milpa y árboles nativos como el maculís, el flamboyán y la lluvia de oro."},
            "cluster": {"t": "Cluster", "d": "Grupo de 2, 4 u 8 lotes de 200 m² para comprar con amigos o familia. En el cruce de sus lotes hay un chapoteadero con la letra del cluster; tócalo para cotizarlo completo."},
            "serv": {"t": "Servidumbre de paso", "d": "Franja de 3 m dentro de los clusters de 8 para que cada lote de atrás tenga entrada, aunque el cluster lo compartan varias familias. No cambia la superficie de los lotes."},
        },
        err_nombre="Escribe tu nombre.", err_email="Escribe un correo válido, por ejemplo nombre@dominio.com."),
)

EN = dict(
    lang="en", alt_lang="es", alt_label="Español", alt_href="../",
    title="Bosque Venado, Acanceh, Yucatán",
    desc=f"A neo-rural community in the forest near Acanceh, Yucatán, with well water, solar power and its own food. {N_LOTES} lots of 200 m², sold one at a time or in clusters of 2, 4 and 8, with lifetime use through a share series tokenized by La Tokenizadora.",
    draft='Design draft. Items marked <span class="tbd">like this</span> are still to be defined.',
    home_label="Bosque Venado, home", nav_label="Sections",
    nav_lugar="The land", nav_vida="Water, power and food", nav_etapa="Phase 3", nav_cotiza="Get a quote", nav_faq="FAQ",
    canon="https://bosquevenado.com/en/", kicker="Phase 3 pre-sale",
    co_etq="The community",
    com_h="An intentional community, not a subdivision.",
    com_lede="Bosque Venado exists to build community around a solidarity economy and resilience in an uncertain future. We want water, power, food and real ties between neighbors. We are in pre-sale: every stake funds what we share.",
    com_items=cuatro([
        ("Water, power and food", "The basics, solved together: well, sun and planting. It is what keeps us going if things outside fail."),
        ("Solidarity economy", "We share tools, work and harvests. We would rather put money into the land and the community than into paperwork."),
        ("Trust among peers", "We all know each other. The community approves who joins and who leaves; no one takes part anonymously."),
        ("Legal rigor", "Trust does not mean improvising. Everything is tokenized and backed by shares in a series of a SAPI de C.V., with bylaws and rules."),
    ]),
    reg_etq="Living together", reg_h="Community rules, in outline.",
    reg_lede="The basics for living together. The final version is written and voted on as a community: " + TBD.format("to be defined") + ".",
    reglas=reglas([
        ("Joining and leaving", ["A visit and a conversation before joining", "The community approves every new member", "Heirs and buyers go through the same admission"]),
        ("Decisions", ["Regular members' assembly", "Rules and improvements are voted on", "Voting method: " + TBD.format("to be defined")]),
        ("Forest and planting", ["No clearing without a shared agreement", "Native species and fruit trees", "The green lanes belong to everyone"]),
        ("Building", ["Materials and heights set by the rules", "The easement is respected", "Maximum built area: " + TBD.format("to be defined")]),
        ("Water and power", ["Careful use of the well and tank", "Each house can add its own system", "Shared systems are kept up with a fee"]),
        ("Daily life", ["Quiet at night", "Pets in their owners' care", "Visitors announced to the community"]),
        ("Shared work", ["Work days in the garden and lanes", "Shared harvests are divided", "Everyone brings their own skills"]),
        ("Fees and conflicts", ["Maintenance fee: " + TBD.format("to be defined"), "Talk first, then mediation", "Non-payment rule: " + TBD.format("to be defined")]),
    ]),
    qs_etq="Who we are", qs_h="The people behind Bosque Venado.",
    qs_lede="The founders and first members of the community. Each one brings their own skills to what we share.",
    gente=gente([
        ("Juan Carlos", "Founder. Bio: " + TBD.format("to be defined")),
        ("María Cecilia", "Founder. Bio: " + TBD.format("to be defined")),
        ("Alejandro", "Founder. Bio: " + TBD.format("to be defined")),
        ("And more members", "The families of phases 1 and 2 have been part of the community from the start."),
    ], "Photo pending"),
    in_etq="References", in_h="Communities that inspire us.",
    in_lede="These are not testimonials: they are real projects in Mexico that have shown for years that this way of living works.",
    referentes=referentes([
        ("Huehuecoyotl", "Sierra del Tepozteco, Morelos. Since 1982.",
         "An ecovillage where each family built its own house and everyone together built the road, rainwater harvesting, a theater and the farmland. The land is managed in common, by agreement among its members.",
         "https://ecovillage.org/resources-library/article/what-is-our-ecovillage/", "Read their story"),
        ("Las Cañadas", "Near Huatusco, Veracruz.",
         "An agroecology cooperative and permaculture center that cares for one of the last islands of cloud forest in central Veracruz, with a food forest and agroecology training.",
         "https://source.ecoversities.org/Ecoversity:Cooperativa_Agroecologica_Las_Ca%C3%B1adas", "Learn about the cooperative"),
    ], ("Voices of Bosque Venado", "Testimonials from the people already in phases 1 and 2 will go here: " + TBD.format("to be collected") + ".")),
    cta_visita="Book a visit", cta_clusters="See available clusters",
    menu="Menu", cerrar="Close", agenda="Book", wa_label="Message us on WhatsApp", nav_visita="Visit",
    hero_tag="Your own water, power and food, in the forest near Acanceh.",
    foto_pend="Photo pending", f_hero="A sascab road between palms and forest",
    f_ceiba="A pale-trunked ceiba with wide roots in the forest", f_ceiba_cap="The ceiba, the sacred Maya tree, in the Yucatán forest",
    predio_t="The whole parcel",
    predio_p="The parcel covers 7 hectares. Phases 1 and 2, on the east side, add up to 5 hectares and are already sold. Phase 3 takes the 2 western hectares, facing the south street.",
    part_etq="Your stake", en_etq="How to join", es_etq="Structure",
    h1="Your own water, power and food, in the forest.",
    hero_lede=f"Bosque Venado is a neo-rural community in Acanceh, Yucatán. Phase 3 has {N_LOTES} lots of 200 m². You can buy a single lot, or a cluster of 2, 4 or 8 with friends or family, with fruit-tree lanes between them and a shared solar power and well water hub.",
    plan_cap="Based on the topographic survey of parcel 3735. The layout is schematic and may be adjusted in the final project.",
    d1_t="Parcel", d1="7 hectares",
    d2_t="Phase 3, for sale", d2="2 hectares",
    d3_t="Lots of 200 m²", d3=f"{N_LOTES} in {N_CL} clusters",
    d4_t="Common areas", d4=f"{COMUN} of the phase",
    lugar_h="The forest first, everything else after.",
    lugar_lede="There is already life on the land: well water, solar power and three buildings. Shared infrastructure is built together, with a light footprint and off the grid.",
    hoy_h="What is there today",
    hoy_items=li([
        ("Well water", "Reached at 27 meters"),
        ("Solar power", "Panels and batteries in one of the lived-in houses"),
        ("Three buildings", "Location on the plan: " + TBD.format("to be confirmed")),
        ("Frontage on the south street", "Direct access to phase 3"),
        ("Close to Acanceh", "About 1.2 km along Calle 19, per the survey sketch"),
    ]),
    juntos_h="What we build together",
    juntos_items=li([
        ("Central sascab street", "Estimated date: " + TBD.format("to be defined")),
        ("Power and water hub", "Panels, batteries, well and elevated tank. Estimated date: " + TBD.format("to be defined")),
        ("Green lanes with fruit trees", "Between every cluster. Estimated date: " + TBD.format("to be defined")),
        ("Food forest and nursery", "Estimated date: " + TBD.format("to be defined")),
        ("Shared palapa and storage", "Estimated date: " + TBD.format("to be defined")),
    ]),
    vida_h="What we share is what sustains you.",
    vida_lede="The amenities at Bosque Venado are not a clubhouse or a pool. They are the water, power and food the community produces and looks after together.",
    pilares=pilares([
        ("Water", "The well already gives water at 27 meters. It is pumped with solar power to an elevated tank and flows by gravity to the clusters.",
         ["Existing well", "Shared elevated tank", "Every house can harvest rain"], "the well and the tank"),
        ("Power", "A hub of panels and batteries for shared needs, and every house can add its own system. No grid needed.",
         ["Solar panels and batteries", "Solar water pumping", "Lane lighting"], "the panels on the lived-in house"),
        ("Food", "A green lane with fruit trees runs between clusters, and the spare corners are planted as a food forest. Food is a few steps from every house.",
         ["Chaya, banana, papaya, dragon fruit, lime", "Milpa and shared garden", "Native tree nursery"], "fruit trees and milpa"),
    ], "Photo pending"),
    sin_show="Self-reliance without the show: no bunker, no barbed wire. Water, power, food and neighbors who know each other.",
    e3_h="Phase 3, cluster by cluster.",
    e3_lede=f"Two hectares on the west side of the parcel. A winding 6 m central street serves {N_LOTES} lots on both sides, grouped in {N_CL} clusters: {POR_TAM[8]} of 8 lots, {POR_TAM[4]} of 4 and {POR_TAM[2]} of 2. Tap a lot to get a quote for it, a cluster's wading pool to quote the whole cluster, or an i icon to learn what each area is.",
    desliza="Swipe to see the whole plan.",
    st_disp="Available", st_apar="Reserved", st_vend="Sold",
    z_calle="Street and wheel tracks", z_agro="Food forest", z_energia="Power", z_agua="Rain pond",
    co_h="Get a quote for your lot or cluster.",
    co_lede="Pre-sale price: MXN $500 per m², or $100,000 per lot over 60 months. A cluster adds up its lots, and the shorter the term, the lower the total. The price goes up 5% every time 4 lots are sold. Download the quote as a PDF or send it to us on WhatsApp.",
    ficha_vacia="Choose a lot or a cluster on the plan, or get a quote by number of lots.",
    co_tam="Number of lots", co_plazo="Term",
    pr_eng="Down payment", pr_total="Total price", pr_m2="Price per m²", pr_ahorro="Savings vs. 60 months",
    co_pdf="Download quote as PDF", co_pedir="Ask about it",
    pr_th1="Term", pr_th2="Monthly", pr_th3="Total", pr_th4="Discount",
    pr_letra="MXN $10,000 down payment per lot on every term. If you pay off early, you pay the price of the term in which you finish. The pre-sale price goes up 5% every time 4 lots are sold. The maintenance fee is separate: " + TBD.format("amount to be defined") + ". Prices in Mexican pesos, interest-free.",
    part_h="What your stake gives you, and what it doesn't.",
    part_lede="Your stake is a set of shares in a series of La Tokenizadora's SAPI de C.V., represented by a token. It gives you lifetime use of one or more 200 m² lots and a say in how the land is cared for.",
    si_h="Included",
    si_items=li([
        ("Lifetime use of your lots", "From a single 200 m² lot, or a cluster of 2, 4 or 8, in phase 3"),
        ("Shared water, power and food", "Well, solar hub, green lanes and food forest, with a maintenance fee"),
        ("Building on your cluster", "Type, materials and size set by the rules: " + TBD.format("to be defined")),
        ("A vote on decisions about the land", "Rules, improvements and admission of new members"),
        ("Inheritance and resale", "Your right passes to your heirs or to a buyer, with admission by the community"),
    ]),
    no_h="Not included",
    no_items=li([
        ("An individual deed", "The land belongs to the company; your right is recorded in the share register"),
        ("Clearing land on your own", "Any clearing is decided together and with permits"),
        ("Renting or commercial use", "Rule: " + TBD.format("to be defined")),
        ("A promise of returns or appreciation", "The value is in the use and the community"),
    ]),
    part_nota="Your rights are set by the bylaws, the use rules and your contract. Final documents: " + TBD.format("to be defined") + ".",
    en_h="How to join the community.",
    en_lede="Before any payment, we get to know each other. A strong community starts with choosing well who joins.",
    pasos=pasos([
        ("Visit the land", "Walk the forest, the well and the available clusters."),
        ("Talk with the community", "We discuss values, expectations and how you want to use the place."),
        ("Reserve your lot", "You receive the bylaws, rules and contract to review at your own pace."),
        ("Sign and register", "You sign your contract and are entered in the share register."),
        ("Receive your token", "La Tokenizadora issues your token and your lots are assigned."),
    ]),
    es_h="The land, the company and the token.",
    es_lede="We would rather put money into water, power and food than into paperwork. But trust among peers does not mean giving up rigor: every stake is backed by shares.",
    capas=capas([
        ("The land", "The property belongs to a share series of La Tokenizadora's SAPI de C.V., created for Bosque Venado. No one can split it up or sell it in pieces."),
        ("Your stake", "It is a set of shares in that series, entered in the share register as soon as you sign. That gives you legal certainty right away, without a deed for each lot or notary fees on every transaction."),
        ("The token", "It represents your shares and makes them easy to move: you can pass them on, pledge them as collateral or transfer them. It is not anonymous: the community approves every change of holder."),
    ]),
    faq_h="Frequently asked questions.",
    faq=faq([
        ("What does pre-sale mean?", "That the shared infrastructure is being built with the first stakes. That is why the price is lower now and goes up 5% every time 4 lots are sold."),
        ("Why is there no deed for each lot?", "Because the land belongs to the company and your right lives in your shares. That means no notary fees on each purchase, inheritance or transfer, and legal certainty from the moment you are entered in the share register."),
        ("Can I pledge my stake as collateral?", "Yes, your shares can be pledged on the terms set by the bylaws. The token makes it easier, but any change of holder goes through the community."),
        ("Can I buy a single lot?", "Yes. You can buy from one 200 m² lot. Clusters of 2, 4 or 8 are for people who want more space or to buy with friends or family, with a green lane of fruit trees around them."),
        ("If I buy a back lot, how do I get in?", "Every back lot has its own access: through the green lane next to its cluster, the 3 m easement in clusters of 8, the south street or the power and water hub. On the plan, each lot shows its access."),
        ("How do I drive to the back lots?", "Along the green lane next to each cluster: it has two concrete wheel tracks for driving in at walking pace. Clusters of 8 also have a 3 m easement through the middle."),
        ("Can I buy a cluster with friends or family?", "Yes. A cluster of 4 or 8 can be shared; each person holds their own shares and the rules set access and use inside the cluster."),
        ("Can I build?", "Yes, under the building rules, which set type, materials and size: " + TBD.format("to be defined") + "."),
        ("Can I sell or pass on my stake?", "Yes. The right of use transfers with your shares, by inheritance or sale. The new holder goes through the same admission process you did."),
        ("Is there water and power?", "There is a well with water at 27 meters. There is no grid connection: one of the lived-in houses runs on solar panels and batteries, and the power and water hub serves the shared areas."),
        ("What about phases 1 and 2?", "They are already sold. Phase 3 is the only one for sale."),
        ("How much is the maintenance fee?", "It covers the street, water, shared power and forest care. Amount: " + TBD.format("to be defined") + "."),
        ("What happens if I stop paying?", "What happens to your payments and your stake is set in the contract: " + TBD.format("rule to be defined") + "."),
    ]),
    vi_h="Book a visit.",
    vi_lede="Tell us who you are and what you are looking for. We will write to set a day and time.",
    vi_correo="Email",
    form_action="/en/gracias",
    f_honey="Leave this field empty", f_nombre="Name", f_email="Email",
    f_cluster="Lot or cluster you are interested in", f_cluster_ph="Optional, for example lot 23 or cluster C",
    f_plazo="Term you are interested in",
    f_plazo_opts='<option value="">Not sure yet</option><option>60 months</option><option>48 months</option><option>36 months</option><option>24 months</option><option>12 months</option><option>Cash</option>',
    f_uso="How do you picture using the place?",
    f_uso_ayuda="Weekends, seasons, living there, with friends or family…",
    f_enviar="Send visit request",
    pie_1="<strong>Bosque Venado</strong><br>Parcel 3735, Seyé, Yucatán, Mexico.<br>Tokenized by La Tokenizadora.",
    pie_2="This page is for information only and is not a public offering of securities or a promise of returns. Stakes are offered privately only, after a visit and admission. Permits and legal documents: " + TBD.format("to be defined") + ". <a href=\"#\">Privacy notice</a> (" + TBD.format("to be defined") + ").",
    JS=dict(
        locale="en-US", estado_url="../estado.json", correo=CORREO,
        meses="{n} months", contado="Cash", na="N/A", mens_etq="{n} monthly payments", unico="Single payment", al_mes="per month", incluido="Included",
        cluster="Cluster", lote="Lot", lotes="lots", lotes_t="Lots", de="of", tam="Size", medidas="Size", acceso_t="Access",
        acceso={"calle": "Facing the central street", "camino": "Through the green lane", "serv": "Through the easement", "sur": "From the south street", "energia": "Through the power and water hub"},
        ver_cl="Quote the whole cluster {c} ({n} lots)",
        stc={"disponible": "Fully available", "parcial": "Some lots available", "apartado": "Reserved", "vendido": "Sold"}, sup="Area", frente="Street frontage", fondo="Depth", ubic="Location", estado="Status",
        banda={"poniente": "West side of the street", "oriente": "East side of the street"},
        st={"disponible": "Available", "apartado": "Reserved", "vendido": "Sold"},
        cuenta="{d} of {t} lots available; {c} full clusters.", quitar="Clear selection", ficha_vacia="Choose a lot or a cluster on the plan, or get a quote by number of lots.",
        t_cap="Every term for {u} ({m})", total_c="total",
        wa_txt="Hi, I am interested in Bosque Venado.",
        co_plazo="Term", pr_eng="Down payment", pr_total="Total price", pr_m2="Price per m²", pr_ahorro="Savings vs. 60 months",
        pr_th1="Term", pr_th2="Monthly", pr_th3="Total", pr_th4="Discount", mens_pdf="Monthly payment ({n} payments)",
        pdf_sub="Phase 3 quote. Parcel 3735, Seyé, Yucatán, Mexico.", pdf_folio="Ref.", pdf_sin="{u}, to be assigned",
        pdf_mapa="Phase 3", pdf_calle="South street", pdf_contacto="Contact", pdf_archivo="Bosque-Venado-quote",
        pdf_notas="MXN $10,000 down payment per lot. If you pay off early, you pay the price of the term in which you finish. Prices in Mexican pesos, interest-free. The maintenance fee is separate. A cluster is reserved only with a signed reservation; this quote does not reserve it. The pre-sale price goes up 5% every time 4 lots are sold. Maintenance fee: to be defined.",
        pdf_legal="For information only. Not a public offering of securities or a promise of returns. Stakes are shares in a series of La Tokenizadora's SAPI de C.V. and are offered privately only, after a visit and admission.",
        tramo_txt="Pre-sale, tier {n}: {p} per m². {q} {l} left at this price; then it goes up 5%.", lote1="lot",
        pdf_gen="Generating the PDF…", pdf_ok="Done. Check your downloads.", pdf_err="The PDF could not be generated. Check your connection and try again.",
        vi_correo="Email",
        info={
            "calle": {"t": "Central street", "d": "6 m of compacted sascab, two-way at walking pace. The curve slows cars and keeps noise down. It connects to the south street."},
            "corredor": {"t": "Green lane", "d": "A 4 m lane between clusters. Two concrete wheel tracks for driving to the back lots, with low fruit trees on both sides. It is the harvest path."},
            "energia": {"t": "Power and water hub", "d": "Solar panels, batteries and the well with its elevated tank. It can also hold shared parking."},
            "aguada": {"t": "Rain pond", "d": "A pond that stores rainwater, waters the fruit trees and gives shelter to birds and wildlife. Location and size are illustrative."},
            "agro": {"t": "Food forest", "d": "Corners too small for a cluster are planted as a shared garden: fruit trees, milpa and trees such as maculís, flame tree and golden shower."},
            "cluster": {"t": "Cluster", "d": "A group of 2, 4 or 8 lots of 200 m² to buy with friends or family. Where its lots meet there is a wading pool with the cluster's letter; tap it to quote the whole cluster."},
            "serv": {"t": "Easement", "d": "A 3 m strip inside clusters of 8 so every back lot has access, even when several families share the cluster. It does not change lot areas."},
        },
        err_nombre="Enter your name.", err_email="Enter a valid email, for example name@domain.com."),
)

GRACIAS = {
    "es": ("es-MX", "Solicitud recibida, Bosque Venado", "Recibimos tu solicitud de visita.",
           "Te escribimos en los próximos días para coordinar el día y la hora del recorrido.", "/", "Volver a Bosque Venado"),
    "en": ("en", "Request received, Bosque Venado", "We received your visit request.",
           "We will write in the next few days to set a day and time for the tour.", "/en/", "Back to Bosque Venado"),
}

GR_TPL = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="robots" content="noindex, nofollow">
<link href="https://fonts.googleapis.com/css2?family=Alegreya:wght@800&family=Alegreya+Sans:wght@400;700&display=swap" rel="stylesheet">
<style>body{{margin:0;background:#E8EAE2;color:#18321F;font-family:"Alegreya Sans",system-ui,sans-serif;font-size:1.15rem;line-height:1.6;display:grid;place-items:center;min-height:100vh;padding:24px;box-sizing:border-box}}
main{{max-width:34rem}}h1{{font-family:"Alegreya",Georgia,serif;font-weight:800;font-size:clamp(2.2rem,6vw,3.4rem);line-height:1.05;margin:0 0 .5em}}
a{{display:inline-block;margin-top:1em;background:#18321F;color:#E8EAE2;text-decoration:none;font-weight:700;padding:.8em 1.3em;border-radius:999px}}
a:focus-visible{{outline:3px solid #0F5E66;outline-offset:3px}}</style></head>
<body><main><h1>{h1}</h1><p>{p}</p><a href="{href}">{back}</a></main></body></html>
"""


def render(t, key):
    tpl = (ROOT / "src" / "template.html").read_text()
    data = dict(t)
    data["PLANO_GENERAL"] = GEO[key]["general"]
    data["LOGO"] = LOGO
    data["IMG"] = "img/" if key == "es" else "../img/"
    data["PLANO_DETALLE"] = GEO[key]["detalle"]
    data["JS"] = json.dumps(t["JS"], ensure_ascii=False)
    data["DATOS"] = json.dumps(DAT, separators=(",", ":"))
    estado = json.loads((ROOT / "estado.json").read_text())
    data["ESTADO"] = json.dumps({"lotes": estado.get("lotes", {}), "clusters": estado.get("clusters", {})})
    data["CORREO_HTML"] = f'<a href="mailto:{CORREO}">{CORREO}</a>' if CORREO else TBD.format("por definir" if key == "es" else "to be defined")
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(data[m.group(1)]), tpl)
    left = re.findall(r"\{\{\w+\}\}", out)
    assert not left, left
    return out


def main():
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(render(ES, "es"))
    (ROOT / "en" / "index.html").write_text(render(EN, "en"))
    for key, path in (("es", ROOT / "gracias.html"), ("en", ROOT / "en" / "gracias.html")):
        lang, title, h1, p, href, back = GRACIAS[key]
        path.write_text(GR_TPL.format(lang=lang, title=title, h1=h1, p=p, href=href, back=back))
    print(json.dumps({"lotes": N_LOTES, "clusters": N_CL, "por_tamano": POR_TAM, "comun": COMUN}, indent=1))


if __name__ == "__main__":
    main()
