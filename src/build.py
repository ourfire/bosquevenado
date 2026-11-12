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
CORREO = ""  # correo de contacto; mientras esté vacío se muestra "por definir"
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
N_LOTES = DAT["lotes"]
N_CL = len(DAT["clusters"])
COMUN = f'{DAT["comun"] / DAT["G"]["area"] * 100:.0f}%'
POR_TAM = {t: sum(1 for c in DAT["clusters"] if c["size"] == t) for t in (8, 4, 2)}


def li(items):
    return "".join(f"<li>{a}<small>{b}</small></li>" for a, b in items)


def pasos(items):
    return "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in items)


def capas(items):
    return "".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in items)


LOGO = ('<svg viewBox="0 0 92 70" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
        '<rect x=".8" y=".8" width="90.4" height="68.4"/><path d="M16 69V32M31 69V12M46 69V38M61 69V20M76 69V44"/></svg>')


def pilares(items, pend):
    out = []
    for a, b, xs, foto in items:
        lis = "".join(f"<li>{x}</li>" for x in xs)
        out.append(f'<article class="panel"><div class="foto" role="img" aria-label="{foto}"><span class="pend">{pend}: {foto}</span></div>'
                   f'<div class="txt"><h3>{a}</h3><p>{b}</p><ul class="lista">{lis}</ul></div></article>')
    return "".join(out)


def faq(items):
    return "".join(f"<details><summary>{a}</summary><p>{b}</p></details>" for a, b in items)


ES = dict(
    lang="es-MX", alt_lang="en", alt_label="English", alt_href="en/",
    title="Bosque Venado, Acanceh, Yucatán",
    desc=f"Comunidad neorural en el monte de Acanceh, Yucatán, con agua de pozo, energía solar y comida propia. {N_LOTES} lotes de 200 m² en clusters de 2, 4 y 8, con uso vitalicio a través de una serie accionaria tokenizada por La Tokenizadora.",
    draft='Borrador de diseño. Los datos marcados <span class="tbd">así</span> están por definir.',
    home_label="Bosque Venado, inicio", nav_label="Secciones",
    nav_lugar="El lugar", nav_vida="Agua, energía y comida", nav_etapa="La etapa 3", nav_cotiza="Cotiza", nav_faq="Preguntas",
    cta_visita="Agenda una visita", cta_clusters="Ver clusters disponibles",
    menu="Menú", cerrar="Cerrar", agenda="Agenda", wa_label="Escríbenos por WhatsApp", nav_visita="Visita",
    hero_tag="Agua, energía y comida propias, en el monte de Acanceh.",
    foto_pend="Foto pendiente", f_hero="Camino de sascab entre palmeras y monte",
    f_ceiba="Una ceiba de tronco claro y raíces anchas en medio del monte", f_ceiba_cap="La ceiba, el árbol sagrado maya, en el monte de Yucatán",
    predio_t="El predio completo",
    predio_p="El tablaje mide 7 hectáreas. Las etapas 1 y 2, al oriente, suman 5 hectáreas y ya están vendidas. La etapa 3 ocupa las 2 hectáreas del poniente, con frente a la calle del sur.",
    part_etq="Tu participación", en_etq="Cómo entrar", es_etq="Estructura",
    h1="Agua, energía y comida propias, en el monte.",
    hero_lede=f"Bosque Venado es una comunidad neorural en Acanceh, Yucatán. En la etapa 3 hay {N_LOTES} lotes de 200 m² agrupados en clusters de 2, 4 y 8, con caminos de frutales entre ellos y un centro común de energía solar y agua de pozo.",
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
    e3_lede=f"Dos hectáreas al poniente del predio. Una calle central ondulada de 6 m reparte {N_CL} clusters a los dos lados: {POR_TAM[8]} de 8 lotes, {POR_TAM[4]} de 4 y {POR_TAM[2]} de 2. Toca un cluster para cotizarlo, o un ícono i para saber qué es cada zona.",
    desliza="Desliza para ver todo el plano.",
    st_disp="Disponible", st_apar="Apartado", st_vend="Vendido",
    z_calle="Calle y huellas", z_agro="Bosque agroforestal", z_energia="Energía y agua",
    co_h="Cotiza tu cluster.",
    co_lede="Cada lote de 200 m² cuesta $100,000 a 60 meses, o $500 por m². Un cluster suma sus lotes, y mientras más corto el plazo, menor el precio total. Descarga la cotización en PDF o mándanosla por WhatsApp.",
    ficha_vacia="Elige un cluster en el plano, o cotiza por tamaño.",
    co_tam="Tamaño del cluster", co_plazo="Plazo",
    pr_eng="Enganche", pr_total="Precio total", pr_m2="Precio por m²", pr_ahorro="Ahorro contra 60 meses",
    co_pdf="Descargar cotización en PDF", co_pedir="Pedir este cluster",
    pr_th1="Plazo", pr_th2="Mensualidad", pr_th3="Total", pr_th4="Descuento",
    pr_letra="Enganche de $10,000 por lote en todos los plazos. Si liquidas antes, pagas el precio del plazo en que terminas. Precios de la etapa 3, vigentes hasta " + TBD.format("fecha por definir") + ". La cuota de mantenimiento se paga aparte: " + TBD.format("monto por definir") + ". Precios en pesos mexicanos, sin intereses.",
    part_h="Qué te da tu participación, y qué no.",
    part_lede="Tu participación son acciones de una serie de la SAPI de C.V. de La Tokenizadora, representadas por un token. Con ellas recibes el uso vitalicio de un cluster de 2, 4 u 8 lotes y voz en cómo se cuida la tierra.",
    si_h="Incluye",
    si_items=li([
        ("Uso vitalicio de tu cluster", "De 2, 4 u 8 lotes de 200 m², en la etapa 3"),
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
        ("Aparta tu cluster", "Recibes estatutos, reglamento y contrato para revisarlos con calma."),
        ("Firma y registro", "Firmas tu contrato y quedas inscrito en el registro de accionistas."),
        ("Recibe tu token", "La Tokenizadora emite tu token y se asigna tu cluster."),
    ]),
    es_h="La tierra, la sociedad y el token.",
    es_lede="Tres piezas que se respaldan entre sí, para que tu participación sea clara hoy y siga clara si algo falla.",
    capas=capas([
        ("La tierra", "El predio pertenece a una serie accionaria de la SAPI de C.V. de La Tokenizadora, creada para Bosque Venado. Nadie lo puede dividir ni vender por partes."),
        ("Tu participación", "Son acciones de esa serie. El registro de accionistas es el documento que manda, y ahí se liga tu cluster."),
        ("El token", "La Tokenizadora tokeniza cada participación. Tu token es tu llave, y si un día falla la red, el padrón y el reglamento existen también en papel."),
    ]),
    faq_h="Preguntas frecuentes.",
    faq=faq([
        ("¿Por qué clusters y no lotes sueltos?", "Cada cluster tiene una hilera de lotes al frente, sobre la calle, y otra atrás, junto al camino verde. Al comprarse juntos, ningún lote queda sin entrada, y entre clusters queda espacio para los frutales."),
        ("¿Cómo entro en auto a los lotes de atrás?", "Por el camino verde que corre junto a cada cluster: tiene dos huellas de concreto para entrar a vuelta de rueda. En los clusters de 8 hay además una servidumbre de paso de 3 m al centro."),
        ("¿Puedo comprar un cluster con amigos o familia?", "Sí. Un cluster de 4 u 8 se puede compartir; cada quien tiene sus acciones y el reglamento fija el paso y el uso dentro del cluster."),
        ("¿Puedo construir?", "Sí, según el reglamento de construcción, que fija tipo, materiales y tamaño: " + TBD.format("por definir") + "."),
        ("¿Recibo escritura?", "No. La tierra es de la sociedad. Tu derecho de uso se liga a tus acciones en el registro de accionistas y a tu contrato."),
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
    f_cluster="Cluster que te interesa", f_cluster_ph="Opcional, por ejemplo 7",
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
        cluster="Cluster", lotes="lotes", de="de", tam="Tamaño", sup="Superficie", frente="Frente a la calle", fondo="Fondo", ubic="Ubicación", estado="Estado",
        banda={"poniente": "Lado poniente de la calle", "oriente": "Lado oriente de la calle"},
        st={"disponible": "Disponible", "apartado": "Apartado", "vendido": "Vendido"},
        cuenta="{d} de {t} clusters disponibles ({l} lotes).", quitar="Cotizar otro tamaño", ficha_vacia="Elige un cluster en el plano, o cotiza por tamaño.",
        t_cap="Todos los plazos para un cluster de {n} lotes ({m})", total_c="total",
        wa_txt="Hola, me interesa Bosque Venado.",
        co_plazo="Plazo", pr_eng="Enganche", pr_total="Precio total", pr_m2="Precio por m²", pr_ahorro="Ahorro contra 60 meses",
        pr_th1="Plazo", pr_th2="Mensualidad", pr_th3="Total", pr_th4="Descuento", mens_pdf="Mensualidad ({n} pagos)",
        pdf_sub="Cotización de la etapa 3. Tablaje 3735, Seyé, Yucatán.", pdf_folio="Folio", pdf_sin="Cluster de {n} lotes, por asignar",
        pdf_mapa="Etapa 3", pdf_calle="Calle al sur", pdf_contacto="Contacto", pdf_archivo="Cotizacion-Bosque-Venado",
        pdf_notas="Enganche de $10,000 por lote. Si liquidas antes, pagas el precio del plazo en que terminas. Precios en pesos mexicanos, sin intereses. La cuota de mantenimiento se paga aparte. El cluster se reserva solo con el apartado firmado; esta cotización no lo aparta. Vigencia y cuota: por definir.",
        pdf_legal="Documento informativo. No constituye una oferta pública de valores ni promesa de rendimiento. Las participaciones son acciones de una serie de la SAPI de C.V. de La Tokenizadora y se ofrecen solo de forma privada, previa visita y admisión.",
        pdf_gen="Generando el PDF…", pdf_ok="Listo. Revisa tus descargas.", pdf_err="No se pudo generar el PDF. Revisa tu conexión e inténtalo de nuevo.",
        vi_correo="Correo",
        info={
            "calle": {"t": "Calle central", "d": "6 m de sascab compactado, doble sentido a vuelta de rueda. La curva baja la velocidad y el ruido. Sale a la calle del sur."},
            "corredor": {"t": "Camino verde", "d": "Corredor de 4 m entre clusters. Dos huellas de concreto para entrar en auto a los lotes de atrás, y frutales de porte bajo a los lados. Es el sendero de recolección."},
            "energia": {"t": "Centro de energía y agua", "d": "Paneles solares, baterías y el pozo con su tanque elevado. Puede alojar un estacionamiento compartido."},
            "agro": {"t": "Bosque agroforestal", "d": "Los rincones que no completan un cluster se siembran como huerto común: frutales, milpa y árboles nativos."},
            "cluster": {"t": "Cluster", "d": "Lotes de 200 m² que se compran juntos, de 2, 4 u 8. El lote del frente da a la calle y el de atrás al camino verde."},
            "serv": {"t": "Servidumbre de paso", "d": "Franja de 3 m dentro de los clusters de 8 para que cada lote de atrás tenga entrada, aunque el cluster lo compartan varias familias. No cambia la superficie de los lotes."},
        },
        err_nombre="Escribe tu nombre.", err_email="Escribe un correo válido, por ejemplo nombre@dominio.com."),
)

EN = dict(
    lang="en", alt_lang="es", alt_label="Español", alt_href="../",
    title="Bosque Venado, Acanceh, Yucatán",
    desc=f"A neo-rural community in the forest near Acanceh, Yucatán, with well water, solar power and its own food. {N_LOTES} lots of 200 m² in clusters of 2, 4 and 8, with lifetime use through a share series tokenized by La Tokenizadora.",
    draft='Design draft. Items marked <span class="tbd">like this</span> are still to be defined.',
    home_label="Bosque Venado, home", nav_label="Sections",
    nav_lugar="The land", nav_vida="Water, power and food", nav_etapa="Phase 3", nav_cotiza="Get a quote", nav_faq="FAQ",
    cta_visita="Book a visit", cta_clusters="See available clusters",
    menu="Menu", cerrar="Close", agenda="Book", wa_label="Message us on WhatsApp", nav_visita="Visit",
    hero_tag="Your own water, power and food, in the forest near Acanceh.",
    foto_pend="Photo pending", f_hero="A sascab road between palms and forest",
    f_ceiba="A pale-trunked ceiba with wide roots in the forest", f_ceiba_cap="The ceiba, the sacred Maya tree, in the Yucatán forest",
    predio_t="The whole parcel",
    predio_p="The parcel covers 7 hectares. Phases 1 and 2, on the east side, add up to 5 hectares and are already sold. Phase 3 takes the 2 western hectares, facing the south street.",
    part_etq="Your stake", en_etq="How to join", es_etq="Structure",
    h1="Your own water, power and food, in the forest.",
    hero_lede=f"Bosque Venado is a neo-rural community in Acanceh, Yucatán. Phase 3 has {N_LOTES} lots of 200 m² grouped in clusters of 2, 4 and 8, with fruit-tree lanes between them and a shared solar power and well water hub.",
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
    e3_lede=f"Two hectares on the west side of the parcel. A winding 6 m central street serves {N_CL} clusters on both sides: {POR_TAM[8]} of 8 lots, {POR_TAM[4]} of 4 and {POR_TAM[2]} of 2. Tap a cluster to get a quote, or an i icon to learn what each area is.",
    desliza="Swipe to see the whole plan.",
    st_disp="Available", st_apar="Reserved", st_vend="Sold",
    z_calle="Street and wheel tracks", z_agro="Food forest", z_energia="Power and water",
    co_h="Get a quote for your cluster.",
    co_lede="Each 200 m² lot costs MXN $100,000 over 60 months, or $500 per m². A cluster adds up its lots, and the shorter the term, the lower the total price. Download the quote as a PDF or send it to us on WhatsApp.",
    ficha_vacia="Choose a cluster on the plan, or get a quote by size.",
    co_tam="Cluster size", co_plazo="Term",
    pr_eng="Down payment", pr_total="Total price", pr_m2="Price per m²", pr_ahorro="Savings vs. 60 months",
    co_pdf="Download quote as PDF", co_pedir="Ask about this cluster",
    pr_th1="Term", pr_th2="Monthly", pr_th3="Total", pr_th4="Discount",
    pr_letra="MXN $10,000 down payment per lot on every term. If you pay off early, you pay the price of the term in which you finish. Phase 3 prices, valid until " + TBD.format("date to be defined") + ". The maintenance fee is separate: " + TBD.format("amount to be defined") + ". Prices in Mexican pesos, interest-free.",
    part_h="What your stake gives you, and what it doesn't.",
    part_lede="Your stake is a set of shares in a series of La Tokenizadora's SAPI de C.V., represented by a token. It gives you lifetime use of a cluster of 2, 4 or 8 lots and a say in how the land is cared for.",
    si_h="Included",
    si_items=li([
        ("Lifetime use of your cluster", "Of 2, 4 or 8 lots of 200 m², in phase 3"),
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
        ("Reserve your cluster", "You receive the bylaws, rules and contract to review at your own pace."),
        ("Sign and register", "You sign your contract and are entered in the share register."),
        ("Receive your token", "La Tokenizadora issues your token and your cluster is assigned."),
    ]),
    es_h="The land, the company and the token.",
    es_lede="Three pieces that back each other up, so your stake is clear today and stays clear if something fails.",
    capas=capas([
        ("The land", "The property belongs to a share series of La Tokenizadora's SAPI de C.V., created for Bosque Venado. No one can split it up or sell it in pieces."),
        ("Your stake", "It is a set of shares in that series. The share register is the controlling record, and your cluster is tied to it."),
        ("The token", "La Tokenizadora tokenizes each stake. Your token is your key, and if the network ever fails, the register and the rules also exist on paper."),
    ]),
    faq_h="Frequently asked questions.",
    faq=faq([
        ("Why clusters and not single lots?", "Each cluster has a row of lots at the front, on the street, and another at the back, next to the green lane. Bought together, no lot is left without access, and there is room for fruit trees between clusters."),
        ("How do I drive to the back lots?", "Along the green lane next to each cluster: it has two concrete wheel tracks for driving in at walking pace. Clusters of 8 also have a 3 m easement through the middle."),
        ("Can I buy a cluster with friends or family?", "Yes. A cluster of 4 or 8 can be shared; each person holds their own shares and the rules set access and use inside the cluster."),
        ("Can I build?", "Yes, under the building rules, which set type, materials and size: " + TBD.format("to be defined") + "."),
        ("Do I get a deed?", "No. The land belongs to the company. Your right of use is tied to your shares in the share register and to your contract."),
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
    f_cluster="Cluster you are interested in", f_cluster_ph="Optional, for example 7",
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
        cluster="Cluster", lotes="lots", de="of", tam="Size", sup="Area", frente="Street frontage", fondo="Depth", ubic="Location", estado="Status",
        banda={"poniente": "West side of the street", "oriente": "East side of the street"},
        st={"disponible": "Available", "apartado": "Reserved", "vendido": "Sold"},
        cuenta="{d} of {t} clusters available ({l} lots).", quitar="Quote another size", ficha_vacia="Choose a cluster on the plan, or get a quote by size.",
        t_cap="Every term for a cluster of {n} lots ({m})", total_c="total",
        wa_txt="Hi, I am interested in Bosque Venado.",
        co_plazo="Term", pr_eng="Down payment", pr_total="Total price", pr_m2="Price per m²", pr_ahorro="Savings vs. 60 months",
        pr_th1="Term", pr_th2="Monthly", pr_th3="Total", pr_th4="Discount", mens_pdf="Monthly payment ({n} payments)",
        pdf_sub="Phase 3 quote. Parcel 3735, Seyé, Yucatán, Mexico.", pdf_folio="Ref.", pdf_sin="Cluster of {n} lots, to be assigned",
        pdf_mapa="Phase 3", pdf_calle="South street", pdf_contacto="Contact", pdf_archivo="Bosque-Venado-quote",
        pdf_notas="MXN $10,000 down payment per lot. If you pay off early, you pay the price of the term in which you finish. Prices in Mexican pesos, interest-free. The maintenance fee is separate. A cluster is reserved only with a signed reservation; this quote does not reserve it. Validity and fee: to be defined.",
        pdf_legal="For information only. Not a public offering of securities or a promise of returns. Stakes are shares in a series of La Tokenizadora's SAPI de C.V. and are offered privately only, after a visit and admission.",
        pdf_gen="Generating the PDF…", pdf_ok="Done. Check your downloads.", pdf_err="The PDF could not be generated. Check your connection and try again.",
        vi_correo="Email",
        info={
            "calle": {"t": "Central street", "d": "6 m of compacted sascab, two-way at walking pace. The curve slows cars and keeps noise down. It connects to the south street."},
            "corredor": {"t": "Green lane", "d": "A 4 m lane between clusters. Two concrete wheel tracks for driving to the back lots, with low fruit trees on both sides. It is the harvest path."},
            "energia": {"t": "Power and water hub", "d": "Solar panels, batteries and the well with its elevated tank. It can also hold shared parking."},
            "agro": {"t": "Food forest", "d": "Corners too small for a cluster are planted as a shared garden: fruit trees, milpa and native trees."},
            "cluster": {"t": "Cluster", "d": "Lots of 200 m² bought together, in groups of 2, 4 or 8. The front lot faces the street and the back lot faces the green lane."},
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
    data["ESTADO"] = json.dumps(estado.get("clusters", {}))
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
