"""Minimal SVG outline reader for the Vesprio brand files (no FreeCAD needed).

Handles what those files use: nested <g transform="translate() scale()">,
<path d> with M/L/H/V/Q/C/Z (absolute or relative), and <rect> (filled, or
stroked: a stroked rect becomes an outer and an inner outline, i.e. a frame).
Returns closed contours in SVG units with y pointing DOWN, as lists of
segments: ('L', p0, p1), ('Q', p0, c, p1) or ('C', p0, c1, c2, p1).
"""
import re
import xml.etree.ElementTree as ET


def _transform(attr):
    a, d, e, f = 1.0, 1.0, 0.0, 0.0                 # x' = a*x + e, y' = d*y + f
    for name, args in re.findall(r'(\w+)\s*\(([^)]*)\)', attr or ''):
        v = [float(x) for x in re.split(r'[\s,]+', args.strip()) if x]
        if name == 'translate':
            tx, ty = v[0], (v[1] if len(v) > 1 else 0.0)
            m = (1.0, 1.0, tx, ty)
        elif name == 'scale':
            sx, sy = v[0], (v[1] if len(v) > 1 else v[0])
            m = (sx, sy, 0.0, 0.0)
        else:
            raise ValueError('unsupported transform ' + name)
        # compose: current o m
        a, d, e, f = a * m[0], d * m[1], a * m[2] + e, d * m[3] + f
    return a, d, e, f


def _compose(outer, inner):
    a, d, e, f = outer
    return (a * inner[0], d * inner[1], a * inner[2] + e, d * inner[3] + f)


def _apply(t, p):
    return (t[0] * p[0] + t[2], t[1] * p[1] + t[3])


def _path(d, t):
    toks = re.findall(r'[MmLlHhVvQqCcZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', d)
    i, cmd = 0, 'M'                                 # a path always starts with M
    cur = start = (0.0, 0.0)
    contours, segs = [], []

    def num():
        nonlocal i
        i += 1
        return float(toks[i - 1])

    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]; i += 1
            if cmd in 'Zz':
                if cur != start:
                    segs.append(('L', cur, start))
                if segs:
                    contours.append(segs)
                segs, cur = [], start
                continue
        rel = cmd.islower()
        ox, oy = cur if rel else (0.0, 0.0)
        c = cmd.upper()
        if c == 'M':
            if segs:
                contours.append(segs); segs = []
            cur = start = (num() + ox, num() + oy)
            cmd = 'l' if rel else 'L'                 # implicit lineto after moveto
        elif c == 'L':
            p = (num() + ox, num() + oy); segs.append(('L', cur, p)); cur = p
        elif c == 'H':
            p = (num() + ox, cur[1]); segs.append(('L', cur, p)); cur = p
        elif c == 'V':
            p = (cur[0], num() + oy); segs.append(('L', cur, p)); cur = p
        elif c == 'Q':
            q = (num() + ox, num() + oy); p = (num() + ox, num() + oy)
            segs.append(('Q', cur, q, p)); cur = p
        elif c == 'C':
            c1 = (num() + ox, num() + oy); c2 = (num() + ox, num() + oy); p = (num() + ox, num() + oy)
            segs.append(('C', cur, c1, c2, p)); cur = p
        else:
            raise ValueError('unsupported path command ' + cmd)
    if segs:
        contours.append(segs)
    out = []
    for cnt in contours:
        cnt = [s for s in cnt if not (s[0] == 'L' and s[1] == s[2])]   # drop zero-length
        out.append([(s[0],) + tuple(_apply(t, p) for p in s[1:]) for s in cnt])
    return out


def _rect(el, t):
    x, y = float(el.get('x', 0)), float(el.get('y', 0))
    w, h = float(el.get('width')), float(el.get('height'))
    sw = float(el.get('stroke-width', 0)) if el.get('stroke') not in (None, 'none') else 0.0
    filled = el.get('fill') not in ('none',)

    def box(x0, y0, x1, y1):
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        return [('L', _apply(t, pts[k]), _apply(t, pts[(k + 1) % 4])) for k in range(4)]
    out = []
    if sw:
        out.append(box(x - sw / 2, y - sw / 2, x + w + sw / 2, y + h + sw / 2))
        if not filled:
            out.append(box(x + sw / 2, y + sw / 2, x + w - sw / 2, y + h - sw / 2))
    elif filled:
        out.append(box(x, y, x + w, y + h))
    return out


def contours(path):
    """All closed contours in the file, in SVG units (y down)."""
    root = ET.parse(path).getroot()
    out = []

    def walk(el, t):
        t = _compose(t, _transform(el.get('transform')))
        tag = el.tag.split('}')[-1]
        if tag == 'path':
            out.extend(_path(el.get('d'), t))
        elif tag == 'rect':
            out.extend(_rect(el, t))
        for ch in el:
            walk(ch, t)
    walk(root, (1.0, 1.0, 0.0, 0.0))
    return out


def bbox(cs):
    xs = [p[0] for c in cs for s in c for p in s[1:]]
    ys = [p[1] for c in cs for s in c for p in s[1:]]
    return min(xs), min(ys), max(xs), max(ys)
