"""Geometría del predio (plano topográfico Tab. 3735, Seyé) y planos SVG.

Coordenadas UTM del cuadro de construcción. Se giran 0°50'38" para que los
linderos poniente y oriente (paralelos entre sí) queden verticales.
"""
import math
import random

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


C1, C2 = solve(AREA / 3), solve(2 * AREA / 3)
ETAPA_AREA = [area_to(C1), area_to(C2) - area_to(C1), AREA - area_to(C2)]

# Etapa 3: columnas de lotes de 10 x 20 m con dos vías de 7 m norte-sur.
ROAD, FRONT, DEPTH, SETBACK = 7.0, 10.0, 20.0, 1.0
COLS = [("L", DEPTH), ("R", ROAD), ("L", DEPTH), ("L", DEPTH), ("R", ROAD), ("L", DEPTH)]


def lay_out():
    x = C2
    lots, roads = [], []
    col = 0
    for kind, w in COLS:
        if kind == "R":
            roads.append((x, w))
        else:
            col += 1
            ylo = max(y_s(x), y_s(x + w)) + SETBACK
            yhi = min(y_n(x), y_n(x + w)) - SETBACK
            y = ylo
            while y + FRONT <= yhi + 1e-9:
                lots.append({"x": x, "y": y, "w": w, "h": FRONT, "col": col})
                y += FRONT
        x += w
    for i, lot in enumerate(lots, 1):
        lot["n"] = i
    return lots, roads


LOTS, ROADS = lay_out()
LOT_AREA = FRONT * DEPTH
LOTS_TOTAL = len(LOTS) * LOT_AREA
COMMON_E3 = ETAPA_AREA[2] - LOTS_TOTAL


def _poly_clip_x(x0, x1):
    """Polígono de la franja del predio entre x0 y x1."""
    return [(x0, y_s(x0)), (x0, y_n(x0)), (x1, y_n(x1)), (x1, y_s(x1))] if x1 <= W else None


def _pts(points, tf):
    return " ".join(f"{tf(x, y)[0]:.1f},{tf(x, y)[1]:.1f}" for x, y in points)


def _trees(x0, x1, tf, seed, n, rmin, rmax):
    rnd = random.Random(seed)
    out = []
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
    for x, y, r in placed:
        sx, sy = tf(x, y)
        out.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="{r * tf.s:.1f}" class="p-tree t{int(r * 7) % 3}"/>')
    return out


def make_tf(s, pad_x, pad_y, ymax, x_off=0.0):
    def tf(x, y):
        return ((x - x_off) * s + pad_x, (ymax - y) * s + pad_y)
    tf.s = s
    return tf


def overview_svg(t):
    """Plano completo con las tres etapas. t: diccionario de textos."""
    s = 1.55
    tf = make_tf(s, 46, 30, Y_NE)
    vw, vh = round(W * s + 46 + 40), round(Y_NE * s + 30 + 64)
    o = [f'<svg class="plan" viewBox="0 0 {vw} {vh}" role="img" aria-labelledby="pl-t pl-d">'
         f'<title id="pl-t">{t["plan_title"]}</title><desc id="pl-d">{t["plan_desc"]}</desc>']
    o.append(f'<polygon points="{_pts(POLY, tf)}" class="p-land"/>')
    o += _trees(0, C2, tf, 11, 330, 2.0, 3.6)
    # etapa 3
    for x, w in ROADS:
        o.append(f'<polygon points="{_pts([(x, y_s(x)), (x, y_n(x)), (x + w, y_n(x + w)), (x + w, y_s(x + w))], tf)}" class="p-road"/>')
    for lot in LOTS:
        sx, sy = tf(lot["x"], lot["y"] + lot["h"])
        o.append(f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{lot["w"] * s:.1f}" height="{lot["h"] * s:.1f}" class="p-lot"/>')
    for c in (C1, C2):
        a, b = tf(c, y_s(c)), tf(c, y_n(c))
        o.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="p-cut"/>')
    o.append(f'<polygon points="{_pts(POLY, tf)}" class="p-edge"/>')
    for i, (x0, x1) in enumerate(((0, C1), (C1, C2), (C2, W)), 1):
        cx = (x0 + x1) / 2
        sx, sy = tf(cx, y_n(cx))
        o.append(f'<text x="{sx:.1f}" y="{sy - 9:.1f}" class="p-stage" text-anchor="middle">{t["etapa"]} {i}</text>')
    # calles
    a, b = tf(W * .25, y_s(W * .25)), tf(W * .75, y_s(W * .75))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 24
    angle = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    o.append(f'<text x="{mx:.1f}" y="{my:.1f}" class="p-street" text-anchor="middle" transform="rotate({angle:.2f} {mx:.1f} {my:.1f})">{t["calle"]}</text>')
    ex, ey = tf(W, (Y_SE + Y_NE) / 2)
    o.append(f'<text x="{ex + 22:.1f}" y="{ey:.1f}" class="p-street" text-anchor="middle" transform="rotate(90 {ex + 22:.1f} {ey:.1f})">{t["calle"]}</text>')
    # norte y escala
    o.append(f'<g class="p-north"><path d="M14 52 L22 28 L30 52 L22 46 Z"/><text x="22" y="20" text-anchor="middle">N</text></g>')
    sx0 = 46
    o.append(f'<g class="p-scale"><line x1="{sx0}" y1="{vh - 14}" x2="{sx0 + 50 * s:.1f}" y2="{vh - 14}"/>'
             f'<line x1="{sx0}" y1="{vh - 20}" x2="{sx0}" y2="{vh - 8}"/><line x1="{sx0 + 50 * s:.1f}" y1="{vh - 20}" x2="{sx0 + 50 * s:.1f}" y2="{vh - 8}"/>'
             f'<text x="{sx0 + 25 * s:.1f}" y="{vh - 22}" text-anchor="middle">50 m</text></g>')
    o.append("</svg>")
    return "\n".join(o)


def detail_svg(t):
    """Etapa 3 con lotes interactivos."""
    s = 2.7
    pad_x, pad_y = 14, 16
    x_off = C2
    ymax = y_n(W)
    tf = make_tf(s, pad_x, pad_y, ymax, x_off)
    ymin = y_s(C2)
    vw = round((W - C2) * s + pad_x + 40)
    vh = round((ymax - ymin) * s + pad_y + 30)
    o = [f'<svg class="plan plan-e3" viewBox="0 0 {vw} {vh}" role="group" aria-label="{t["e3_map_label"]}">']
    band = [(C2, y_s(C2)), (C2, y_n(C2)), (W, y_n(W)), (W, y_s(W))]
    o.append(f'<polygon points="{_pts(band, tf)}" class="p-common"/>')
    for x, w in ROADS:
        o.append(f'<polygon points="{_pts([(x, y_s(x)), (x, y_n(x)), (x + w, y_n(x + w)), (x + w, y_s(x + w))], tf)}" class="p-road"/>')
    for lot in LOTS:
        sx, sy = tf(lot["x"], lot["y"] + lot["h"])
        lw, lh = lot["w"] * s, lot["h"] * s
        o.append(f'<g class="lote" data-lote="{lot["n"]}" tabindex="0" role="button" aria-label="{t["lote"]} {lot["n"]}">'
                 f'<rect x="{sx + .6:.1f}" y="{sy + .6:.1f}" width="{lw - 1.2:.1f}" height="{lh - 1.2:.1f}" rx="2"/>'
                 f'<text x="{sx + lw / 2:.1f}" y="{sy + lh / 2 + 4:.1f}" text-anchor="middle">{lot["n"]}</text></g>')
    o.append(f'<polygon points="{_pts(band, tf)}" class="p-edge-soft"/>')
    ex, ey = tf(W, (y_s(W) + y_n(W)) / 2)
    o.append(f'<text x="{ex + 20:.1f}" y="{ey:.1f}" class="p-street" text-anchor="middle" transform="rotate(90 {ex + 20:.1f} {ey:.1f})">{t["calle"]}</text>')
    o.append("</svg>")
    return "\n".join(o)


def summary():
    return {
        "area": AREA,
        "etapas": ETAPA_AREA,
        "lotes": len(LOTS),
        "lotes_m2": LOTS_TOTAL,
        "comun_m2": COMMON_E3,
        "comun_pct": COMMON_E3 / ETAPA_AREA[2],
        "cortes": (C1, C2),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(summary(), indent=1))
    from collections import Counter
    print(Counter(l["col"] for l in LOTS))
