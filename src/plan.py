"""Geometría del predio (plano topográfico Tab. 3735, Seyé) y planos SVG.

Coordenadas UTM del cuadro de construcción. Se giran 0°50'38" para que los
linderos poniente y oriente (paralelos entre sí) queden verticales.

Etapas de oriente a poniente: la 1 junto a la calle oriente, la 2 al centro y
la 3 al poniente. La etapa 3 es la que se lotifica.

LAYOUT elige la lotificación de la etapa 3:
  "rect": lotes de 11.11 x 18 m con dos vías de 7 m norte-sur.
  "hex":  lotes hexagonales de 200 m² rodeados por senderos de 3 m.
"""
import math
import random

LAYOUT = "rect"

P_UTM = [
    (246757.404, 2303902.805),  # 1
    (246761.356, 2304171.082),  # 2
    (246946.724, 2304204.736),  # 3
    (247037.204, 2304221.162),  # 4
    (247033.660, 2303980.554),  # 5
]

ANG = math.atan2(P_UTM[1][0] - P_UTM[0][0], P_UTM[1][1] - P_UTM[0][1])
OX, OY = P_UTM[0]


def rot(x, y):
    dx, dy = x - OX, y - OY
    c, s = math.cos(ANG), math.sin(ANG)
    return (dx * c - dy * s, dx * s + dy * c)


POLY = [rot(*p) for p in P_UTM]
W = POLY[4][0]
Y_NW, Y_NE, Y_SE = POLY[1][1], POLY[3][1], POLY[4][1]


def y_n(x):
    return Y_NW + (Y_NE - Y_NW) / W * x


def y_s(x):
    return Y_SE / W * x


def area_to(x):
    return Y_NW * x - 0.5 * (Y_NW - (Y_NE - Y_SE)) / W * x * x


def shoelace(p):
    n = len(p)
    return abs(sum(p[i][0] * p[(i + 1) % n][1] - p[(i + 1) % n][0] * p[i][1] for i in range(n))) / 2


AREA = shoelace(POLY)


def solve(target):
    lo, hi = 0.0, W
    for _ in range(100):
        m = (lo + hi) / 2
        if area_to(m) < target:
            lo = m
        else:
            hi = m
    return m


# Cortes de poniente a oriente; etapa 3 = [0, C1], etapa 2 = [C1, C2], etapa 1 = [C2, W]
C1, C2 = solve(AREA / 3), solve(2 * AREA / 3)
BANDS = {3: (0.0, C1), 2: (C1, C2), 1: (C2, W)}
ETAPA_AREA = {3: area_to(C1), 2: area_to(C2) - area_to(C1), 1: AREA - area_to(C2)}
X0, X1 = BANDS[3]
SETBACK = 1.0
LOT_AREA = 200.0


def inside(x, y, sb=SETBACK):
    return X0 + sb <= x <= X1 - sb and y_s(x) + sb <= y <= y_n(x) - sb


def band_poly(x0, x1):
    return [(x0, y_s(x0)), (x0, y_n(x0)), (x1, y_n(x1)), (x1, y_s(x1))]


# ---------- lotificación rectangular ----------
R_DEPTH, R_ROAD = 18.0, 7.0
R_FRONT = LOT_AREA / R_DEPTH
R_COLS = [("L", R_DEPTH), ("R", R_ROAD), ("L", R_DEPTH), ("L", R_DEPTH), ("R", R_ROAD), ("L", R_DEPTH)]


def lots_rect():
    x = X0 + SETBACK
    lots, ways = [], []
    for kind, w in R_COLS:
        if kind == "R":
            ways.append(band_poly(x, x + w))
        else:
            ylo = max(y_s(x), y_s(x + w)) + SETBACK
            yhi = min(y_n(x), y_n(x + w)) - SETBACK
            y = ylo
            while y + R_FRONT <= yhi + 1e-9:
                lots.append([(x, y), (x, y + R_FRONT), (x + w, y + R_FRONT), (x + w, y)])
                y += R_FRONT
        x += w
    return lots, ways


# ---------- lotificación hexagonal ----------
H_SIDE = math.sqrt(LOT_AREA / (3 * math.sqrt(3) / 2))
H_FLAT = math.sqrt(3) * H_SIDE
H_GAP = 3.0


def _hex(cx, cy):
    return [(cx + H_SIDE * math.cos(math.radians(60 * k)), cy + H_SIDE * math.sin(math.radians(60 * k))) for k in range(6)]


def _honeycomb(dx, dy):
    d = H_FLAT + H_GAP
    s = d / math.sqrt(3)
    hx, hy = 1.5 * s, d
    out = []
    for i in range(-2, int((X1 + 20) / hx) + 2):
        for j in range(-2, int(340 / hy) + 2):
            cx = i * hx + dx
            cy = j * hy + dy + (hy / 2 if i % 2 else 0)
            pts = _hex(cx, cy)
            if all(inside(x, y) for x, y in pts):
                out.append(pts)
    return out


def lots_hex():
    best = None
    for dx in [k * 0.5 for k in range(40)]:
        for dy in [k * 1.0 for k in range(20)]:
            r = _honeycomb(dx, dy)
            if best is None or len(r) > len(best):
                best = r
    best.sort(key=lambda p: (round(sum(x for x, _ in p) / 6, 1), sum(y for _, y in p) / 6))
    return best, []


def build(layout):
    lots, ways = lots_rect() if layout == "rect" else lots_hex()
    return [{"n": i, "pts": p} for i, p in enumerate(lots, 1)], ways


LOTS, WAYS = build(LAYOUT)
LOTS_TOTAL = len(LOTS) * LOT_AREA
COMMON_E3 = ETAPA_AREA[3] - LOTS_TOTAL


def _pts(points, tf):
    return " ".join(f"{tf(x, y)[0]:.1f},{tf(x, y)[1]:.1f}" for x, y in points)


def _center(p):
    return (sum(x for x, _ in p) / len(p), sum(y for _, y in p) / len(p))


def _trees(x0, x1, tf, seed, n, rmin, rmax):
    rnd = random.Random(seed)
    placed = []
    tries = 0
    while len(placed) < n and tries < n * 60:
        tries += 1
        x = rnd.uniform(x0 + 2, x1 - 2)
        y = rnd.uniform(y_s(x) + 2, y_n(x) - 2)
        r = rnd.choice([rmin, (rmin + rmax) / 2, rmax])
        if any(math.hypot(x - a, y - b) < (r + rr) * 1.15 for a, b, rr in placed):
            continue
        placed.append((x, y, r))
    out = []
    for x, y, r in placed:
        sx, sy = tf(x, y)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r * tf.s:.1f}" class="p-tree t{int(r * 7) % 3}"/>')
    return out


def make_tf(s, pad_x, pad_y, ymax, x_off=0.0):
    def tf(x, y):
        return ((x - x_off) * s + pad_x, (ymax - y) * s + pad_y)
    tf.s = s
    return tf


def _lots_layer(tf, interactive, t, lots, ways):
    o = [f'<polygon points="{_pts(band_poly(X0, X1), tf)}" class="p-common"/>']
    for w in ways:
        o.append(f'<polygon points="{_pts(w, tf)}" class="p-road"/>')
    for lot in lots:
        if interactive:
            cx, cy = tf(*_center(lot["pts"]))
            o.append(f'<g class="lote" data-lote="{lot["n"]}" tabindex="0" role="button" aria-label="{t["lote"]} {lot["n"]}">'
                     f'<polygon points="{_pts(lot["pts"], tf)}"/>'
                     f'<text x="{cx:.1f}" y="{cy + 4:.1f}" text-anchor="middle">{lot["n"]}</text></g>')
        else:
            o.append(f'<polygon points="{_pts(lot["pts"], tf)}" class="p-lot"/>')
    return o


def overview_svg(t, lots=None, ways=None):
    """Plano completo con las tres etapas. t: diccionario de textos."""
    lots = LOTS if lots is None else lots
    ways = WAYS if ways is None else ways
    s = 1.55
    tf = make_tf(s, 46, 30, Y_NE)
    vw, vh = round(W * s + 46 + 40), round(Y_NE * s + 30 + 64)
    o = [f'<svg class="plan" viewBox="0 0 {vw} {vh}" role="img" aria-labelledby="pl-t pl-d">'
         f'<title id="pl-t">{t["plan_title"]}</title><desc id="pl-d">{t["plan_desc"]}</desc>']
    o.append(f'<polygon points="{_pts(POLY, tf)}" class="p-land"/>')
    o += _trees(C1, W, tf, 11, 330, 2.0, 3.6)
    o += _lots_layer(tf, False, t, lots, ways)
    for c in (C1, C2):
        a, b = tf(c, y_s(c)), tf(c, y_n(c))
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="p-cut"/>')
    o.append(f'<polygon points="{_pts(POLY, tf)}" class="p-edge"/>')
    for i, (x0, x1) in BANDS.items():
        cx = (x0 + x1) / 2
        sx, sy = tf(cx, y_n(cx))
        suf = f' <tspan class="p-sold">({t["vendida"]})</tspan>' if i < 3 else ""
        o.append(f'<text x="{sx:.1f}" y="{sy - 9:.1f}" class="p-stage" text-anchor="middle">{t["etapa"]} {i}{suf}</text>')
    a, b = tf(W * .25, y_s(W * .25)), tf(W * .75, y_s(W * .75))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 24
    angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    o.append(f'<text x="{mx:.1f}" y="{my:.1f}" class="p-street" text-anchor="middle" transform="rotate({angle:.2f} {mx:.1f} {my:.1f})">{t["calle"]}</text>')
    ex, ey = tf(W, (Y_SE + Y_NE) / 2)
    o.append(f'<text x="{ex + 22:.1f}" y="{ey:.1f}" class="p-street" text-anchor="middle" transform="rotate(90 {ex + 22:.1f} {ey:.1f})">{t["calle"]}</text>')
    o.append('<g class="p-north"><path d="M14 52 L22 28 L30 52 L22 46 Z"/><text x="22" y="20" text-anchor="middle">N</text></g>')
    sx0 = vw - 40 - 50 * s
    o.append(f'<g class="p-scale"><line x1="{sx0:.1f}" y1="{vh - 14}" x2="{sx0 + 50 * s:.1f}" y2="{vh - 14}"/>'
             f'<line x1="{sx0:.1f}" y1="{vh - 20}" x2="{sx0:.1f}" y2="{vh - 8}"/><line x1="{sx0 + 50 * s:.1f}" y1="{vh - 20}" x2="{sx0 + 50 * s:.1f}" y2="{vh - 8}"/>'
             f'<text x="{sx0 + 25 * s:.1f}" y="{vh - 22}" text-anchor="middle">50 m</text></g>')
    o.append("</svg>")
    return "\n".join(o)


def detail_svg(t, lots=None, ways=None):
    """Etapa 3 con lotes interactivos."""
    lots = LOTS if lots is None else lots
    ways = WAYS if ways is None else ways
    s = 2.9
    pad_x, pad_y = 30, 16
    ymax = y_n(X1)
    tf = make_tf(s, pad_x, pad_y, ymax, X0)
    vw = round((X1 - X0) * s + pad_x + 14)
    vh = round((ymax - y_s(X0)) * s + pad_y + 34)
    o = [f'<svg class="plan plan-e3" viewBox="0 0 {vw} {vh}" role="group" aria-label="{t["e3_map_label"]}">']
    o += _lots_layer(tf, True, t, lots, ways)
    o.append(f'<polygon points="{_pts(band_poly(X0, X1), tf)}" class="p-edge-soft"/>')
    a, b = tf(X0, y_s(X0)), tf(X1, y_s(X1))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 20
    angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    o.append(f'<text x="{mx:.1f}" y="{my:.1f}" class="p-street" text-anchor="middle" transform="rotate({angle:.2f} {mx:.1f} {my:.1f})">{t["calle"]}</text>')
    o.append("</svg>")
    return "\n".join(o)


def summary(lots=None):
    lots = LOTS if lots is None else lots
    total = len(lots) * LOT_AREA
    return {
        "layout": LAYOUT,
        "area": AREA,
        "etapa_area": ETAPA_AREA[3],
        "lotes": len(lots),
        "lotes_m2": total,
        "comun_m2": ETAPA_AREA[3] - total,
        "comun_pct": (ETAPA_AREA[3] - total) / ETAPA_AREA[3],
    }


if __name__ == "__main__":
    import json
    print(json.dumps(summary(), indent=1))
