"""Genera index.html (es), en/index.html (en) y las páginas de gracias.

Uso: python3 src/build.py   (desde la raíz del repositorio)
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import plan  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TBD = '<span class="tbd">{}</span>'
S = plan.summary()
N_LOTES = S["lotes"]
HA = f'{S["area"] / 10000:.0f}'
HA_ETAPA = f'{S["etapa_area"] / 10000:.2f}'
LAY = {
    "rect": dict(es_med="11.1 × 18 m", en_med="11.1 × 18 m", es_vias="con dos vías internas", en_vias="with two internal roads",
                 es_com="áreas comunes y vías", en_com="common areas and roads"),
    "parque": dict(es_med="Frente de 9 a 14 m", en_med="9 to 14 m frontage",
                   es_vias="sobre una calle ondulada al poniente y una calle recta en el lindero con la etapa 2, unidas por una glorieta alrededor de un parque central",
                   en_vias="along a winding street on the west and a straight street on the boundary with phase 2, joined by a loop around a central park",
                   es_com="calles, el parque central y un corredor de monte entre los fondos", en_com="streets, the central park and a strip of forest between back yards",
                   es_extra=" La curva baja la velocidad de los autos y el ruido.", en_extra=" The curve slows cars down and keeps noise low."),
    "onda": dict(es_med="Frente y fondo variables", en_med="Varies with the curve", es_vias="a lo largo de dos calles onduladas de 6 m que forman un circuito",
                 en_vias="along two winding 6 m streets that form a loop", es_com="calles, áreas comunes y jardines", en_com="streets, common areas and gardens",
                 es_extra=" Las curvas bajan la velocidad de los autos y el ruido.", en_extra=" The curves slow cars down and keep noise low."),
    "hex": dict(es_med="8.8 m por lado", en_med="8.8 m per side", es_vias="hexagonales, rodeados por senderos de 3 m", en_vias="hexagonal, surrounded by 3 m footpaths",
                es_com="áreas comunes y senderos", en_com="common areas and footpaths"),
}[plan.LAYOUT]
COMUN = f'{S["comun_pct"] * 100:.0f}%'


def li(items):
    return "".join(f"<li>{a}<small>{b}</small></li>" for a, b in items)


def pasos(items):
    return "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in items)


def capas(items):
    return "".join(f"<div><h3>{a}</h3><p>{b}</p></div>" for a, b in items)


def faq(items):
    return "".join(f"<details><summary>{a}</summary><p>{b}</p></details>" for a, b in items)


ES = dict(
    lang="es-MX", alt_lang="en", alt_label="English", alt_href="en/",
    title="Bosque Venado, Acanceh, Yucatán",
    desc=f"{HA} hectáreas de monte junto a Acanceh, Yucatán, cuidadas por una comunidad. Uso vitalicio de lotes de 200 m², a través de una serie accionaria tokenizada por La Tokenizadora.",
    draft='Borrador de diseño. Los datos marcados <span class="tbd">así</span> están por definir.',
    home_label="Bosque Venado, inicio", nav_label="Secciones",
    nav_lugar="El lugar", nav_etapas="Etapas y lotes", nav_part="Tu participación", nav_precios="Precios", nav_faq="Preguntas",
    cta_visita="Agenda una visita", cta_lotes="Ver lotes",
    h1="Siete hectáreas de monte, cuidadas por una comunidad.",
    hero_lede="Bosque Venado es tierra de conservación junto a Acanceh, Yucatán, y un experimento de vida neorural fuera de la red. Cada participación te da el uso vitalicio de un lote de 200 m² y voz en cómo se cuida el lugar.",
    plan_title="Plano del predio en tres etapas",
    plan_desc=f"Predio de {HA} hectáreas dividido en tres etapas. La etapa 3, al poniente, tiene {N_LOTES} lotes de 200 metros cuadrados {LAY['es_vias']}.",
    plan_cap="Plano basado en el levantamiento topográfico del tablaje 3735. La distribución de lotes es esquemática.",
    etapa="Etapa", vendida="vendida", calle="Calle sin nombre", lote="Lote",
    e3_map_label=f"Etapa 3: {N_LOTES} lotes. Elige uno para ver su información.",
    d1_t="Superficie", d1=f"{HA} hectáreas",
    d2_t="Ubicación", d2="Junto a Acanceh, Yucatán",
    d3_t="Etapa 3", d3=f"{N_LOTES} lotes de 200 m²",
    d4_t="Áreas comunes y vías", d4=f"{COMUN} de la etapa",
    lugar_h="Primero el monte, después todo lo demás.",
    lugar_lede="Ya hay vida en el predio: agua de pozo, energía solar y tres construcciones. Lo común se construye entre todos, con poco impacto y fuera de la red.",
    hoy_h="Lo que hay hoy",
    hoy_items=li([
        ("Agua de pozo", "A 27 metros de profundidad"),
        ("Energía solar", "Paneles y baterías en una de las casas habitadas"),
        ("Tres construcciones", "Ubicación en el plano: " + TBD.format("por confirmar")),
        ("Acceso por dos calles", "Al sur y al oriente del predio"),
        ("Cerca de Acanceh", "A unos 1.2 km por la calle 19, según el croquis del plano"),
    ]),
    juntos_h="Lo que construimos juntos",
    juntos_items=li([
        ("Vías internas de la etapa 3", "Fecha estimada: " + TBD.format("por definir")),
        ("Sistema solar común", "Fecha estimada: " + TBD.format("por definir")),
        ("Almacenamiento y distribución de agua", "Fecha estimada: " + TBD.format("por definir")),
        ("Huerto y vivero", "Fecha estimada: " + TBD.format("por definir")),
        ("Palapa y bodega común", "Fecha estimada: " + TBD.format("por definir")),
    ]),
    et_h="Tres etapas, de oriente a poniente.",
    et_lede=f"Cada etapa ocupa un tercio del predio, unas {HA_ETAPA} hectáreas. Las etapas 1 y 2, al oriente y al centro, ya están vendidas; la etapa 3, al poniente, es la que está a la venta.",
    e3_n="Etapa 3", e3_tag="Disponible",
    e3_p=f"Al poniente, con frente a la calle del sur. {N_LOTES} lotes de 200 m² {LAY['es_vias']}; el {COMUN} de la etapa queda para {LAY['es_com']}.{LAY.get('es_extra', '')}",
    e2_n="Etapa 2", e12_tag="Vendida",
    e2_p="Al centro del predio. Ya está vendida.",
    e1_n="Etapa 1",
    e1_p="Al oriente, junto a la calle. Ya está vendida.",
    ficha_vacia="Elige un lote en el plano para ver su información.",
    st_disp="Disponible", st_apar="Apartado", st_vend="Vendido",
    part_h="Qué te da tu participación, y qué no.",
    part_lede="Tu participación son acciones de una serie de la SAPI de C.V. de La Tokenizadora, representadas por un token. Con ellas recibes el uso vitalicio de un lote de 200 m² y voz en cómo se cuida la tierra.",
    si_h="Incluye",
    si_items=li([
        ("Uso vitalicio de un lote de 200 m²", "Asignado a tu participación, en la etapa 3"),
        ("Acceso a las áreas comunes", "Vías, agua, energía, huerto y bodega, con cuota de mantenimiento"),
        ("Construir en tu lote", "Tipo, materiales y tamaño según el reglamento: " + TBD.format("por definir")),
        ("Voto en las decisiones sobre la tierra", "Reglas, mejoras y admisión de nuevos miembros"),
        ("Herencia y reventa", "Tu derecho pasa a tus herederos o a quien compre, con admisión por la comunidad"),
    ]),
    no_h="No incluye",
    no_items=li([
        ("Escritura individual del lote", "La tierra es de la sociedad; tu derecho queda en el registro de acciones"),
        ("Desmonte por tu cuenta", "Cualquier claro se decide en común y con permiso"),
        ("Renta o uso comercial del lote", "Regla: " + TBD.format("por definir")),
        ("Promesa de rendimiento o plusvalía", "El valor está en el uso y la comunidad"),
    ]),
    part_nota="Los derechos se fijan en los estatutos, el reglamento de uso y tu contrato. Versión final de los documentos: " + TBD.format("por definir") + ".",
    pr_h="Un lote, seis formas de pagarlo.",
    pr_lede="Cada lote de 200 m² cuesta $100,000 a 60 meses, o $500 por m². Mientras más corto el plazo, menor el precio total.",
    pr_elige="Elige un plazo", pr_eng="Enganche", pr_total="Precio total", pr_m2="Precio por m²", pr_ahorro="Ahorro contra 60 meses",
    pr_tabla="Todos los planes", pr_th1="Plazo", pr_th2="Mensualidad", pr_th3="Total", pr_th4="Descuento",
    pr_letra="Enganche de $10,000 en todos los plazos. Si liquidas antes, pagas el precio del plazo en que terminas. Precios de la etapa 3, vigentes hasta " + TBD.format("fecha por definir") + ". La cuota de mantenimiento se paga aparte: " + TBD.format("monto por definir") + ". Precios en pesos mexicanos, sin intereses.",
    en_h="Cómo entrar a la comunidad.",
    en_lede="Antes de pagar, nos conocemos. Una comunidad fuerte empieza por elegir bien a quién se suma.",
    pasos=pasos([
        ("Visita el predio", "Recorre el monte, las construcciones y los lotes disponibles."),
        ("Conversa con la comunidad", "Hablamos de valores, expectativas y cómo quieres usar el lugar."),
        ("Aparta y revisa", "Recibes estatutos, reglamento y contrato para revisarlos con calma."),
        ("Firma y registro", "Firmas tu contrato y quedas inscrito en el registro de accionistas."),
        ("Recibe tu token", "La Tokenizadora emite tu token y se asigna tu lote."),
    ]),
    es_h="La tierra, la sociedad y el token.",
    es_lede="Tres piezas que se respaldan entre sí, para que tu participación sea clara hoy y siga clara si algo falla.",
    capas=capas([
        ("La tierra", "El predio pertenece a una serie accionaria de la SAPI de C.V. de La Tokenizadora, creada para Bosque Venado. Nadie lo puede dividir ni vender por partes."),
        ("Tu participación", "Son acciones de esa serie. El registro de accionistas es el documento que manda, y ahí se liga tu lote."),
        ("El token", "La Tokenizadora tokeniza cada participación. Tu token es tu llave, y si un día falla la red, el padrón y el reglamento existen también en papel."),
    ]),
    faq_h="Preguntas frecuentes.",
    faq=faq([
        ("¿Puedo construir en mi lote?", "Sí, según el reglamento de construcción, que fija tipo, materiales y tamaño: " + TBD.format("por definir") + "."),
        ("¿Recibo escritura del lote?", "No. La tierra es de la sociedad. Tu derecho de uso se liga a tus acciones en el registro de accionistas y a tu contrato."),
        ("¿Puedo vender o heredar mi participación?", "Sí. El derecho de uso se transmite con tus acciones, por herencia o por venta. Quien la reciba pasa por el mismo proceso de admisión que tú."),
        ("¿Hay agua y luz?", "Hay un pozo con agua a 27 metros. No hay red eléctrica: una de las casas habitadas funciona con paneles solares y baterías, y el plan común suma energía solar para la comunidad."),
        ("¿Qué pasa con las etapas 1 y 2?", "Ya están vendidas. La etapa 3 es la única que está a la venta."),
        ("¿Cuánto es la cuota de mantenimiento?", "Cubre vías, agua, energía y cuidado del monte. Monto: " + TBD.format("por definir") + "."),
        ("¿Qué pasa si dejo de pagar?", "Lo que pasa con tus pagos y tu participación se fija en el contrato: " + TBD.format("regla por definir") + "."),
    ]),
    vi_h="Agenda una visita.",
    vi_lede="Cuéntanos quién eres y qué buscas. Te escribimos para coordinar el día y la hora.",
    vi_wa="También por WhatsApp:",
    form_action="/gracias",
    f_honey="No llenes este campo", f_nombre="Nombre", f_email="Correo",
    f_lote="Lote que te interesa", f_lote_ph="Opcional, por ejemplo 23",
    f_plazo="Plazo que te interesa",
    f_plazo_opts='<option value="">Aún no sé</option><option>60 meses</option><option>48 meses</option><option>36 meses</option><option>24 meses</option><option>12 meses</option><option>Contado</option>',
    f_uso="¿Cómo te imaginas usar el lugar?",
    f_uso_ayuda="Fines de semana, temporadas, vivir ahí, un huerto…",
    f_enviar="Enviar solicitud de visita",
    pie_1="<strong>Bosque Venado</strong><br>Tablaje 3735, Seyé, Yucatán.<br>Tokenizado por La Tokenizadora.",
    pie_2="Esta página es informativa y no constituye una oferta pública de valores ni promesa de rendimiento. Las participaciones se ofrecen solo de forma privada, previa visita y admisión. Autorizaciones y documentos legales: " + TBD.format("por definir") + ". <a href=\"#\">Aviso de privacidad</a> (" + TBD.format("por definir") + ").",
    JS=dict(meses="{n} meses", contado="Contado", na="N/A", mens_etq="Mensualidad, {n} pagos", unico="Pago único",
            al_mes="al mes", incluido="Incluido", lote="Lote", sup="Superficie", medidas="Medidas", med=LAY["es_med"], estado="Estado", desde="Desde",
            st={"disponible": "Disponible", "apartado": "Apartado", "vendido": "Vendido"},
            cuenta="{d} de {t} lotes disponibles en la etapa 3.", pedir="Pedir este lote",
            err_nombre="Escribe tu nombre.", err_email="Escribe un correo válido, por ejemplo nombre@dominio.com."),
)

EN = dict(
    lang="en", alt_lang="es", alt_label="Español", alt_href="../",
    title="Bosque Venado, Acanceh, Yucatán",
    desc=f"{HA} hectares of native forest next to Acanceh, Yucatán, cared for by a community. Lifetime use of 200 m² lots, through a share series tokenized by La Tokenizadora.",
    draft='Design draft. Items marked <span class="tbd">like this</span> are still to be defined.',
    home_label="Bosque Venado, home", nav_label="Sections",
    nav_lugar="The land", nav_etapas="Phases and lots", nav_part="Your stake", nav_precios="Pricing", nav_faq="FAQ",
    cta_visita="Book a visit", cta_lotes="See the lots",
    h1="Seven hectares of native forest, cared for by a community.",
    hero_lede="Bosque Venado is conservation land next to Acanceh, Yucatán, and an off-grid experiment in rural living. Each stake gives you lifetime use of a 200 m² lot and a say in how the land is cared for.",
    plan_title="Site plan in three phases",
    plan_desc=f"A {HA}-hectare property divided into three phases. Phase 3, on the west side, has {N_LOTES} lots of 200 square meters, {LAY['en_vias']}.",
    plan_cap="Based on the topographic survey of parcel 3735. The lot layout is schematic.",
    etapa="Phase", vendida="sold", calle="Unnamed street", lote="Lot",
    e3_map_label=f"Phase 3: {N_LOTES} lots. Choose one to see its details.",
    d1_t="Area", d1=f"{HA} hectares",
    d2_t="Location", d2="Next to Acanceh, Yucatán",
    d3_t="Phase 3", d3=f"{N_LOTES} lots of 200 m²",
    d4_t="Common areas and roads", d4=f"{COMUN} of the phase",
    lugar_h="The forest first, everything else after.",
    lugar_lede="There is already life on the land: well water, solar power and three buildings. Shared infrastructure is built together, with a light footprint and off the grid.",
    hoy_h="What is there today",
    hoy_items=li([
        ("Well water", "Reached at 27 meters"),
        ("Solar power", "Panels and batteries in one of the lived-in houses"),
        ("Three buildings", "Location on the plan: " + TBD.format("to be confirmed")),
        ("Access from two streets", "On the south and east sides of the property"),
        ("Close to Acanceh", "About 1.2 km along Calle 19, per the survey sketch"),
    ]),
    juntos_h="What we build together",
    juntos_items=li([
        ("Internal roads in phase 3", "Estimated date: " + TBD.format("to be defined")),
        ("Shared solar system", "Estimated date: " + TBD.format("to be defined")),
        ("Water storage and distribution", "Estimated date: " + TBD.format("to be defined")),
        ("Garden and nursery", "Estimated date: " + TBD.format("to be defined")),
        ("Shared palapa and storage", "Estimated date: " + TBD.format("to be defined")),
    ]),
    et_h="Three phases, from east to west.",
    et_lede=f"Each phase covers a third of the property, about {HA_ETAPA} hectares. Phases 1 and 2, on the east side and in the middle, are already sold; phase 3, on the west side, is the one for sale.",
    e3_n="Phase 3", e3_tag="Available",
    e3_p=f"On the west side, facing the south street. {N_LOTES} lots of 200 m², {LAY['en_vias']}; {COMUN} of the phase is set aside for {LAY['en_com']}.{LAY.get('en_extra', '')}",
    e2_n="Phase 2", e12_tag="Sold",
    e2_p="In the middle of the property. Already sold.",
    e1_n="Phase 1",
    e1_p="On the east side, along the street. Already sold.",
    ficha_vacia="Choose a lot on the plan to see its details.",
    st_disp="Available", st_apar="Reserved", st_vend="Sold",
    part_h="What your stake gives you, and what it doesn't.",
    part_lede="Your stake is a set of shares in a series of La Tokenizadora's SAPI de C.V., represented by a token. It gives you lifetime use of a 200 m² lot and a say in how the land is cared for.",
    si_h="Included",
    si_items=li([
        ("Lifetime use of a 200 m² lot", "Assigned to your stake, in phase 3"),
        ("Access to common areas", "Roads, water, power, garden and storage, with a maintenance fee"),
        ("Building on your lot", "Type, materials and size set by the rules: " + TBD.format("to be defined")),
        ("A vote on decisions about the land", "Rules, improvements and admission of new members"),
        ("Inheritance and resale", "Your right passes to your heirs or to a buyer, with admission by the community"),
    ]),
    no_h="Not included",
    no_items=li([
        ("An individual deed to the lot", "The land belongs to the company; your right is recorded in the share register"),
        ("Clearing land on your own", "Any clearing is decided together and with permits"),
        ("Renting or commercial use of the lot", "Rule: " + TBD.format("to be defined")),
        ("A promise of returns or appreciation", "The value is in the use and the community"),
    ]),
    part_nota="Your rights are set by the bylaws, the use rules and your contract. Final documents: " + TBD.format("to be defined") + ".",
    pr_h="One lot, six ways to pay.",
    pr_lede="Each 200 m² lot costs MXN $100,000 over 60 months, or $500 per m². The shorter the term, the lower the total price.",
    pr_elige="Choose a term", pr_eng="Down payment", pr_total="Total price", pr_m2="Price per m²", pr_ahorro="Savings vs. 60 months",
    pr_tabla="All plans", pr_th1="Term", pr_th2="Monthly", pr_th3="Total", pr_th4="Discount",
    pr_letra="MXN $10,000 down payment on every term. If you pay off early, you pay the price of the term in which you finish. Phase 3 prices, valid until " + TBD.format("date to be defined") + ". The maintenance fee is separate: " + TBD.format("amount to be defined") + ". Prices in Mexican pesos, interest-free.",
    en_h="How to join the community.",
    en_lede="Before any payment, we get to know each other. A strong community starts with choosing well who joins.",
    pasos=pasos([
        ("Visit the land", "Walk the forest, the buildings and the available lots."),
        ("Talk with the community", "We discuss values, expectations and how you want to use the place."),
        ("Reserve and review", "You receive the bylaws, rules and contract to review at your own pace."),
        ("Sign and register", "You sign your contract and are entered in the share register."),
        ("Receive your token", "La Tokenizadora issues your token and your lot is assigned."),
    ]),
    es_h="The land, the company and the token.",
    es_lede="Three pieces that back each other up, so your stake is clear today and stays clear if something fails.",
    capas=capas([
        ("The land", "The property belongs to a share series of La Tokenizadora's SAPI de C.V., created for Bosque Venado. No one can split it up or sell it in pieces."),
        ("Your stake", "It is a set of shares in that series. The share register is the controlling record, and your lot is tied to it."),
        ("The token", "La Tokenizadora tokenizes each stake. Your token is your key, and if the network ever fails, the register and the rules also exist on paper."),
    ]),
    faq_h="Frequently asked questions.",
    faq=faq([
        ("Can I build on my lot?", "Yes, under the building rules, which set type, materials and size: " + TBD.format("to be defined") + "."),
        ("Do I get a deed to the lot?", "No. The land belongs to the company. Your right of use is tied to your shares in the share register and to your contract."),
        ("Can I sell or pass on my stake?", "Yes. The right of use transfers with your shares, by inheritance or sale. The new holder goes through the same admission process you did."),
        ("Is there water and power?", "There is a well with water at 27 meters. There is no grid connection: one of the lived-in houses runs on solar panels and batteries, and the shared plan adds solar power for the community."),
        ("What about phases 1 and 2?", "They are already sold. Phase 3 is the only one for sale."),
        ("How much is the maintenance fee?", "It covers roads, water, power and forest care. Amount: " + TBD.format("to be defined") + "."),
        ("What happens if I stop paying?", "What happens to your payments and your stake is set in the contract: " + TBD.format("rule to be defined") + "."),
    ]),
    vi_h="Book a visit.",
    vi_lede="Tell us who you are and what you are looking for. We will write to set a day and time.",
    vi_wa="Or on WhatsApp:",
    form_action="/en/gracias",
    f_honey="Leave this field empty", f_nombre="Name", f_email="Email",
    f_lote="Lot you are interested in", f_lote_ph="Optional, for example 23",
    f_plazo="Term you are interested in",
    f_plazo_opts='<option value="">Not sure yet</option><option>60 months</option><option>48 months</option><option>36 months</option><option>24 months</option><option>12 months</option><option>Cash</option>',
    f_uso="How do you picture using the place?",
    f_uso_ayuda="Weekends, seasons, living there, a garden…",
    f_enviar="Send visit request",
    pie_1="<strong>Bosque Venado</strong><br>Parcel 3735, Seyé, Yucatán, Mexico.<br>Tokenized by La Tokenizadora.",
    pie_2="This page is for information only and is not a public offering of securities or a promise of returns. Stakes are offered privately only, after a visit and admission. Permits and legal documents: " + TBD.format("to be defined") + ". <a href=\"#\">Privacy notice</a> (" + TBD.format("to be defined") + ").",
    JS=dict(meses="{n} months", contado="Cash", na="N/A", mens_etq="Monthly payment, {n} payments", unico="Single payment",
            al_mes="per month", incluido="Included", lote="Lot", sup="Area", medidas="Size", med=LAY["en_med"], estado="Status", desde="From",
            st={"disponible": "Available", "apartado": "Reserved", "vendido": "Sold"},
            cuenta="{d} of {t} lots available in phase 3.", pedir="Ask about this lot",
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


def render(t):
    tpl = (ROOT / "src" / "template.html").read_text()
    data = dict(t)
    data["PLAN_OVERVIEW"] = plan.overview_svg(t)
    data["PLAN_DETAIL"] = plan.detail_svg(t)
    data["JS"] = json.dumps(t["JS"], ensure_ascii=False)
    data["LOTES"] = json.dumps({l["n"]: {} for l in plan.LOTS})
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(data[m.group(1)]), tpl)
    left = re.findall(r"\{\{\w+\}\}", out)
    assert not left, left
    return out


def main():
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "index.html").write_text(render(ES))
    (ROOT / "en" / "index.html").write_text(render(EN))
    for key, path in (("es", ROOT / "gracias.html"), ("en", ROOT / "en" / "gracias.html")):
        lang, title, h1, p, href, back = GRACIAS[key]
        path.write_text(GR_TPL.format(lang=lang, title=title, h1=h1, p=p, href=href, back=back))
    print(json.dumps(S, indent=1))


if __name__ == "__main__":
    main()
