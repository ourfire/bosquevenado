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
RAZON = "Tokenizadora, S.A. de C.V."  # razón social del responsable de los datos; ajustar si hay homonimia
CUOTA = "$1,000"
DOMICILIO = "Calle 14 esquina #78, oficina 303, colonia México, Mérida, Yucatán"  # cuota anual de mantenimiento por lote
WA = "999 991 0450"

TITULOS = {
    "es": {"detalle": "Plano de la etapa 3. Elige un cluster para cotizarlo.",
           "general": "Plano del predio",
           "general_desc": "Tablaje de 7 hectáreas. Las etapas 1 y 2, al oriente, están vendidas. La etapa 3, al poniente, tiene 3 hectáreas con clusters de lotes a los lados de dos calles onduladas."},
    "en": {"detalle": "Phase 3 plan. Choose a cluster to get a quote.",
           "general": "Site plan",
           "general_desc": "A 7-hectare parcel. Phases 1 and 2, on the east side, are sold. Phase 3, on the west side, covers 3 hectares with clusters of lots along two winding streets."},
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
        '<rect x="3" y="3" width="94" height="94"/><path d="M30,46 L30,22"/><path d="M70,46 L70,22"/><path d="M22,46 L22,30"/><path d="M78,46 L78,30"/><path d="M38,46 L38,14"/><path d="M62,46 L62,14"/><path d="M22,46 L38,46"/><path d="M78,46 L62,46"/><path d="M40,50 L28,54 L40,58"/><path d="M60,50 L72,54 L60,58"/><path d="M40,46 L60,46 L50,82 Z"/><circle cx="45.6" cy="55" r="1.7" fill="currentColor" stroke="none"/><circle cx="54.4" cy="55" r="1.7" fill="currentColor" stroke="none"/></svg>')


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
        out.append(f'<div><div class="foto" role="img" aria-label="{re.sub("<[^>]+>", "", nombre)}"><span class="pend">{pend}</span></div><h3>{nombre}</h3><p>{rol}</p></div>')
    return "".join(out)


def referentes(items):
    return "".join(f'<article><h3>{a}</h3><p class="lugar">{b}</p><p>{c}</p><p><a href="{u}" target="_blank" rel="noopener">{v}</a></p></article>' for a, b, c, u, v in items)


def voces(items, etq):
    return "".join(f'<figure><blockquote><p>{t}</p></blockquote><figcaption><strong>{n}</strong><span>{q}</span><span class="ej">{etq}</span></figcaption></figure>' for t, n, q in items)


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
    com_lede="Creemos que la fuerza de una comunidad está en sus lazos: entre sus miembros, y entre la comunidad y Acanceh y su gente. Por eso queremos agua limpia, energía propia y comida suficiente para compartir e intercambiar. Estamos en preventa: cada participación financia lo común.",
    com_items=cuatro([
        ("Agua, energía y comida", "Pozo, sol y siembra resueltos en común, con excedentes para intercambiar."),
        ("Lazos con Acanceh", "Queremos crecer junto con el pueblo: trabajo local, intercambio y, más adelante, monedas solidarias con nuestros vecinos."),
        ("Confianza entre pares", "Todos nos conocemos. La comunidad aprueba quién entra y quién sale; nadie participa de forma anónima."),
        ("Rigor legal", "Todo está tokenizado y respaldado con acciones de una serie de una SAPI de C.V., con estatutos y reglamento."),
    ]),
    reg_etq="Convivencia", reg_h="Reglamento de convivencia, en esquema.",
    reg_lede="Lo básico para vivir juntos. Empezamos simple; a medida que la comunidad crezca, ella misma escribe y vota la versión final.",
    reglas=reglas([
        ("Admisión y salida", ["Visita y conversación antes de entrar", "La comunidad aprueba a cada nuevo miembro", "Quien hereda o compra pasa por la misma admisión"]),
        ("Decisiones", ["Asamblea periódica de miembros", "Se vota lo que concierne a todos", "Cuando seamos más, la comunidad diseña su propio modelo"]),
        ("Monte y siembra", ["Ningún desmonte sin acuerdo común", "Especies nativas y frutales", "Los caminos verdes son de todos"]),
        ("Construcción", ["Materiales y alturas según el reglamento", "Se respeta la servidumbre de paso"]),
        ("Agua y energía", ["Uso responsable del pozo y el tanque", "Cada casa puede sumar su propio sistema", "Lo común se mantiene con una cuota"]),
        ("Vida diaria", ["Silencio por la noche", "Mascotas bajo el cuidado de su dueño", "Visitas con aviso a la comunidad"]),
        ("Trabajo común", ["Jornadas en el huerto y los caminos", "Las cosechas comunes se reparten y los excedentes se intercambian", "Cada quien aporta su oficio"]),
        ("Cuotas y conflictos", ["Cuota de " + CUOTA + " al año por lote, desde que inician obras en su cluster", "Lo que sobra va a la reserva común de la sociedad", "Primero se conversa, luego hay mediación", "Si alguien deja de pagar, su participación se subasta entre los vecinos"]),
    ]),
    qs_etq="Quiénes somos", qs_h="Quienes empujan Bosque Venado.",
    qs_lede="Los fundadores y primeros miembros de la comunidad. Cada quien aporta su oficio a lo común.",
    gente=gente([
        ("Juan Carlos Soto", "Fundador. Artista y emprendedor."),
        ("María Cecilia Botero", "Fundadora. Artista y emprendedora."),
        ("Alejandro Vélez", "Fundador. Artista y emprendedor."),
    ], "Foto pendiente"),
    in_etq="Referentes", in_h="Comunidades que nos inspiran.",
    in_lede="Proyectos reales en México que llevan años viviendo así. Los citamos como inspiración; no son testimonios de Bosque Venado.",
    referentes=referentes([
        ("Huehuecoyotl", "Sierra del Tepozteco, Morelos. Desde 1982.",
         "Ecoaldea donde cada familia construyó su casa y entre todos hicieron el camino, la captación de lluvia, un teatro y las tierras de cultivo. La tierra se maneja en común, por acuerdo entre sus miembros.",
         "https://ecovillage.org/resources-library/article/what-is-our-ecovillage/", "Leer su historia"),
        ("Las Cañadas", "Cerca de Huatusco, Veracruz.",
         "Cooperativa agroecológica y centro de permacultura que cuida una de las últimas islas de bosque de niebla del centro de Veracruz, con bosque comestible y formación en agroecología.",
         "https://source.ecoversities.org/Ecoversity:Cooperativa_Agroecologica_Las_Ca%C3%B1adas", "Conocer la cooperativa"),
    ]),
    vo_etq="Voces", vo_h="Lo que dicen quienes ya están.",
    vo_lede="Testimonios de ejemplo, mientras recopilamos los de quienes viven en las etapas 1 y 2.",
    voces=voces([
        ("Llegamos por el silencio y nos quedamos por la gente. Las jornadas de los sábados en el huerto ya son lo mejor de la semana.", "Mariana", "Etapa 1"),
        ("Compramos un cluster de 4 con mis hermanos. Los niños conocen el monte y nosotros aprendimos a cuidar el agua.", "Tomás", "Cluster de 4 lotes"),
        ("Me convenció la claridad: sé qué tengo, qué no y cómo se decide. Y el pozo y los paneles ya funcionan.", "Daniela", "Primer lote"),
    ], "Ejemplo"),
    cta_visita="Agenda una visita", cta_clusters="Ver clusters disponibles",
    menu="Menú", cerrar="Cerrar", agenda="Agenda", wa_label="Escríbenos por WhatsApp", nav_visita="Visita",
    hero_tag="Agua, energía y comida propias, en el monte de Acanceh.",
    foto_pend="Foto pendiente", f_hero="Camino de sascab entre palmeras y monte",
    f_ceiba="Una ceiba de tronco claro y raíces anchas en medio del monte", f_ceiba_cap="La ceiba, el árbol sagrado maya, en el monte de Yucatán",
    predio_t="El predio completo",
    predio_p="El tablaje mide 7 hectáreas. Al oriente están las etapas 1 y 2, de 2 hectáreas cada una: la etapa 1 es La Villa Vikinga, donde están las tres construcciones, y la etapa 2 es un proyecto privado de Alejandro Vélez, residencia y centro de experimentación tecnológica y rural. La etapa 3 ocupa las 3 hectáreas del poniente, con frente a la calle del sur, y es la que está a la venta.",
    part_etq="Tu participación", en_etq="Cómo entrar", es_etq="Estructura",
    h1="Agua, energía y comida propias, en el monte.",
    hero_lede=f"Bosque Venado es una comunidad neorural en Acanceh, Yucatán. En la etapa 3 hay {N_LOTES} lotes de 200 m². Puedes comprar desde uno, o un cluster de 2, 4 u 8 con amigos o familia, con caminos de frutales entre ellos y un centro común de energía solar y agua de pozo.",
    plan_cap="Basado en el levantamiento topográfico del tablaje 3735. La distribución es esquemática y puede ajustarse en el proyecto definitivo.",
    d1_t="Predio", d1="7 hectáreas",
    d2_t="Etapa 3, a la venta", d2="3 hectáreas",
    d3_t="Lotes de 200 m²", d3=f"{N_LOTES} en {N_CL} clusters",
    d4_t="Áreas comunes", d4=f"{COMUN} de la etapa",
    lugar_h="Primero el monte, después todo lo demás.",
    lugar_lede="Ya hay vida en el predio: agua de pozo, energía solar y tres construcciones. Lo común se construye entre todos, con poco impacto y fuera de la red.",
    hoy_h="Lo que hay hoy",
    hoy_items=li([
        ("Agua de pozo", "A 27 metros de profundidad"),
        ("Energía solar", "Paneles y baterías en una de las casas habitadas"),
        ("Tres construcciones", "En La Villa Vikinga, la etapa 1"),
        ("Frente a la calle del sur", "Acceso directo a la etapa 3"),
        ("Cerca de Acanceh", "A unos 1.2 km por la calle 19, según el croquis del plano"),
    ]),
    juntos_h="Lo que construimos juntos",
    juntos_items=li([
        ("Dos calles de sascab", "Reparten a todos los clusters desde la calle del sur"),
        ("Centro de energía y agua", "Paneles, baterías, pozo y tanque elevado"),
        ("Caminos verdes con frutales", "Entre cada cluster"),
        ("Bosque agroforestal y vivero", "En los rincones libres de la etapa"),
        ("Aguada y chapoteaderos", "Guardan la lluvia y refrescan los clusters"),
        ("Palapa y bodega común", "Para reunirnos y guardar la herramienta"),
    ]),
    vida_h="Lo común es lo que te sostiene.",
    vida_lede="Las amenidades de Bosque Venado son el agua, la energía y la comida que la comunidad produce y cuida en conjunto.",
    pilares=pilares([
        ("Agua", "El pozo ya da agua a 27 metros. Se bombea con energía solar a un tanque elevado y baja por gravedad a los clusters.",
         ["Pozo existente", "Tanque elevado común", "Aguada de lluvia y chapoteaderos"], "el pozo y el tanque"),
        ("Energía", "Un centro de paneles y baterías para lo común, y cada casa puede sumar su propio sistema. Sin depender de la red.",
         ["Paneles solares y baterías", "Bombeo de agua solar", "Iluminación de caminos"], "los paneles de la casa habitada"),
        ("Comida", "Entre cluster y cluster corre un camino verde con frutales, y los rincones libres se siembran como bosque agroforestal. La comida queda a pasos de cada casa.",
         ["Chaya, plátano, papaya, pitahaya, limón", "Milpa y huerto común", "Vivero de árboles nativos"], "frutales y milpa"),
    ], "Foto pendiente"),
    sin_show="<p>Creemos que la verdadera resiliencia de una comunidad, y mejor aún su antifragilidad, está en los lazos entre sus miembros y entre la comunidad y su contexto local: Acanceh y su gente. Esos lazos nos hacen más fuertes que cualquier barda, cerca o arma ante un colapso como el que hoy muchos vaticinan.</p><p>Por eso buscamos agua limpia y suficiente, energía fuera de la red y producir buena parte de nuestra comida, con excedentes para intercambiar con otros. Más adelante podríamos crear monedas solidarias y proyectos de intercambio con nuestros vecinos, para que esos lazos sigan creciendo.</p>",
    e3_h="La etapa 3, cluster por cluster.",
    e3_lede=f"Tres hectáreas al poniente del predio. Dos calles onduladas de 6 m reparten {N_LOTES} lotes en tres franjas, agrupados en {N_CL} clusters: {POR_TAM[8]} de 8 lotes, {POR_TAM[4]} de 4 y {POR_TAM[2]} de 2. Toca un lote para cotizarlo solo, el chapoteadero de un cluster para cotizarlo completo, o un ícono i para saber qué es cada zona.",
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
    pr_letra="Enganche de $10,000 por lote en todos los plazos. Si liquidas antes, pagas el precio del plazo en que terminas. El precio de preventa sube 5% cada vez que se venden 4 lotes. La cuota de mantenimiento es anual, de " + CUOTA + " por lote; se cobra a cada cluster desde que inician obras que lo benefician y se ajusta según lo que necesite la comunidad. Precios en pesos mexicanos, sin intereses.",
    part_h="Qué te da tu participación, y qué no.",
    part_lede="Tu participación son acciones de una serie de la SAPI de C.V. de La Tokenizadora, representadas por un token. Con ellas recibes el uso vitalicio de uno o varios lotes de 200 m² y voz en cómo se cuida la tierra.",
    si_h="Incluye",
    si_items=li([
        ("Uso vitalicio de tus lotes", "Desde un lote de 200 m², o un cluster de 2, 4 u 8, en la etapa 3"),
        ("Agua, energía y comida comunes", "Pozo, centro solar, caminos verdes y bosque agroforestal, con cuota de mantenimiento"),
        ("Construir en tus lotes", "Tipo, materiales y tamaño según el reglamento de construcción"),
        ("Voto en las decisiones sobre la tierra", "Reglas, mejoras y admisión de nuevos miembros"),
        ("Herencia y reventa", "Tu derecho pasa a tus herederos o a quien compre, con admisión por la comunidad"),
    ]),
    no_h="No incluye",
    no_items=li([
        ("Escritura individual", "La tierra es de la sociedad; tu derecho queda en el registro de acciones"),
        ("Desmonte por tu cuenta", "Cualquier claro se decide en común y con permiso"),
        ("Promesa de rendimiento o plusvalía", "El valor está en el uso y la comunidad"),
    ]),
    part_nota="Los derechos se fijan en los estatutos, el reglamento de uso y tu contrato, que recibes al apartar.",
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
    es_lede="Preferimos poner el dinero en agua, energía y comida que en trámites, sin perder el rigor: cada participación está respaldada por acciones.",
    capas=capas([
        ("La tierra", "El predio pertenece a una serie accionaria de la SAPI de C.V. de La Tokenizadora, creada para Bosque Venado. Nadie lo puede dividir ni vender por partes."),
        ("Tu participación", "Son acciones de esa serie, inscritas en el registro de accionistas desde que firmas. Eso te da certeza jurídica inmediata, sin escriturar cada lote ni pagar notaría en cada operación."),
        ("El token", "Representa tus acciones y les da fluidez: puedes heredarlas, darlas en garantía o traspasarlas. No es anónimo: cada cambio de titular lo aprueba la comunidad."),
    ]),
    faq_h="Preguntas frecuentes.",
    faq=faq([
        ("¿Qué significa preventa?", "Que lo común se está construyendo con las primeras participaciones. Por eso el precio es más bajo ahora y sube 5% cada vez que se venden 4 lotes."),
        ("¿Por qué no se escritura cada lote?", "Porque la tierra es de la sociedad y tu derecho vive en tus acciones. Así no hay gastos notariales en cada compra, herencia o traspaso, y tienes certeza jurídica desde que quedas inscrito en el registro de accionistas."),
        ("¿Puedo comprar un solo lote?", "Sí, desde un lote de 200 m². Los clusters de 2, 4 u 8 son para quien quiere más espacio o comprar con amigos o familia; cada quien tiene sus acciones y el reglamento fija el uso dentro del cluster."),
        ("Si compro un lote de atrás, ¿cómo entro en auto?", "En la franja central, entre las dos calles, todos los lotes dan a una calle. En las franjas de los lados, cada lote de atrás tiene paso propio: por el camino verde junto a su cluster, que lleva dos huellas de concreto para entrar a vuelta de rueda, por la servidumbre de 3 m de los clusters de 8, por la calle del sur o por el centro de energía y agua. En el plano, cada lote dice cuál es su acceso."),
        ("¿Puedo construir?", "Sí, según el reglamento de construcción, que fija tipo, materiales y tamaño. Lo recibes al apartar tu lote."),
        ("¿Puedo vender, heredar o dar en garantía mi participación?", "Sí. Tu derecho de uso se transmite con tus acciones, en los términos que fijen los estatutos. Quien las reciba pasa por el mismo proceso de admisión que tú."),
        ("¿Hay agua y luz?", "Hay un pozo con agua a 27 metros. No hay red eléctrica: una de las casas habitadas funciona con paneles solares y baterías, y el centro de energía y agua da servicio a lo común."),
        ("¿Cuánto es la cuota de mantenimiento?", CUOTA + " al año por lote. Se empieza a cobrar a cada cluster cuando inician obras que lo benefician. Cubre la calle, el agua, la energía común y el cuidado del bosque, y lo que sobra forma una reserva económica de la sociedad para imprevistos y mejoras. El monto se ajusta según lo que necesite la comunidad."),
        ("¿Qué pasa si dejo de pagar?", "Tienes un plazo de gracia para ponerte al corriente. Si no se resuelve, tu participación se subasta primero entre los vecinos de la comunidad, que ya pasaron por la admisión; si nadie la toma, pasa a La Tokenizadora. Lo que hayas aportado hasta entonces puede perderse a favor de la sociedad, según tu contrato."),
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
    f_privacidad='Al enviar aceptas el <a href="aviso-de-privacidad.html">aviso de privacidad</a>.',
    ilustrativo="Ubicación y forma de la aguada y los chapoteaderos, ilustrativas.",
    pie_1="<strong>Bosque Venado</strong><br>Tablaje 3735, Seyé, Yucatán.<br>Tokenizado por La Tokenizadora.",
    pie_2="Esta página es informativa y no constituye una oferta pública de valores ni promesa de rendimiento. Las participaciones se ofrecen solo de forma privada, previa visita y admisión. La tierra se posee de forma colectiva bajo los estatutos de la sociedad. <a href=\"aviso-de-privacidad.html\">Aviso de privacidad</a>.",
    JS=dict(
        locale="es-MX", estado_url="estado.json", jspdf="vendor/jspdf-2.5.1.umd.min.js", correo=CORREO,
        meses="{n} meses", contado="Contado", na="N/A", mens_etq="{n} mensualidades", unico="Pago único", al_mes="al mes", incluido="Incluido",
        cluster="Cluster", lote="Lote", lotes="lotes", lotes_t="Lotes", de="de", tam="Tamaño", medidas="Medidas", acceso_t="Acceso",
        acceso={"calle": "Frente a la calle", "calle2": "Por la calle de atrás", "camino": "Por el camino verde", "serv": "Por la servidumbre de paso", "sur": "Por la calle del sur", "energia": "Por el centro de energía y agua"},
        ver_cl="Cotizar el cluster {c} completo ({n} lotes)",
        stc={"disponible": "Disponible completo", "parcial": "Con lotes disponibles", "apartado": "Apartado", "vendido": "Vendido"}, sup="Superficie", frente="Frente a la calle", fondo="Fondo", ubic="Ubicación", estado="Estado",
        banda={"poniente": "Franja poniente", "centro": "Franja central, entre las dos calles", "oriente": "Franja oriente"},
        st={"disponible": "Disponible", "apartado": "Apartado", "vendido": "Vendido"},
        cuenta="{d} de {t} lotes disponibles; {c} clusters completos.", quitar="Quitar selección", ficha_vacia="Elige un lote o un cluster en el plano, o cotiza por número de lotes.",
        t_cap="Todos los plazos para {u} ({m})", total_c="total",
        wa_txt="Hola, me interesa Bosque Venado.",
        co_plazo="Plazo", pr_eng="Enganche", pr_total="Precio total", pr_m2="Precio por m²", pr_ahorro="Ahorro contra 60 meses",
        pr_th1="Plazo", pr_th2="Mensualidad", pr_th3="Total", pr_th4="Descuento", mens_pdf="Mensualidad ({n} pagos)",
        pdf_sub="Cotización de la etapa 3. Tablaje 3735, Seyé, Yucatán.", pdf_folio="Folio", pdf_sin="{u}, por asignar",
        pdf_mapa="Etapa 3", pdf_calle="Calle al sur", pdf_contacto="Contacto", pdf_archivo="Cotizacion-Bosque-Venado",
        pdf_notas="Enganche de $10,000 por lote. Si liquidas antes, pagas el precio del plazo en que terminas. Precios en pesos mexicanos, sin intereses. El precio de preventa sube 5% cada vez que se venden 4 lotes. Esta cotización no aparta el lote: se reserva solo con el apartado firmado. La cuota de mantenimiento es de $1,000 al año por lote y se cobra desde que inician obras en el cluster.",
        pdf_legal="Documento informativo. No constituye una oferta pública de valores ni promesa de rendimiento. Las participaciones son acciones de una serie de la SAPI de C.V. de La Tokenizadora y se ofrecen solo de forma privada, previa visita y admisión.",
        tramo_txt="Preventa, tramo {n}: {p} por m². Quedan {q} {l} a este precio; después sube 5%.", lote1="lote",
        pdf_gen="Generando el PDF…", pdf_ok="Listo. Revisa tus descargas.", pdf_err="No se pudo generar el PDF. Revisa tu conexión e inténtalo de nuevo.",
        vi_correo="Correo",
        info={
            "calle": {"t": "Calles", "d": "Dos calles de 6 m de sascab compactado, doble sentido a vuelta de rueda. Las curvas bajan la velocidad y el ruido. Las dos salen a la calle del sur."},
            "corredor": {"t": "Camino verde", "d": "Corredor de 4 m entre clusters. Dos huellas de concreto para entrar en auto a los lotes de atrás, y frutales de porte bajo a los lados. Es el sendero de recolección."},
            "energia": {"t": "Centro de energía y agua", "d": "Paneles solares, baterías y el pozo con su tanque elevado. Puede alojar un estacionamiento compartido."},
            "aguada": {"t": "Aguada", "d": "Un estanque que guarda el agua de lluvia, riega los frutales y da refugio a aves y fauna. "},
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
    com_lede="We believe a community's strength lies in its ties: among its members, and between the community and Acanceh and its people. That is why we want clean water, our own power and enough food to share and trade. We are in pre-sale: every stake funds what we share.",
    com_items=cuatro([
        ("Water, power and food", "Well, sun and planting, solved together, with surplus to trade."),
        ("Ties with Acanceh", "We want to grow together with the town: local work, trade and, later on, community currencies with our neighbors."),
        ("Trust among peers", "We all know each other. The community approves who joins and who leaves; no one takes part anonymously."),
        ("Legal rigor", "Everything is tokenized and backed by shares in a series of a SAPI de C.V., with bylaws and rules."),
    ]),
    reg_etq="Living together", reg_h="Community rules, in outline.",
    reg_lede="The basics for living together. We start simple; as the community grows, it writes and votes on the final version itself.",
    reglas=reglas([
        ("Joining and leaving", ["A visit and a conversation before joining", "The community approves every new member", "Heirs and buyers go through the same admission"]),
        ("Decisions", ["Regular members' assembly", "We vote on what concerns everyone", "As we grow, the community designs its own model"]),
        ("Forest and planting", ["No clearing without a shared agreement", "Native species and fruit trees", "The green lanes belong to everyone"]),
        ("Building", ["Materials and heights set by the rules", "The easement is respected"]),
        ("Water and power", ["Careful use of the well and tank", "Each house can add its own system", "Shared systems are kept up with a fee"]),
        ("Daily life", ["Quiet at night", "Pets in their owners' care", "Visitors announced to the community"]),
        ("Shared work", ["Work days in the garden and lanes", "Shared harvests are divided and surplus is traded", "Everyone brings their own skills"]),
        ("Fees and conflicts", ["MXN " + CUOTA + " a year per lot, once works start on its cluster", "What is left goes to the company's shared reserve", "Talk first, then mediation", "If someone stops paying, their stake is auctioned among the neighbors"]),
    ]),
    qs_etq="Who we are", qs_h="The people behind Bosque Venado.",
    qs_lede="The founders and first members of the community. Each one brings their own skills to what we share.",
    gente=gente([
        ("Juan Carlos Soto", "Founder. Artist and entrepreneur."),
        ("María Cecilia Botero", "Founder. Artist and entrepreneur."),
        ("Alejandro Vélez", "Founder. Artist and entrepreneur."),
    ], "Photo pending"),
    in_etq="References", in_h="Communities that inspire us.",
    in_lede="Real projects in Mexico that have lived this way for years. We cite them as inspiration; they are not testimonials from Bosque Venado.",
    referentes=referentes([
        ("Huehuecoyotl", "Sierra del Tepozteco, Morelos. Since 1982.",
         "An ecovillage where each family built its own house and everyone together built the road, rainwater harvesting, a theater and the farmland. The land is managed in common, by agreement among its members.",
         "https://ecovillage.org/resources-library/article/what-is-our-ecovillage/", "Read their story"),
        ("Las Cañadas", "Near Huatusco, Veracruz.",
         "An agroecology cooperative and permaculture center that cares for one of the last islands of cloud forest in central Veracruz, with a food forest and agroecology training.",
         "https://source.ecoversities.org/Ecoversity:Cooperativa_Agroecologica_Las_Ca%C3%B1adas", "Learn about the cooperative"),
    ]),
    vo_etq="Voices", vo_h="What the people already here say.",
    vo_lede="Sample testimonials, while we collect those of the people living in phases 1 and 2.",
    voces=voces([
        ("We came for the quiet and stayed for the people. Saturday work days in the garden are now the best part of the week.", "Mariana", "Phase 1"),
        ("We bought a cluster of 4 with my brothers. The kids know the forest and we learned to look after the water.", "Tomás", "Cluster of 4 lots"),
        ("What won me over was the clarity: I know what I have, what I don't and how decisions are made. And the well and panels already work.", "Daniela", "First lot"),
    ], "Sample"),
    cta_visita="Book a visit", cta_clusters="See available clusters",
    menu="Menu", cerrar="Close", agenda="Book", wa_label="Message us on WhatsApp", nav_visita="Visit",
    hero_tag="Your own water, power and food, in the forest near Acanceh.",
    foto_pend="Photo pending", f_hero="A sascab road between palms and forest",
    f_ceiba="A pale-trunked ceiba with wide roots in the forest", f_ceiba_cap="The ceiba, the sacred Maya tree, in the Yucatán forest",
    predio_t="The whole parcel",
    predio_p="The parcel covers 7 hectares. On the east side are phases 1 and 2, 2 hectares each: phase 1 is La Villa Vikinga, where the three buildings stand, and phase 2 is a private project by Alejandro Vélez, a home and a center for technology and rural experimentation. Phase 3 takes the 3 western hectares, facing the south street, and is the one for sale.",
    part_etq="Your stake", en_etq="How to join", es_etq="Structure",
    h1="Your own water, power and food, in the forest.",
    hero_lede=f"Bosque Venado is a neo-rural community in Acanceh, Yucatán. Phase 3 has {N_LOTES} lots of 200 m². You can buy a single lot, or a cluster of 2, 4 or 8 with friends or family, with fruit-tree lanes between them and a shared solar power and well water hub.",
    plan_cap="Based on the topographic survey of parcel 3735. The layout is schematic and may be adjusted in the final project.",
    d1_t="Parcel", d1="7 hectares",
    d2_t="Phase 3, for sale", d2="3 hectares",
    d3_t="Lots of 200 m²", d3=f"{N_LOTES} in {N_CL} clusters",
    d4_t="Common areas", d4=f"{COMUN} of the phase",
    lugar_h="The forest first, everything else after.",
    lugar_lede="There is already life on the land: well water, solar power and three buildings. Shared infrastructure is built together, with a light footprint and off the grid.",
    hoy_h="What is there today",
    hoy_items=li([
        ("Well water", "Reached at 27 meters"),
        ("Solar power", "Panels and batteries in one of the lived-in houses"),
        ("Three buildings", "In La Villa Vikinga, phase 1"),
        ("Frontage on the south street", "Direct access to phase 3"),
        ("Close to Acanceh", "About 1.2 km along Calle 19, per the survey sketch"),
    ]),
    juntos_h="What we build together",
    juntos_items=li([
        ("Two sascab streets", "They serve every cluster from the south street"),
        ("Power and water hub", "Panels, batteries, well and elevated tank"),
        ("Green lanes with fruit trees", "Between every cluster"),
        ("Food forest and nursery", "In the spare corners of the phase"),
        ("Rain pond and wading pools", "They hold the rain and cool the clusters"),
        ("Shared palapa and storage", "For meeting up and keeping tools"),
    ]),
    vida_h="What we share is what sustains you.",
    vida_lede="The amenities at Bosque Venado are the water, power and food the community produces and looks after together.",
    pilares=pilares([
        ("Water", "The well already gives water at 27 meters. It is pumped with solar power to an elevated tank and flows by gravity to the clusters.",
         ["Existing well", "Shared elevated tank", "Rain pond and wading pools"], "the well and the tank"),
        ("Power", "A hub of panels and batteries for shared needs, and every house can add its own system. No grid needed.",
         ["Solar panels and batteries", "Solar water pumping", "Lane lighting"], "the panels on the lived-in house"),
        ("Food", "A green lane with fruit trees runs between clusters, and the spare corners are planted as a food forest. Food is a few steps from every house.",
         ["Chaya, banana, papaya, dragon fruit, lime", "Milpa and shared garden", "Native tree nursery"], "fruit trees and milpa"),
    ], "Photo pending"),
    sin_show="<p>We believe the real resilience of a community, and better yet its antifragility, lies in the ties among its members and between the community and its local context: Acanceh and its people. Those ties make us stronger than any wall, fence or weapon in the kind of collapse many people predict today.</p><p>That is why we aim for clean and sufficient water, off-grid power and growing much of our own food, with surplus to trade with others. Later on we could create community currencies and exchange projects with our neighbors, so those ties keep growing.</p>",
    e3_h="Phase 3, cluster by cluster.",
    e3_lede=f"Three hectares on the west side of the parcel. Two winding 6 m streets serve {N_LOTES} lots in three strips, grouped in {N_CL} clusters: {POR_TAM[8]} of 8 lots, {POR_TAM[4]} of 4 and {POR_TAM[2]} of 2. Tap a lot to get a quote for it, a cluster's wading pool to quote the whole cluster, or an i icon to learn what each area is.",
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
    pr_letra="MXN $10,000 down payment per lot on every term. If you pay off early, you pay the price of the term in which you finish. The pre-sale price goes up 5% every time 4 lots are sold. The maintenance fee is annual, MXN " + CUOTA + " per lot; it is charged to each cluster once works that benefit it begin, and adjusted to what the community needs. Prices in Mexican pesos, interest-free.",
    part_h="What your stake gives you, and what it doesn't.",
    part_lede="Your stake is a set of shares in a series of La Tokenizadora's SAPI de C.V., represented by a token. It gives you lifetime use of one or more 200 m² lots and a say in how the land is cared for.",
    si_h="Included",
    si_items=li([
        ("Lifetime use of your lots", "From a single 200 m² lot, or a cluster of 2, 4 or 8, in phase 3"),
        ("Shared water, power and food", "Well, solar hub, green lanes and food forest, with a maintenance fee"),
        ("Building on your lots", "Type, materials and size set by the building rules"),
        ("A vote on decisions about the land", "Rules, improvements and admission of new members"),
        ("Inheritance and resale", "Your right passes to your heirs or to a buyer, with admission by the community"),
    ]),
    no_h="Not included",
    no_items=li([
        ("An individual deed", "The land belongs to the company; your right is recorded in the share register"),
        ("Clearing land on your own", "Any clearing is decided together and with permits"),
        ("A promise of returns or appreciation", "The value is in the use and the community"),
    ]),
    part_nota="Your rights are set by the bylaws, the use rules and your contract, which you receive when you reserve.",
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
    es_lede="We would rather put money into water, power and food than into paperwork, without giving up rigor: every stake is backed by shares.",
    capas=capas([
        ("The land", "The property belongs to a share series of La Tokenizadora's SAPI de C.V., created for Bosque Venado. No one can split it up or sell it in pieces."),
        ("Your stake", "It is a set of shares in that series, entered in the share register as soon as you sign. That gives you legal certainty right away, without a deed for each lot or notary fees on every transaction."),
        ("The token", "It represents your shares and makes them easy to move: you can pass them on, pledge them as collateral or transfer them. It is not anonymous: the community approves every change of holder."),
    ]),
    faq_h="Frequently asked questions.",
    faq=faq([
        ("What does pre-sale mean?", "That the shared infrastructure is being built with the first stakes. That is why the price is lower now and goes up 5% every time 4 lots are sold."),
        ("Why is there no deed for each lot?", "Because the land belongs to the company and your right lives in your shares. That means no notary fees on each purchase, inheritance or transfer, and legal certainty from the moment you are entered in the share register."),
        ("Can I buy a single lot?", "Yes, from one 200 m² lot. Clusters of 2, 4 or 8 are for people who want more space or to buy with friends or family; each person holds their own shares and the rules set use inside the cluster."),
        ("If I buy a back lot, how do I drive in?", "In the middle strip, between the two streets, every lot faces a street. In the side strips, every back lot has its own access: the green lane next to its cluster, with two concrete wheel tracks for driving in at walking pace, the 3 m easement in clusters of 8, the south street or the power and water hub. On the plan, each lot shows its access."),
        ("Can I build?", "Yes, under the building rules, which set type, materials and size. You receive them when you reserve your lot."),
        ("Can I sell, pass on or pledge my stake?", "Yes. Your right of use transfers with your shares, on the terms set by the bylaws. The new holder goes through the same admission process you did."),
        ("Is there water and power?", "There is a well with water at 27 meters. There is no grid connection: one of the lived-in houses runs on solar panels and batteries, and the power and water hub serves the shared areas."),
        ("How much is the maintenance fee?", "MXN " + CUOTA + " a year per lot. It is charged to each cluster once works that benefit it begin. It covers the street, water, shared power and forest care, and whatever is left builds the company's financial reserve for contingencies and improvements. The amount is adjusted to what the community needs."),
        ("What happens if I stop paying?", "You get a grace period to catch up. If it is not resolved, your stake is auctioned first among the neighbors in the community, who have already been through admission; if no one takes it, it passes to La Tokenizadora. What you have paid in up to then may be lost in favor of the company, as set in your contract."),
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
    f_privacidad='By sending you accept the <a href="privacy.html">privacy notice</a>.',
    ilustrativo="Location and shape of the rain pond and wading pools are illustrative.",
    pie_1="<strong>Bosque Venado</strong><br>Parcel 3735, Seyé, Yucatán, Mexico.<br>Tokenized by La Tokenizadora.",
    pie_2="This page is for information only and is not a public offering of securities or a promise of returns. Stakes are offered privately only, after a visit and admission. The land is held collectively under the company's bylaws. <a href=\"privacy.html\">Privacy notice</a>.",
    JS=dict(
        locale="en-US", estado_url="../estado.json", jspdf="../vendor/jspdf-2.5.1.umd.min.js", correo=CORREO,
        meses="{n} months", contado="Cash", na="N/A", mens_etq="{n} monthly payments", unico="Single payment", al_mes="per month", incluido="Included",
        cluster="Cluster", lote="Lot", lotes="lots", lotes_t="Lots", de="of", tam="Size", medidas="Size", acceso_t="Access",
        acceso={"calle": "Facing the street", "calle2": "From the street behind", "camino": "Through the green lane", "serv": "Through the easement", "sur": "From the south street", "energia": "Through the power and water hub"},
        ver_cl="Quote the whole cluster {c} ({n} lots)",
        stc={"disponible": "Fully available", "parcial": "Some lots available", "apartado": "Reserved", "vendido": "Sold"}, sup="Area", frente="Street frontage", fondo="Depth", ubic="Location", estado="Status",
        banda={"poniente": "West strip", "centro": "Middle strip, between the two streets", "oriente": "East strip"},
        st={"disponible": "Available", "apartado": "Reserved", "vendido": "Sold"},
        cuenta="{d} of {t} lots available; {c} full clusters.", quitar="Clear selection", ficha_vacia="Choose a lot or a cluster on the plan, or get a quote by number of lots.",
        t_cap="Every term for {u} ({m})", total_c="total",
        wa_txt="Hi, I am interested in Bosque Venado.",
        co_plazo="Term", pr_eng="Down payment", pr_total="Total price", pr_m2="Price per m²", pr_ahorro="Savings vs. 60 months",
        pr_th1="Term", pr_th2="Monthly", pr_th3="Total", pr_th4="Discount", mens_pdf="Monthly payment ({n} payments)",
        pdf_sub="Phase 3 quote. Parcel 3735, Seyé, Yucatán, Mexico.", pdf_folio="Ref.", pdf_sin="{u}, to be assigned",
        pdf_mapa="Phase 3", pdf_calle="South street", pdf_contacto="Contact", pdf_archivo="Bosque-Venado-quote",
        pdf_notas="MXN $10,000 down payment per lot. If you pay off early, you pay the price of the term in which you finish. Prices in Mexican pesos, interest-free. The pre-sale price goes up 5% every time 4 lots are sold. This quote does not reserve the lot: it is reserved only with a signed reservation. The maintenance fee is MXN $1,000 a year per lot, charged once works start on the cluster.",
        pdf_legal="For information only. Not a public offering of securities or a promise of returns. Stakes are shares in a series of La Tokenizadora's SAPI de C.V. and are offered privately only, after a visit and admission.",
        tramo_txt="Pre-sale, tier {n}: {p} per m². {q} {l} left at this price; then it goes up 5%.", lote1="lot",
        pdf_gen="Generating the PDF…", pdf_ok="Done. Check your downloads.", pdf_err="The PDF could not be generated. Check your connection and try again.",
        vi_correo="Email",
        info={
            "calle": {"t": "Streets", "d": "Two 6 m streets of compacted sascab, two-way at walking pace. The curves slow cars and keep noise down. Both connect to the south street."},
            "corredor": {"t": "Green lane", "d": "A 4 m lane between clusters. Two concrete wheel tracks for driving to the back lots, with low fruit trees on both sides. It is the harvest path."},
            "energia": {"t": "Power and water hub", "d": "Solar panels, batteries and the well with its elevated tank. It can also hold shared parking."},
            "aguada": {"t": "Rain pond", "d": "A pond that stores rainwater, waters the fruit trees and gives shelter to birds and wildlife. "},
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


PRIV = {
    "es": dict(lang="es-MX", archivo="aviso-de-privacidad.html", title="Aviso de privacidad, Bosque Venado", volver="Volver a Bosque Venado", href="./",
        h1="Aviso de privacidad", act="Última actualización: 11 de noviembre de 2026.",
        cuerpo=[
            ("Quién es responsable de tus datos", f"{RAZON}, con domicilio en {DOMICILIO}, es responsable del tratamiento de los datos personales que nos compartes en bosquevenado.com. Puedes escribirnos a <a href=\"mailto:{CORREO}\">{CORREO}</a>."),
            ("Qué datos recabamos", "Solo los que escribes en el formulario de visita: nombre, correo, WhatsApp, el lote o cluster que te interesa, el plazo que te interesa y lo que nos cuentes sobre cómo usarías el lugar. No pedimos datos sensibles ni datos de pago."),
            ("Para qué los usamos", "Para contestarte, coordinar tu visita al predio, enviarte cotizaciones y darte seguimiento en el proceso de admisión a la comunidad. No los usamos para publicidad ni los vendemos."),
            ("Con quién los compartimos", "Con nadie fuera del equipo de Bosque Venado y La Tokenizadora. El formulario se guarda en Netlify, el servicio que aloja este sitio, que actúa solo como proveedor."),
            ("Tus derechos", f"Puedes pedir en cualquier momento acceder a tus datos, corregirlos, cancelarlos u oponerte a su uso (derechos ARCO), o retirar tu consentimiento. Escríbenos a <a href=\"mailto:{CORREO}\">{CORREO}</a> con tu nombre y lo que necesitas, y te respondemos en un máximo de 20 días hábiles."),
            ("Cambios a este aviso", "Si cambiamos este aviso, publicaremos la nueva versión en esta misma página."),
        ]),
    "en": dict(lang="en", archivo="en/privacy.html", title="Privacy notice, Bosque Venado", volver="Back to Bosque Venado", href="./",
        h1="Privacy notice", act="Last updated: November 11, 2026.",
        cuerpo=[
            ("Who is responsible for your data", f"{RAZON}, located at {DOMICILIO}, Mexico, is responsible for the personal data you share with us at bosquevenado.com. You can write to us at <a href=\"mailto:{CORREO}\">{CORREO}</a>."),
            ("What data we collect", "Only what you enter in the visit form: name, email, WhatsApp, the lot or cluster you are interested in, the payment term and what you tell us about how you would use the place. We do not ask for sensitive data or payment details."),
            ("What we use it for", "To reply to you, arrange your visit, send you quotes and follow up during the admission process. We do not use it for advertising and we do not sell it."),
            ("Who we share it with", "No one outside the Bosque Venado and La Tokenizadora team. The form is stored by Netlify, the service that hosts this site, acting only as a provider."),
            ("Your rights", f"You can ask at any time to access, correct or delete your data, object to its use, or withdraw your consent. Write to <a href=\"mailto:{CORREO}\">{CORREO}</a> with your name and what you need, and we will reply within 20 business days."),
            ("Changes to this notice", "If we change this notice, we will publish the new version on this page."),
        ]),
}

PRIV_TPL = """<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><meta name="robots" content="noindex, nofollow">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500&display=swap" rel="stylesheet">
<style>body{{margin:0;background:#F2EFE9;color:#0E100D;font-family:"Inter Tight","Helvetica Neue",Arial,sans-serif;font-weight:300;font-size:1.05rem;line-height:1.6}}
main{{max-width:720px;margin:0 auto;padding:56px 20px 80px}}a{{color:inherit}}
h1{{font-weight:300;text-transform:uppercase;font-size:clamp(2rem,5vw,3rem);line-height:1;margin:.6em 0 .3em}}
h2{{font-weight:400;text-transform:uppercase;font-size:.85rem;letter-spacing:.03em;margin:2.2em 0 .5em;border-top:1px solid #0E100D;padding-top:14px}}
.act{{color:#5F625B;font-size:.9rem}}.volver{{font-size:.82rem;text-transform:uppercase;letter-spacing:.03em}}
.tbd{{background:rgba(216,178,62,.3);border-bottom:1px dashed #8a6a12;padding:0 .2em}}</style></head>
<body><main><a class="volver" href="{href}">{volver}</a><h1>{h1}</h1><p class="act">{act}</p>{secciones}</main></body></html>
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
    for key, d in PRIV.items():
        secc = "".join(f"<h2>{a}</h2><p>{b}</p>" for a, b in d["cuerpo"])
        (ROOT / d["archivo"]).write_text(PRIV_TPL.format(secciones=secc, **{k: v for k, v in d.items() if k != "cuerpo"}))
    for key, path in (("es", ROOT / "gracias.html"), ("en", ROOT / "en" / "gracias.html")):
        lang, title, h1, p, href, back = GRACIAS[key]
        path.write_text(GR_TPL.format(lang=lang, title=title, h1=h1, p=p, href=href, back=back))
    print(json.dumps({"lotes": N_LOTES, "clusters": N_CL, "por_tamano": POR_TAM, "comun": COMUN}, indent=1))


if __name__ == "__main__":
    main()
