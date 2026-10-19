#!/usr/bin/env python3
"""
diagram_generator.py - Generador de diagramas SVG limpios, sin dependencias.

Tipos (campo "type" del JSON):
  graph | flowchart | automaton | state | pipeline   -> nodos + aristas con auto-layout por capas
  tree                                               -> arbol jerarquico (sintactico, organigrama...)
  sequence                                           -> diagrama de secuencia
  layers                                             -> arquitectura en capas / stack
  timeline                                           -> linea de tiempo

Uso:
  python tools/diagram_generator.py --json spec.json --output img/diagrama.svg [--theme dark] [--png img/diagrama.png]
  python tools/diagram_generator.py --example flowchart > spec.json
  cat spec.json | python tools/diagram_generator.py --stdin --output out.svg
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
from xml.sax.saxutils import escape

sys.setrecursionlimit(10000)

FONT = "Inter, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
LH, SLH, LBL_FS, LBL_LH = 18.0, 15.0, 12, 15.0   # alturas de linea: etiqueta nodo, sub, fuente/linea de arista
WARNINGS = []

# ----------------------------------------------------------------------------- colores
PALETTE = {  # nombre: (relleno, borde, texto)
    "gray":   ("#F1EFE8", "#5F5E5A", "#2C2C2A"),
    "blue":   ("#E6F1FB", "#185FA5", "#0C447C"),
    "green":  ("#E1F5EE", "#0F6E56", "#085041"),
    "amber":  ("#FAEEDA", "#854F0B", "#633806"),
    "red":    ("#FCEBEB", "#A32D2D", "#791F1F"),
    "purple": ("#EEEDFE", "#534AB7", "#3C3489"),
    "coral":  ("#FAECE7", "#993C1D", "#712B13"),
    "pink":   ("#FBEAF0", "#993556", "#72243E"),
}
THEMES = {
    "light": dict(bg="#FFFFFF", edge="#4A4A47", muted="#6B6A66", text="#2C2C2A", halo="#FFFFFF"),
    "dark":  dict(bg="#1B1B1A", edge="#B4B2A9", muted="#9C9A92", text="#EDEBE3", halo="#1B1B1A"),
}


def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[i:i + 2], 16) for i in (0, 2, 4)]


def mix(a, b, t):
    return "#%02x%02x%02x" % tuple(round(x * (1 - t) + y * t) for x, y in zip(_rgb(a), _rgb(b)))


# ----------------------------------------------------------------------------- texto
def char_w(c):
    if c in "iljt.,;:'|!`":
        return 0.30
    if c in " ()[]/\\-":
        return 0.36
    if c in "mwMW@%":
        return 0.88
    if c.isupper():
        return 0.68
    if ord(c) > 0x2E80:
        return 1.0
    return 0.56


def text_w(s, fs, bold=False):
    return sum(char_w(c) for c in str(s)) * fs * (1.06 if bold else 1.0)


def wrap_text(s, fs, maxw, bold=False):
    lines, cur = [], ""
    for w in s.split(" "):
        t = (cur + " " + w) if cur else w
        if text_w(t, fs, bold) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def lines_of(text, fs, maxw=None, bold=False):
    out = []
    for part in str(text).split("\n"):
        out += wrap_text(part, fs, maxw, bold) if maxw else [part]
    return out or [""]


# ----------------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, theme="light", background=True):
        self.theme = theme if theme in THEMES else "light"
        self.t = THEMES[self.theme]
        self.background = background
        self.z = [[], [], []]  # 0 aristas/fondos, 1 nodos, 2 etiquetas
        self.markers = {}
        self.x0 = self.y0 = 1e9
        self.x1 = self.y1 = -1e9

    def bb(self, x0, y0, x1=None, y1=None):
        x1 = x0 if x1 is None else x1
        y1 = y0 if y1 is None else y1
        self.x0, self.y0 = min(self.x0, x0, x1), min(self.y0, y0, y1)
        self.x1, self.y1 = max(self.x1, x0, x1), max(self.y1, y0, y1)

    def add(self, svg, z=1):
        self.z[z].append(svg)

    def colors(self, name):
        """(relleno, borde, texto) para un nombre de paleta o un hex."""
        if name and name.startswith("#"):
            base = name
            fill, stroke, text = (mix(base, "#FFFFFF", 0.88), base, mix(base, "#000000", 0.55))
        else:
            fill, base, text = PALETTE.get(name, PALETTE["gray"])
            stroke = base
        if self.theme == "dark":
            return mix(base, self.t["bg"], 0.82), mix(base, "#FFFFFF", 0.35), mix(base, "#FFFFFF", 0.75)
        return fill, stroke, text

    def line_color(self, name):
        return self.colors(name)[1] if name else self.t["edge"]

    def marker(self, color, start=False):
        key = ("s" if start else "e") + color.lstrip("#")
        self.markers[key] = (color, start)
        return f"url(#m{key})"

    def text(self, x, y, txt, fs=13, w=400, fill=None, anchor="middle", halo=False, z=2, opacity=None):
        tw = text_w(txt, fs, w >= 600)
        ax = {"middle": x - tw / 2, "start": x, "end": x - tw}[anchor]
        self.bb(ax, y - fs * 0.7, ax + tw, y + fs * 0.7)
        extra = ""
        if halo:
            extra = f' paint-order="stroke" stroke="{self.t["halo"]}" stroke-width="4" stroke-linejoin="round"'
        if opacity:
            extra += f' fill-opacity="{opacity}"'
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" dy=".35em" font-size="{fs}" font-weight="{w}" '
                 f'text-anchor="{anchor}" fill="{fill or self.t["text"]}"{extra}>{escape(str(txt))}</text>', z)

    def block(self, x, y, lines, fs, lh, **kw):
        """Bloque de lineas centrado verticalmente en y."""
        top = y - len(lines) * lh / 2
        for i, l in enumerate(lines):
            self.text(x, top + lh * (i + 0.5), l, fs=fs, **kw)

    def path(self, d, pts, stroke, sw=1.6, dash=None, fill="none", mend=None, mstart=None, z=0):
        for p in pts:
            self.bb(p[0], p[1])
        a = f' stroke-dasharray="{dash}"' if dash else ""
        a += f' marker-end="{mend}"' if mend else ""
        a += f' marker-start="{mstart}"' if mstart else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
                 f'stroke-linecap="round" stroke-linejoin="round"{a}/>', z)

    def render(self, title=None, subtitle=None, alt=""):
        if title:
            ty = self.y0 - 26
            self.text(self.x0, ty, title, fs=17, w=600, anchor="start", z=2)
            if subtitle:
                self.text(self.x0, ty + 20, subtitle, fs=12, anchor="start", fill=self.t["muted"], z=2)
                self.bb(self.x0, ty - 8, self.x0, ty + 22)
        pad = 24
        X0, Y0 = self.x0 - pad, self.y0 - pad
        W, H = self.x1 - self.x0 + 2 * pad, self.y1 - self.y0 + 2 * pad
        defs = ""
        for key, (color, start) in self.markers.items():
            if start:
                defs += (f'<marker id="m{key}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" '
                         f'orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="{color}"/></marker>')
            else:
                defs += (f'<marker id="m{key}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                         f'orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>')
        bg = f'<rect x="{X0:.1f}" y="{Y0:.1f}" width="{W:.1f}" height="{H:.1f}" fill="{self.t["bg"]}"/>' if self.background else ""
        body = "".join("".join(z) for z in self.z)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{X0:.1f} {Y0:.1f} {W:.1f} {H:.1f}" '
                f'width="{W:.0f}" height="{H:.0f}" role="img" style="max-width:100%;height:auto" '
                f'font-family="{FONT}"><title>{escape(alt or title or "Diagrama")}</title>'
                f'<defs>{defs}</defs>{bg}{body}</svg>\n')


# ----------------------------------------------------------------------------- nodos y aristas
SHAPE_ALIAS = {"start": "pill", "end": "pill", "terminal": "pill", "decision": "diamond", "process": "rounded",
               "rect": "box", "rectangle": "box", "db": "cylinder", "database": "cylinder", "input": "io",
               "output": "io", "state": "circle", "oval": "ellipse"}
ELLIPTIC = ("circle", "doublecircle", "ellipse")


class Node:
    is_dummy = False

    def __init__(self, d, default_shape="rounded", max_label=210):
        self.id = str(d["id"])
        label = d.get("label", d.get("title", self.id))
        self.lines = lines_of(label, 14, max_label)
        sub = d.get("sub")
        self.sub = lines_of(sub, 11.5, max_label) if sub else []
        shape = d.get("shape") or default_shape
        self.shape = SHAPE_ALIAS.get(shape, shape)
        self.color = d.get("color") or ("blue" if d.get("highlight") else "gray")
        self.initial, self.final = bool(d.get("initial")), bool(d.get("final"))
        if self.final and self.shape == "circle":
            self.shape = "doublecircle"
        self.x, self.y = d.get("x"), d.get("y")
        self.pad_neg = self.pad_pos = 0.0
        self.up, self.down = [], []
        tw = max([text_w(l, 14) * 1.04 for l in self.lines] + [text_w(l, 11.5) for l in self.sub])
        th = len(self.lines) * LH + (len(self.sub) * SLH + 3 if self.sub else 0)
        sh = self.shape
        if sh in ("circle", "doublecircle"):
            dm = max(46, tw + 22, th + 18) + (10 if sh == "doublecircle" else 0)
            self.w = self.h = dm
        elif sh == "ellipse":
            self.w, self.h = max(70, tw * 1.3 + 26), max(40, th + 24)
        elif sh == "diamond":
            self.w, self.h = max(90, tw * 1.65 + 30), max(60, th * 1.9 + 18)
        elif sh == "cylinder":
            self.w, self.h = max(70, tw + 36), max(52, th + 36)
        elif sh == "io":
            self.w, self.h = max(80, tw + 56), max(40, th + 20)
        else:
            self.h = max(40, th + 20)
            self.w = max(72, tw + 34) + (self.h * 0.4 if sh == "pill" else 0)
        self.w, self.h = round(self.w), round(self.h)


class Dummy:
    is_dummy = True
    hm = 0.0
    hc = 6.0
    en = ep = 6.0
    shape = "dummy"

    def __init__(self, layer, key):
        self.layer, self.key = layer, key
        self.up, self.down = [], []


class Edge:
    def __init__(self, d):
        g = lambda *ks: next((d[k] for k in ks if k in d), None)
        self.src, self.dst = str(g("from", "source", "src")), str(g("to", "target", "dst"))
        labels = d.get("labels")
        if labels is None:
            lab = d.get("label")
            labels = str(lab).split("\n") if lab not in (None, "") else []
        self.labels = [str(l) for l in labels]
        self.style, self.color, self.arrow = d.get("style", "solid"), d.get("color"), d.get("arrow", "end")
        t = str(d.get("type", ""))
        self.loop = d.get("loop") or (t[5:] if t.startswith("loop_") else None)
        self.rev = False
        self.lane = 0.0


def boundary(n, tx, ty):
    dx, dy = tx - n.x, ty - n.y
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return n.x, n.y
    hw, hh = n.w / 2, n.h / 2
    if n.shape in ELLIPTIC:
        k = 1 / math.hypot(dx / hw, dy / hh)
    elif n.shape == "diamond":
        k = 1 / (abs(dx) / hw + abs(dy) / hh)
    else:
        k = min(hw / abs(dx) if dx else 1e9, hh / abs(dy) if dy else 1e9)
    return n.x + dx * k, n.y + dy * k


def draw_node(cv, n):
    fill, stroke, tc = cv.colors(n.color)
    x, y, w, h, sh = n.x, n.y, n.w, n.h, n.shape
    st = f'fill="{fill}" stroke="{stroke}" stroke-width="1.6"'
    ty = y
    if sh in ("box", "rounded", "pill"):
        rx = {"box": 3, "rounded": 10, "pill": h / 2}[sh]
        cv.add(f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w}" height="{h}" rx="{rx:.1f}" {st}/>')
    elif sh in ("circle", "ellipse"):
        cv.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w / 2}" ry="{h / 2}" {st}/>')
    elif sh == "doublecircle":
        cv.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w / 2}" ry="{h / 2}" {st}/>')
        cv.add(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{w / 2 - 5}" ry="{h / 2 - 5}" fill="none" stroke="{stroke}" stroke-width="1.6"/>')
    elif sh == "diamond":
        cv.add(f'<polygon points="{x:.1f},{y - h / 2:.1f} {x + w / 2:.1f},{y:.1f} {x:.1f},{y + h / 2:.1f} {x - w / 2:.1f},{y:.1f}" {st} stroke-linejoin="round"/>')
    elif sh == "io":
        k = 14
        cv.add(f'<polygon points="{x - w / 2 + k:.1f},{y - h / 2:.1f} {x + w / 2:.1f},{y - h / 2:.1f} {x + w / 2 - k:.1f},{y + h / 2:.1f} {x - w / 2:.1f},{y + h / 2:.1f}" {st} stroke-linejoin="round"/>')
    elif sh == "cylinder":
        x0, x1, y0, y1, c = x - w / 2, x + w / 2, y - h / 2, y + h / 2, 8
        cv.add(f'<path d="M{x0:.1f},{y0 + c:.1f} A{w / 2},{c} 0 0 1 {x1:.1f},{y0 + c:.1f} L{x1:.1f},{y1 - c:.1f} '
               f'A{w / 2},{c} 0 0 1 {x0:.1f},{y1 - c:.1f} Z" {st}/>')
        cv.add(f'<path d="M{x0:.1f},{y0 + c:.1f} A{w / 2},{c} 0 0 0 {x1:.1f},{y0 + c:.1f}" fill="none" stroke="{stroke}" stroke-width="1.6"/>')
        ty = y + c / 2
    else:
        WARNINGS.append(f"forma desconocida '{sh}' en nodo {n.id}")
    cv.bb(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    th = len(n.lines) * LH + (len(n.sub) * SLH + 3 if n.sub else 0)
    top = ty - th / 2
    for i, l in enumerate(n.lines):
        cv.text(x, top + LH * (i + .5), l, fs=14, w=500, fill=tc, z=1)
    for i, l in enumerate(n.sub):
        cv.text(x, top + len(n.lines) * LH + 3 + SLH * (i + .5), l, fs=11.5, fill=tc, opacity=.78, z=1)


# ----------------------------------------------------------------------------- utilidades geometria
def round_poly(pts, r=10):
    clean = [pts[0]]
    for p in pts[1:]:
        if math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-6:
            clean.append(p)
    pts = clean
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        l1, l2 = math.hypot(p1[0] - p0[0], p1[1] - p0[1]), math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        rr = min(r, l1 / 2, l2 / 2)
        a = (p1[0] + (p0[0] - p1[0]) / l1 * rr, p1[1] + (p0[1] - p1[1]) / l1 * rr)
        b = (p1[0] + (p2[0] - p1[0]) / l2 * rr, p1[1] + (p2[1] - p1[1]) / l2 * rr)
        d += f" L{a[0]:.1f} {a[1]:.1f} Q{p1[0]:.1f} {p1[1]:.1f} {b[0]:.1f} {b[1]:.1f}"
    d += f" L{pts[-1][0]:.1f} {pts[-1][1]:.1f}"
    return d, pts


def pava(vals, weights=None):
    """Regresion isotonica ponderada: secuencia no decreciente mas cercana a vals."""
    weights = weights or [1.0] * len(vals)
    blocks = []
    for v, w in zip(vals, weights):
        blocks.append([v * w, w, 1])
        while len(blocks) > 1 and blocks[-2][0] / blocks[-2][1] > blocks[-1][0] / blocks[-1][1]:
            a, b, c = blocks.pop()
            blocks[-1][0] += a
            blocks[-1][1] += b
            blocks[-1][2] += c
    out = []
    for a, b, c in blocks:
        out += [a / b] * c
    return out


def sgn(v):
    return 1 if v >= 0 else -1


# ----------------------------------------------------------------------------- layout por capas
def layout_layered(nodes, edges, direction, routing, align_leaves=False):
    LR = direction in ("LR", "RL")
    flip = direction in ("RL", "BT")
    N = {n.id: n for n in nodes}
    idx = {n.id: i for i, n in enumerate(nodes)}
    real = [e for e in edges if e.src != e.dst]

    # 1. romper ciclos (aristas "hacia atras" se dibujan invertidas en el layout)
    out = {n.id: [] for n in nodes}
    indeg = {n.id: 0 for n in nodes}
    for e in real:
        out[e.src].append(e)
        indeg[e.dst] += 1
    state = {}

    def dfs(u):
        state[u] = 1
        for e in out[u]:
            if state.get(e.dst) == 1:
                e.rev = True
            elif e.dst not in state:
                dfs(e.dst)
        state[u] = 2

    for s in [n.id for n in nodes if n.initial] + [n.id for n in nodes if indeg[n.id] == 0] + list(N):
        if s not in state:
            dfs(s)

    # 2. capas (camino mas largo)
    preds = {i: [] for i in N}
    succs = {i: [] for i in N}
    for e in real:
        e.a, e.b = (e.dst, e.src) if e.rev else (e.src, e.dst)
        succs[e.a].append(e)
        preds[e.b].append(e)
    deg = {i: len(preds[i]) for i in N}
    topo, queue = [], [i for i in N if deg[i] == 0]
    while queue:
        u = queue.pop(0)
        topo.append(u)
        for e in succs[u]:
            deg[e.b] -= 1
            if deg[e.b] == 0:
                queue.append(e.b)
    layer = {i: 0 for i in N}
    for u in topo:
        for e in succs[u]:
            layer[e.b] = max(layer[e.b], layer[u] + 1)
    for u in reversed(topo):
        if not preds[u] and succs[u]:
            layer[u] = min(layer[e.b] for e in succs[u]) - 1
    top = max(layer.values()) if layer else 0
    if align_leaves:
        for u in N:
            if not succs[u] and preds[u]:
                layer[u] = top
    lo = min(layer.values()) if layer else 0
    for i in N:
        layer[i] -= lo
        N[i].layer = layer[i]
    top = max(layer.values()) if layer else 0

    # 3. nodos ficticios para aristas largas
    for e in real:
        chain = [N[e.a]]
        for l in range(layer[e.a] + 1, layer[e.b]):
            chain.append(Dummy(l, idx[e.a] + 0.5))
        chain.append(N[e.b])
        e.chain = chain
        for p, q in zip(chain, chain[1:]):
            p.down.append(q)
            q.up.append(p)
    L = [[] for _ in range(top + 1)]
    for n in nodes:
        L[n.layer].append(n)
    for e in real:
        for d in e.chain:
            if d.is_dummy:
                L[d.layer].append(d)
    for ln in L:
        ln.sort(key=lambda n: idx[n.id] if not n.is_dummy else n.key)

    # 4. orden dentro de cada capa (baricentro, minimizando cruces)
    def setpos():
        for ln in L:
            for i, n in enumerate(ln):
                n.pos = i

    def crossings():
        tot = 0
        for l in range(len(L) - 1):
            segs = [(n.pos, q.pos) for n in L[l] for q in n.down]
            for i in range(len(segs)):
                for j in range(i + 1, len(segs)):
                    if (segs[i][0] - segs[j][0]) * (segs[i][1] - segs[j][1]) < 0:
                        tot += 1
        return tot

    setpos()
    best, best_c = [list(ln) for ln in L], crossings()
    for it in range(14):
        order = range(1, len(L)) if it % 2 == 0 else range(len(L) - 2, -1, -1)
        for l in order:
            for n in L[l]:
                nb = n.up if it % 2 == 0 else n.down
                n.bary = sum(p.pos for p in nb) / len(nb) if nb else n.pos
            L[l].sort(key=lambda n: (n.bary, n.pos))
            for i, n in enumerate(L[l]):
                n.pos = i
        c = crossings()
        if c < best_c:
            best, best_c = [list(ln) for ln in L], c
    L = best
    setpos()

    # 5. tamanos segun eje principal (m) y transversal (c)
    for n in nodes:
        n.hm, n.hc = (n.w / 2, n.h / 2) if LR else (n.h / 2, n.w / 2)
        n.en, n.ep = n.hc + n.pad_neg, n.hc + n.pad_pos
    base_gap = 74 if LR else 62
    gap = [base_gap] * max(1, top)
    for e in real:
        if not e.labels:
            continue
        a = e.chain[0].layer
        if LR:
            lw = max(text_w(t, LBL_FS) for t in e.labels)
            need = (lw + 16) / 0.82 if routing == "ortho" else lw + 60
        else:
            need = len(e.labels) * LBL_LH + 26
        if a < len(gap):
            gap[a] = max(gap[a], need)
    size = [max([n.hm * 2 for n in ln if not n.is_dummy] or [0]) for ln in L]
    pm = [0.0]
    for l in range(top):
        pm.append(pm[-1] + size[l] / 2 + gap[l] + size[l + 1] / 2)
    for l, ln in enumerate(L):
        for n in ln:
            n.m = pm[l]

    CG = 38 if LR else 44

    def wmean(nb):
        ws = [0.1 if q.is_dummy else 1.0 for q in nb]
        return sum(q.c * w for q, w in zip(nb, ws)) / sum(ws)

    def sep(a, b):
        g = CG if not (a.is_dummy or b.is_dummy) else (14 if a.is_dummy and b.is_dummy else 18)
        return a.ep + b.en + g

    def resolve(ln, des):
        offs = [0.0]
        for i in range(1, len(ln)):
            offs.append(offs[-1] + sep(ln[i - 1], ln[i]))
        ys = pava([d - o for d, o in zip(des, offs)], [0.01 if n.is_dummy else 1.0 for n in ln])
        for n, y, o in zip(ln, ys, offs):
            n.c = y + o

    for ln in L:
        resolve(ln, [0.0] * len(ln))
        mid = (ln[0].c + ln[-1].c) / 2 if ln else 0
        for n in ln:
            n.c -= mid
    for it in range(16):
        order = range(1, len(L)) if it % 2 == 0 else range(len(L) - 2, -1, -1)
        for l in order:
            des = []
            for n in L[l]:
                nb = n.up if it % 2 == 0 else n.down
                des.append(wmean(nb) if nb else n.c)
            resolve(L[l], des)
    for it in range(4):
        for l in range(len(L)):
            des = []
            for n in L[l]:
                nb = n.up + n.down
                des.append(wmean(nb) if nb else n.c)
            resolve(L[l], des)

    if all(len(preds[i]) <= 1 for i in N):  # estructura de arbol: padres centrados sobre hijos
        for l in range(len(L) - 2, -1, -1):
            resolve(L[l], [sum(q.c for q in n.down) / len(n.down) if n.down else n.c for n in L[l]])
    for ln in L:
        for n in ln:
            if flip:
                n.m = -n.m
    return LR, flip, real, N


def place_nodes(nodes, LR):
    for n in nodes:
        n.x, n.y = (n.m, n.c) if LR else (n.c, n.m)


def port_half(n, off):
    if n.is_dummy:
        return 0.0
    hm, hc = n.hm, n.hc
    r = min(abs(off), hc * 0.85) / hc if hc else 0
    if n.shape in ELLIPTIC:
        return hm * math.sqrt(max(0.0, 1 - r * r))
    if n.shape == "diamond":
        return hm * (1 - r)
    return hm


def route_layered(e, LR, routing, labeled_first=True):
    """Devuelve (path d, puntos, posicion etiqueta)."""
    chain = e.chain[::-1] if e.rev else e.chain
    off = e.lane
    mc = [(n.m, n.c + off) for n in chain]
    xy = (lambda m, c: (m, c)) if LR else (lambda m, c: (c, m))
    if routing == "straight":
        pts = [(n.x, n.y) for n in chain]
        first, last = chain[0], chain[-1]
        if not first.is_dummy:
            pts[0] = boundary(first, *pts[1])
        if not last.is_dummy:
            pts[-1] = boundary(last, *pts[-2])
        d = "M" + " L".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts)
        return d, pts, ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
    m0, c0 = mc[0]
    dm = sgn(mc[1][0] - m0)
    mc[0] = (m0 + dm * port_half(chain[0], off), c0)
    ml, cl = mc[-1]
    dm = sgn(mc[-2][0] - ml)
    mc[-1] = (ml + dm * port_half(chain[-1], off), cl)
    pts = [xy(*p) for p in mc]
    if routing == "ortho":
        poly, f = [], 0.82 if (e.labels and labeled_first) else 0.5
        for i in range(len(mc) - 1):
            (ma, ca), (mb, cb) = mc[i], mc[i + 1]
            ff = f if i == 0 else 0.5
            mm = ma + ff * (mb - ma)
            poly += [xy(ma, ca), xy(mm, ca), xy(mm, cb)]
        poly.append(xy(*mc[-1]))
        d, poly = round_poly(poly, 10)
        (ma, ca), (mb, cb) = mc[0], mc[1]
        sd = sgn(cb - ca) if abs(cb - ca) > 1 else (-1 if LR else 1)
        if LR:
            oc = sd * (len(e.labels) * LBL_LH / 2 + 8)
        else:
            oc = sd * (max([text_w(t, LBL_FS) for t in e.labels] + [0]) / 2 + 8)
        lab = xy(ma + f * (mb - ma) / 2, ca + oc)
        return d, poly, lab
    d = "M%.1f %.1f" % xy(*mc[0])
    for (ma, ca), (mb, cb) in zip(mc, mc[1:]):
        h = (mb - ma) / 2
        d += " C%.1f %.1f %.1f %.1f %.1f %.1f" % (xy(ma + h, ca) + xy(mb - h, cb) + xy(mb, cb))
    lab = xy((mc[0][0] + mc[1][0]) / 2, (mc[0][1] + mc[1][1]) / 2)
    return d, pts, lab


# ----------------------------------------------------------------------------- aristas manuales y bucles
def route_manual(e, N, bow):
    a, b = N[e.src], N[e.dst]
    pa, pb = boundary(a, b.x, b.y), boundary(b, a.x, a.y)
    if abs(bow) < 1:
        d = f"M{pa[0]:.1f} {pa[1]:.1f} L{pb[0]:.1f} {pb[1]:.1f}"
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        return d, [pa, pb], (mx, my - (len(e.labels) * LBL_LH / 2 + 6))
    dx, dy = b.x - a.x, b.y - a.y
    ln = math.hypot(dx, dy) or 1
    nx, ny = -dy / ln, dx / ln
    cx, cy = (a.x + b.x) / 2 + nx * bow * 2, (a.y + b.y) / 2 + ny * bow * 2
    pa, pb = boundary(a, cx, cy), boundary(b, cx, cy)
    d = f"M{pa[0]:.1f} {pa[1]:.1f} Q{cx:.1f} {cy:.1f} {pb[0]:.1f} {pb[1]:.1f}"
    mx, my = (pa[0] + 2 * cx + pb[0]) / 4, (pa[1] + 2 * cy + pb[1]) / 4
    return d, [pa, (cx, cy), pb], (mx, my)


def draw_loops(cv, N, loops, default_side):
    groups = {}
    for e in loops:
        groups.setdefault((e.src, e.loop or default_side), []).append(e)
    for (nid, side), es in groups.items():
        n = N[nid]
        labels = [l for e in es for l in e.labels]
        e0 = es[0]
        ah, oh = (n.w / 2, n.h / 2) if side in ("up", "down") else (n.h / 2, n.w / 2)
        a, Lh = ah * 0.42, 34

        def d0(a_):
            if n.shape in ELLIPTIC:
                return oh * math.sqrt(max(0.0, 1 - (a_ / ah) ** 2))
            if n.shape == "diamond":
                return oh * (1 - abs(a_) / ah)
            return oh

        def pt(a_, d_):
            return {"up": (n.x + a_, n.y - d_), "down": (n.x + a_, n.y + d_),
                    "left": (n.x - d_, n.y + a_), "right": (n.x + d_, n.y + a_)}[side]

        p0, p3 = pt(-a, d0(a)), pt(a, d0(a))
        c1, c2 = pt(-a * 1.7, d0(a) + Lh * 1.33), pt(a * 1.7, d0(a) + Lh * 1.33)
        col = cv.line_color(e0.color)
        d = f"M{p0[0]:.1f} {p0[1]:.1f} C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p3[0]:.1f} {p3[1]:.1f}"
        dash = {"dashed": "6 4", "dotted": "2 4"}.get(e0.style)
        cv.path(d, [p0, c1, c2, p3], col, dash=dash, mend=cv.marker(col))
        if labels:
            apex = d0(0) + Lh
            nl = len(labels)
            if side == "up":
                bx, by = pt(0, apex + 6 + nl * LBL_LH / 2)
                cv.block(bx, by, labels, LBL_FS, LBL_LH)
            elif side == "down":
                bx, by = pt(0, apex + 6 + nl * LBL_LH / 2)
                cv.block(bx, by, labels, LBL_FS, LBL_LH)
            else:
                bx, by = pt(0, apex + 6)
                anchor = "start" if side == "right" else "end"
                top = by - nl * LBL_LH / 2
                for i, l in enumerate(labels):
                    cv.text(bx, top + LBL_LH * (i + .5), l, fs=LBL_FS, anchor=anchor)


def loop_pad(n, side, nlabels, LR):
    pad = 34 + nlabels * LBL_LH + 12 if nlabels else 34 + 8
    if LR and side == "up":
        n.pad_neg = max(n.pad_neg, pad)
    elif LR and side == "down":
        n.pad_pos = max(n.pad_pos, pad)
    elif not LR and side == "left":
        n.pad_neg = max(n.pad_neg, pad)
    elif not LR and side == "right":
        n.pad_pos = max(n.pad_pos, pad)


def draw_edge(cv, e, d, pts, lab):
    col = cv.line_color(e.color)
    dash = {"dashed": "6 4", "dotted": "2 4"}.get(e.style)
    mend = cv.marker(col) if e.arrow in ("end", "both") else None
    mst = cv.marker(col, True) if e.arrow == "both" else None
    cv.path(d, pts, col, dash=dash, mend=mend, mstart=mst)
    if e.labels:
        cv.block(lab[0], lab[1], e.labels, LBL_FS, LBL_LH, halo=True)


# ----------------------------------------------------------------------------- grafo (flowchart/automata/pipeline/...)
def normalize_graph(spec, kind):
    if kind == "pipeline":
        stages = spec.get("stages", spec.get("nodes", []))
        nodes, edges = [], []
        for i, s in enumerate(stages):
            s = dict(s)
            s.setdefault("id", f"s{i}")
            nodes.append(s)
            if i:
                edges.append({"from": nodes[i - 1]["id"], "to": s["id"],
                              "label": stages[i - 1].get("output_label", stages[i - 1].get("edge_label", ""))})
        edges += spec.get("edges", [])
        return nodes, edges
    nodes = spec.get("nodes", spec.get("states", []))
    edges = spec.get("edges", spec.get("transitions", []))
    return nodes, edges


def render_graph(spec, kind, cv):
    node_defs, edge_defs = normalize_graph(spec, kind)
    default_shape = spec.get("default_shape") or {"automaton": "circle", "state": "rounded"}.get(kind, "rounded")
    nodes = [Node(d, default_shape, spec.get("max_label_width", 210)) for d in node_defs]
    if not nodes:
        raise SystemExit("El diagrama no tiene nodos")
    N = {n.id: n for n in nodes}
    edges = [Edge(d) for d in edge_defs]
    for e in edges:
        for k in (e.src, e.dst):
            if k not in N:
                raise SystemExit(f"Arista referencia un nodo inexistente: '{k}' (nodos: {', '.join(N)})")
    manual = all(n.x is not None and n.y is not None for n in nodes)
    direction = spec.get("direction", "LR" if kind in ("automaton", "pipeline") else "TB")
    if kind == "flowchart" and "direction" not in spec:
        direction = "TB"
    routing = spec.get("routing") or ("ortho" if kind == "flowchart" else "curve")
    LR = direction in ("LR", "RL")
    loops = [e for e in edges if e.src == e.dst]
    default_side = spec.get("loop_side") or ("up" if (LR or manual) else "right")
    for e in loops:
        loop_pad(N[e.src], e.loop or default_side, len(e.labels), LR)

    # lanes para aristas paralelas / bidireccionales
    pairs = {}
    for e in edges:
        if e.src != e.dst:
            pairs.setdefault(frozenset((e.src, e.dst)), []).append(e)
    for es in pairs.values():
        gap = 18 if any(x.labels for x in es) else 12
        for j, e in enumerate(es):
            e.lane = (j - (len(es) - 1) / 2) * gap if len(es) > 1 else 0.0

    flow = (1, 0)
    if manual:
        for n in nodes:
            n.x, n.y = float(n.x), float(n.y)
        routes = []
        for es in pairs.values():
            for j, e in enumerate(es):
                bow = 0
                if len(es) > 1:
                    bow = 18 * (j - (len(es) - 1) / 2) * 2
                    if all(x.src == e.src for x in es) is False and len(es) == 2:
                        bow = 18 if e.src < e.dst else -18
                routes.append((e,) + route_manual(e, N, bow))
        # solapes
        for i, a in enumerate(nodes):
            for b in nodes[i + 1:]:
                if abs(a.x - b.x) < (a.w + b.w) / 2 and abs(a.y - b.y) < (a.h + b.h) / 2:
                    WARNINGS.append(f"nodos solapados: {a.id} y {b.id}")
    else:
        LR, flip, real, _ = layout_layered(nodes, edges, direction, routing, bool(spec.get("align_leaves")))
        # nodos ficticios necesitan x,y para boundary; los reales se colocan aqui
        place_nodes(nodes, LR)
        for e in real:
            for dmy in e.chain:
                if dmy.is_dummy:
                    dmy.x, dmy.y = (dmy.m, dmy.c) if LR else (dmy.c, dmy.m)
        routes = []
        for e in real:
            routes.append((e,) + route_layered(e, LR, routing))
        flow = ((-1 if flip else 1), 0) if LR else (0, (-1 if flip else 1))

    for e, d, pts, lab in routes:
        draw_edge(cv, e, d, pts, lab)
    draw_loops(cv, N, loops, default_side)
    for n in nodes:
        draw_node(cv, n)
    for n in nodes:  # flecha de estado inicial
        if n.initial:
            fx, fy = flow
            hw = port_half_xy(n, fx, fy)
            ex, ey = n.x - fx * hw, n.y - fy * hw
            sx, sy = ex - fx * 40, ey - fy * 40
            col = cv.line_color(None)
            cv.path(f"M{sx:.1f} {sy:.1f} L{ex:.1f} {ey:.1f}", [(sx, sy), (ex, ey)], col, mend=cv.marker(col))


def port_half_xy(n, fx, fy):
    return n.w / 2 if fx else n.h / 2


# ----------------------------------------------------------------------------- arbol
def render_tree(spec, cv):
    nodes, edges = [], []
    leaf_color = spec.get("leaf_color")

    def walk(t, parent=None):
        d = dict(t) if isinstance(t, dict) else {"label": str(t)}
        children = d.pop("children", [])
        d["id"] = f"t{len(nodes)}"
        if not children and leaf_color and "color" not in d:
            d["color"] = leaf_color
        if not children and spec.get("leaf_shape") and "shape" not in d:
            d["shape"] = spec["leaf_shape"]
        nodes.append(d)
        if parent:
            edges.append({"from": parent, "to": d["id"], "arrow": "none"})
        for c in children:
            walk(c, d["id"])

    walk(spec["root"])
    sub = dict(spec)
    sub.update({"nodes": nodes, "edges": edges, "direction": spec.get("direction", "TB"),
                "routing": spec.get("routing", "straight"), "default_shape": spec.get("default_shape", "rounded")})
    render_graph(sub, "tree", cv)


# ----------------------------------------------------------------------------- secuencia
def render_sequence(spec, cv):
    parts = []
    for p in spec["participants"]:
        p = {"id": p, "label": p} if isinstance(p, str) else dict(p)
        parts.append(Node(p, spec.get("participant_shape", "rounded")))
    idx = {p.id: i for i, p in enumerate(parts)}
    n = len(parts)
    gaps = [max(parts[i].w / 2 + parts[i + 1].w / 2 + 36, 130) for i in range(n - 1)]
    items = spec["messages"]
    for m in items:
        if "from" not in m:
            continue
        i, j = sorted((idx[str(m["from"])], idx[str(m["to"])]))
        lw = text_w(m.get("label", ""), LBL_FS) + 50
        if i == j:
            if i + 1 < n:
                i, j = i, i + 1
                lw += 20
            else:
                continue
        spans = (i, j, lw)
        cur = sum(gaps[i:j])
        if cur < lw:
            for k in range(i, j):
                gaps[k] += (lw - cur) / (j - i)
    xs = [0.0]
    for g in gaps:
        xs.append(xs[-1] + g)
    hh = max(p.h for p in parts)
    for p, x in zip(parts, xs):
        p.x, p.y = x, hh / 2
    y = hh + 38
    draws, num = [], 0
    for m in items:
        if "note" in m:
            over = m.get("over", parts[0].id)
            over = [over] if isinstance(over, (str, int)) else over
            xa, xb = xs[idx[str(over[0])]], xs[idx[str(over[-1])]]
            lines = lines_of(m["note"], 12, 220)
            w = max(text_w(l, 12) for l in lines) + 24
            w = max(w, xb - xa + 40)
            h = len(lines) * LBL_LH + 14
            draws.append(("note", (xa + xb) / 2, y + 4, w, h, lines))
            y += h + 22
            continue
        fi, ti = xs[idx[str(m["from"])]], xs[idx[str(m["to"])]]
        lab = m.get("label", "")
        if spec.get("numbered"):
            num += 1
            lab = f"{num}. {lab}"
        kind = m.get("type", "self" if fi == ti else "call")
        lines = lines_of(lab, LBL_FS)
        draws.append((kind, fi, ti, y, lines))
        y += 46 + (len(lines) - 1) * LBL_LH + (22 if kind == "self" else 0)
    yend = y + 6
    col = cv.t["edge"]
    for p, x in zip(parts, xs):
        cv.path(f"M{x:.1f} {hh:.1f} L{x:.1f} {yend:.1f}", [(x, hh), (x, yend)], mix(col, cv.t["bg"], .45), sw=1.2, dash="5 5")
    for dr in draws:
        if dr[0] == "note":
            _, cx, cy, w, h, lines = dr
            fill, stroke, tc = cv.colors("amber")
            cv.add(f'<rect x="{cx - w / 2:.1f}" y="{cy:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>')
            cv.bb(cx - w / 2, cy, cx + w / 2, cy + h)
            cv.block(cx, cy + h / 2, lines, 12, LBL_LH, fill=tc)
            continue
        kind, fi, ti, yy, lines = dr
        dash = "6 4" if kind == "return" else None
        if kind == "self":
            d = f"M{fi:.1f} {yy:.1f} h34 v22 h-34"
            cv.path(d, [(fi, yy), (fi + 34, yy + 22)], col, dash=dash, mend=cv.marker(col), z=1)
            for k, l in enumerate(lines):
                cv.text(fi + 42, yy + 11 + (k - (len(lines) - 1) / 2) * LBL_LH, l, fs=LBL_FS, anchor="start")
        else:
            s = sgn(ti - fi)
            cv.path(f"M{fi + s * 2:.1f} {yy:.1f} L{ti - s * 1:.1f} {yy:.1f}", [(fi, yy), (ti, yy)], col, dash=dash,
                    mend=cv.marker(col), z=1)
            for k, l in enumerate(lines):
                cv.text((fi + ti) / 2, yy - 10 - (len(lines) - 1 - k) * LBL_LH, l, fs=LBL_FS)
    for p in parts:
        draw_node(cv, p)


# ----------------------------------------------------------------------------- capas
def render_layers(spec, cv):
    layers = spec["layers"]
    maxw = spec.get("max_width", 700)
    chip_gap, pad = 12, 16
    rows_data = []
    for ly in layers:
        chips = []
        for it in ly.get("items", []):
            it = {"label": it} if isinstance(it, str) else dict(it)
            it["id"] = it["label"]
            it.setdefault("color", ly.get("color", "gray"))
            chips.append(Node(it, "rounded", 180))
        rows_data.append(chips)
    title_w = max([text_w(ly.get("title", ""), 14, True) for ly in layers] + [0])
    title_w = title_w + 28 if title_w else 0
    natural = [sum(c.w for c in ch) + chip_gap * max(0, len(ch) - 1) for ch in rows_data]
    area = min(max(natural + [0]), maxw)
    area = max(area, max([c.w for ch in rows_data for c in ch] + [0]))
    W = title_w + area + 2 * pad
    y, ids = 0.0, []
    for i, (ly, chips) in enumerate(zip(layers, rows_data)):
        rows, cur, cw = [], [], 0
        for c in chips:
            if cur and cw + chip_gap + c.w > area:
                rows.append(cur)
                cur, cw = [], 0
            cw += (chip_gap if cur else 0) + c.w
            cur.append(c)
        if cur:
            rows.append(cur)
        rh = max([c.h for c in chips] + [40])
        H = len(rows) * rh + (len(rows) - 1) * chip_gap + 2 * pad if rows else 2 * pad + 20
        fill, stroke, tc = cv.colors(ly.get("color", "gray"))
        cv.add(f'<rect x="0" y="{y:.1f}" width="{W:.1f}" height="{H:.1f}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>', 0)
        cv.bb(0, y, W, y + H)
        if ly.get("title"):
            cv.text(pad, y + H / 2, ly["title"], fs=14, w=600, fill=tc, anchor="start")
        ry = y + pad
        for row in rows:
            rw = sum(c.w for c in row) + chip_gap * (len(row) - 1)
            x = title_w + pad + (area - rw) / 2 if spec.get("center_items", True) else title_w + pad
            for c in row:
                c.x, c.y = x + c.w / 2, ry + rh / 2
                c.color = ly.get("color", c.color)
                draw_node_chip(cv, c)
                x += c.w + chip_gap
            ry += rh + chip_gap
        y += H
        if i < len(layers) - 1:
            gap = 30
            if spec.get("arrows", True):
                col = cv.t["edge"]
                cv.path(f"M{W / 2:.1f} {y + 4:.1f} L{W / 2:.1f} {y + gap - 4:.1f}", [(W / 2, y), (W / 2, y + gap)], col,
                        mend=cv.marker(col), mstart=cv.marker(col, True) if spec.get("bidirectional") else None)
            y += gap


def draw_node_chip(cv, c):
    fill, stroke, tc = cv.colors(c.color)
    c.shape = "rounded"
    x, y = c.x, c.y
    cv.add(f'<rect x="{x - c.w / 2:.1f}" y="{y - c.h / 2:.1f}" width="{c.w}" height="{c.h}" rx="8" fill="{cv.t["bg"]}" stroke="{stroke}" stroke-width="1.3"/>')
    th = len(c.lines) * LH + (len(c.sub) * SLH + 3 if c.sub else 0)
    top = y - th / 2
    for i, l in enumerate(c.lines):
        cv.text(x, top + LH * (i + .5), l, fs=14, w=500, fill=cv.t["text"], z=1)
    for i, l in enumerate(c.sub):
        cv.text(x, top + len(c.lines) * LH + 3 + SLH * (i + .5), l, fs=11.5, fill=cv.t["muted"], z=1)


# ----------------------------------------------------------------------------- linea de tiempo
def render_timeline(spec, cv):
    ev = spec["events"]
    cw = spec.get("card_width", 176)
    cards = []
    for e in ev:
        title = lines_of(e.get("title", ""), 13, cw - 20, True)
        desc = lines_of(e["desc"], 11.5, cw - 20) if e.get("desc") else []
        date = str(e.get("date", ""))
        h = 20 + (16 if date else 0) + len(title) * 17 + len(desc) * 15 + (4 if desc else 0)
        cards.append((date, title, desc, h))
    step, stem = cw / 2 + 28, 30
    palette = ["blue", "green", "amber", "purple", "coral", "pink"]
    last = step * (len(ev) - 1)
    col = cv.t["edge"]
    cv.path(f"M{-34:.1f} 0 L{last + 40:.1f} 0", [(-34, 0), (last + 40, 0)], col, sw=2, mend=cv.marker(col), z=0)
    for i, (e, (date, title, desc, h)) in enumerate(zip(ev, cards)):
        x = i * step
        fill, stroke, tc = cv.colors(e.get("color", palette[i % len(palette)] if spec.get("colorful") else "blue"))
        up = i % 2 == 0
        y0 = -(stem + h) if up else stem
        cv.path(f"M{x:.1f} {0:.1f} L{x:.1f} {(-stem if up else stem):.1f}", [(x, 0), (x, -stem if up else stem)], stroke, sw=1.3, z=0)
        cv.add(f'<circle cx="{x:.1f}" cy="0" r="6.5" fill="{stroke}" stroke="{cv.t["bg"]}" stroke-width="2"/>')
        cv.add(f'<rect x="{x - cw / 2:.1f}" y="{y0:.1f}" width="{cw}" height="{h}" rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>', 0)
        cv.bb(x - cw / 2, y0, x + cw / 2, y0 + h)
        ty = y0 + 12
        if date:
            cv.text(x, ty + 5, date, fs=11, w=600, fill=stroke)
            ty += 16
        for l in title:
            cv.text(x, ty + 8, l, fs=13, w=600, fill=tc)
            ty += 17
        if desc:
            ty += 4
            for l in desc:
                cv.text(x, ty + 7, l, fs=11.5, fill=tc, opacity=.8)
                ty += 15


# ----------------------------------------------------------------------------- ejemplos
EXAMPLES = {
    "automaton": {
        "type": "automaton", "title": "AFD: cadenas con 'ab' al final", "direction": "LR",
        "states": [{"id": "q0", "label": "q₀", "initial": True}, {"id": "q1", "label": "q₁"},
                   {"id": "q2", "label": "q₂", "final": True}],
        "transitions": [
            {"from": "q0", "to": "q0", "labels": ["b"]}, {"from": "q0", "to": "q1", "label": "a"},
            {"from": "q1", "to": "q1", "label": "a"}, {"from": "q1", "to": "q2", "label": "b"},
            {"from": "q2", "to": "q0", "label": "b"}, {"from": "q2", "to": "q1", "label": "a"}]},
    "automaton-manual": {
        "type": "automaton",
        "states": [{"id": "q0", "label": "q₀", "x": 75, "y": 95, "initial": True}, {"id": "q1", "label": "q₁", "x": 225, "y": 95},
                   {"id": "q2", "label": "q₂", "x": 395, "y": 95}, {"id": "q3", "label": "q₃", "x": 565, "y": 95, "final": True}],
        "transitions": [{"from": "q0", "to": "q1", "label": "ε, ε / Z₀"},
                        {"from": "q1", "to": "q1", "type": "loop_up", "labels": ["a, Z₀ / AZ₀", "a, A / AA"]},
                        {"from": "q1", "to": "q2", "label": "b, A / ε"},
                        {"from": "q2", "to": "q2", "type": "loop_down", "labels": ["b, A / ε"]},
                        {"from": "q2", "to": "q3", "label": "ε, Z₀ / ε"}]},
    "flowchart": {
        "type": "flowchart", "title": "Proceso de login", "direction": "TB",
        "nodes": [{"id": "s", "label": "Inicio", "shape": "start", "color": "green"},
                  {"id": "i", "label": "Ingresar credenciales", "shape": "io"},
                  {"id": "v", "label": "¿Válidas?", "shape": "decision", "color": "amber"},
                  {"id": "ok", "label": "Crear sesión", "color": "blue"},
                  {"id": "err", "label": "Mostrar error", "color": "red"},
                  {"id": "db", "label": "Usuarios", "shape": "db"},
                  {"id": "e", "label": "Fin", "shape": "end", "color": "green"}],
        "edges": [{"from": "s", "to": "i"}, {"from": "i", "to": "v"}, {"from": "db", "to": "v", "style": "dashed"},
                  {"from": "v", "to": "ok", "label": "Sí"}, {"from": "v", "to": "err", "label": "No"},
                  {"from": "err", "to": "i", "label": "Reintentar"}, {"from": "ok", "to": "e"}]},
    "tree": {
        "type": "tree", "title": "Árbol sintáctico: 3 + 4 * 5", "leaf_color": "green",
        "root": {"label": "E", "children": [{"label": "E", "children": [{"label": "3"}]}, {"label": "+"},
                                             {"label": "T", "children": [{"label": "T", "children": [{"label": "4"}]},
                                                                          {"label": "*"}, {"label": "5"}]}]}},
    "pipeline": {
        "type": "pipeline",
        "stages": [{"title": "Fuente", "sub": "Código"}, {"title": "Léxico", "sub": "Scanner", "output_label": "Tokens"},
                   {"title": "Sintáctico", "sub": "Parser", "highlight": True, "output_label": "AST"},
                   {"title": "Semántico", "sub": "Tipos"}]},
    "sequence": {
        "type": "sequence", "title": "Petición HTTP", "numbered": True,
        "participants": ["Cliente", "API", {"id": "db", "label": "Base de datos", "shape": "cylinder"}],
        "messages": [{"from": "Cliente", "to": "API", "label": "GET /usuarios"},
                     {"from": "API", "to": "db", "label": "SELECT *"},
                     {"note": "Cachea el resultado 60 s", "over": "API"},
                     {"from": "db", "to": "API", "label": "filas", "type": "return"},
                     {"from": "API", "to": "API", "label": "serializar"},
                     {"from": "API", "to": "Cliente", "label": "200 JSON", "type": "return"}]},
    "layers": {
        "type": "layers", "title": "Arquitectura web",
        "layers": [{"title": "Presentación", "color": "blue", "items": ["Web", "Móvil", "CLI"]},
                   {"title": "Lógica", "color": "green", "items": ["Auth", "Pedidos", "Pagos", "Notificaciones"]},
                   {"title": "Datos", "color": "amber", "items": ["PostgreSQL", "Redis", "S3"]}]},
    "timeline": {
        "type": "timeline", "title": "Hitos del proyecto",
        "events": [{"date": "Ene", "title": "Kick-off", "desc": "Alcance y equipo definidos"},
                   {"date": "Mar", "title": "Prototipo", "desc": "Primera demo interna"},
                   {"date": "Jun", "title": "Beta", "desc": "50 usuarios de prueba"},
                   {"date": "Sep", "title": "Lanzamiento"}]},
}


# ----------------------------------------------------------------------------- main
def build(spec, theme=None):
    kind = spec.get("type", "graph")
    cv = Canvas(theme or spec.get("theme", "light"), spec.get("background", "white") != "none")
    if kind in ("graph", "flowchart", "automaton", "state", "pipeline", "dependency", "network"):
        render_graph(spec, kind, cv)
    elif kind == "tree":
        render_tree(spec, cv)
    elif kind == "sequence":
        render_sequence(spec, cv)
    elif kind == "layers":
        render_layers(spec, cv)
    elif kind == "timeline":
        render_timeline(spec, cv)
    else:
        raise SystemExit(f"Tipo desconocido '{kind}'. Validos: graph, flowchart, automaton, state, pipeline, tree, sequence, layers, timeline")
    return cv.render(spec.get("title"), spec.get("subtitle"), spec.get("alt", ""))


def to_png(svg_path, png_path):
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=2)
        return True
    except Exception:
        pass
    for cmd in (["rsvg-convert", "-z", "2", "-o", png_path, svg_path],
                ["inkscape", svg_path, "-o", png_path, "-d", "192"],
                ["convert", "-density", "192", "-background", "none", svg_path, png_path]):
        if shutil.which(cmd[0]):
            if subprocess.run(cmd, capture_output=True).returncode == 0:
                return True
    return False


def main():
    ap = argparse.ArgumentParser(description="Generador de diagramas SVG")
    ap.add_argument("--json", help="archivo de especificacion JSON")
    ap.add_argument("--stdin", action="store_true", help="leer la especificacion de stdin")
    ap.add_argument("--output", "-o", help="SVG de salida")
    ap.add_argument("--theme", choices=["light", "dark"])
    ap.add_argument("--png", help="ademas exportar PNG (requiere cairosvg, rsvg-convert, inkscape o ImageMagick)")
    ap.add_argument("--example", choices=sorted(EXAMPLES), help="imprime una especificacion de ejemplo y sale")
    a = ap.parse_args()
    if a.example:
        print(json.dumps(EXAMPLES[a.example], ensure_ascii=False, indent=2))
        return
    if a.stdin:
        spec = json.load(sys.stdin)
    elif a.json:
        with open(a.json, encoding="utf-8") as f:
            spec = json.load(f)
    else:
        ap.error("indica --json, --stdin o --example")
    if not a.output:
        ap.error("falta --output")
    svg = build(spec, a.theme)
    os.makedirs(os.path.dirname(os.path.abspath(a.output)), exist_ok=True)
    with open(a.output, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"OK: {a.output}")
    if a.png:
        print(f"PNG: {a.png}" if to_png(a.output, a.png) else "AVISO: no hay conversor PNG disponible", file=sys.stderr)
    for w in WARNINGS:
        print("AVISO:", w, file=sys.stderr)


if __name__ == "__main__":
    main()