"""Marking geometry for the case: monoline lettering, SVG artwork and the
LED / USB icons, all as flat faces at z = 0, plus printability(), which tests
a marking against what the printer resolves. Needs FreeCAD (Part); mm.
"""
import Part
from FreeCAD import Vector as V

import svgpaths


def faces_of(shape):
    return Part.makeCompound(shape.Faces)


def svg_faces(path, width):
    """SVG outlines as faces `width` wide, centred on the origin, y up."""
    cs = svgpaths.contours(path)
    x0, y0, x1, y1 = svgpaths.bbox(cs)
    k = width / (x1 - x0)
    P = lambda p: V((p[0] - (x0 + x1) / 2) * k, -(p[1] - (y0 + y1) / 2) * k, 0)
    wires = []
    for cnt in cs:
        edges = []
        for sg in cnt:
            pts = [P(p) for p in sg[1:]]
            if sg[0] == 'L':
                edges.append(Part.LineSegment(pts[0], pts[1]).toShape())
            else:
                bz = Part.BezierCurve(); bz.setPoles(pts); edges.append(bz.toShape())
        wires.append(Part.Wire(edges))
    return Part.makeFace(wires, 'Part::FaceMakerBullseye')


def poly(pts):
    return Part.Face(Part.makePolygon([V(x, y, 0) for x, y in pts] + [V(*pts[0], 0)]))


def stroke(pts, w):
    """An open polyline thickened to width w, as a face."""
    wire = Part.makePolygon([V(x, y, 0) for x, y in pts])
    return Part.Face(wire.makeOffset2D(w / 2, 0, False, False, False))


def disc(x, y, r):
    return Part.Face(Part.Wire(Part.makeCircle(r, V(x, y, 0))))


def union(*faces):
    """Fuse faces into disjoint faces. A 2D fuse keeps the pieces as faces
    sharing edges, which extrude to touching solids (a non-manifold STL), so
    fuse them as slabs and keep the merged bottom faces."""
    slabs = [s for f in faces for s in Part.makeCompound(f.Faces).extrude(V(0, 0, 1)).Solids]
    u = (slabs[0].multiFuse(slabs[1:]) if len(slabs) > 1 else slabs[0]).removeSplitter()
    return Part.makeCompound([f for f in u.Faces
                              if f.BoundBox.ZMax < 1e-6 and f.BoundBox.ZMin > -1e-6])


def icon_power():          # D4: logic power (IEC 5009 standby symbol)
    ring = disc(0, -0.2, 2.0).cut(disc(0, -0.2, 1.35))
    ring = ring.cut(poly([(-0.9, 0.2), (0.9, 0.2), (0.9, 3), (-0.9, 3)]))
    return union(ring, poly([(-0.33, -0.4), (0.33, -0.4), (0.33, 2.2), (-0.33, 2.2)]))


def icon_bolt():           # D5: 12 V motor power
    # Flat-cut tips about 1 mm wide at 1.4x: the old pointed tips were under
    # the printable stroke for their last 1.8 mm and printed as a blurry plus.
    k = 1 / 1.4
    return union(poly([(x * k, y * k) for x, y in
                       ((0.5, 3.2), (1.5, 3.2), (0.5, 0.6), (1.7, 0.6),
                        (-0.5, -3.2), (-1.5, -3.2), (-0.5, -0.6), (-1.7, -0.6))]))


def icon_status():         # D3: status / fault (warning triangle, "!" cut out)
    t = poly([(-2.6, -2.1), (2.6, -2.1), (0, 2.4)])
    t = t.cut(poly([(-0.32, -0.6), (0.32, -0.6), (0.32, 1.1), (-0.32, 1.1)]))
    t = t.cut(poly([(-0.32, -1.6), (0.32, -1.6), (0.32, -1.0), (-0.32, -1.0)]))
    return faces_of(t)


def icon_usb():            # J2: USB trident, pointing out of the case (-X)
    f = union(disc(2.9, 0, 0.75),
              poly([(2.9, -0.3), (-2.4, -0.3), (-2.4, 0.3), (2.9, 0.3)]),
              poly([(-2.2, -0.85), (-2.2, 0.85), (-3.6, 0)]),
              stroke([(1.2, 0), (0.1, 1.35), (-1.0, 1.35)], 0.6), disc(-1.25, 1.35, 0.55),
              stroke([(0.6, 0), (-0.4, -1.3), (-1.4, -1.3)], 0.6),
              poly([(-1.4, -1.8), (-2.4, -1.8), (-2.4, -0.8), (-1.4, -0.8)]))
    return f


def rounded_rect(w, h, r):
    """A w x h rectangle with corner radius r, centred on the origin, as faces."""
    box = Part.makePlane(w - 2 * r, h - 2 * r, V(-w / 2 + r, -h / 2 + r, 0))
    return Part.makeCompound([Part.Face(box.makeOffset2D(r, 0).OuterWire)])


# What the printer resolves on the bed face (tile v2, 2026-10-15, black PETG,
# 0.4 nozzle, elephant foot compensation 0, Arachne): a 0.6 mm line prints
# clean, and a 0.5 mm gap stays open. 0.5 lines and 0.4 gaps did not.
MIN_STROKE, MIN_GAP = 0.6, 0.5


def groups_of(shape):
    """The letters / parts of a mark: its sub-compounds if it has them (as
    mono_text() builds), else each solid or face on its own."""
    kids = shape.childShapes()
    if kids and all(k.ShapeType == 'Compound' for k in kids):
        return kids
    return shape.Solids or shape.Faces


def printability(shape, stroke=MIN_STROKE, gap=MIN_GAP, tol=0.35, res=0.02, letters=True):
    """Rasterise a mark's top faces and test them like a pen of the nozzle's
    reach. Thin: parts a `stroke`-wide pen can't draw. Narrow: background a
    `gap`-wide pen can't fit into. Sharp corners always fail both a little
    (they print rounded), so only what reaches deeper than `tol` counts.
    A gap that closes inside one letter or part (the crotch of an N or W, a
    corner) is the glyph's design, checked once when it was drawn; only gaps
    between letters, rows and parts count here (letters=False counts all).
    Returns (thin, narrow): lists of failures, worst first, each the depth in
    mm it reaches and where, e.g. ([], [(1.2, (x, y))]) for one closed gap."""
    import numpy as np
    from PIL import Image, ImageDraw
    from scipy.ndimage import distance_transform_edt as edt, label
    z = shape.BoundBox.ZMax
    top = lambda sh: [f for f in sh.Faces
                      if abs(f.BoundBox.ZMax - z) < 1e-6 and abs(f.BoundBox.ZMin - z) < 1e-6]
    faces = top(shape)
    bb = Part.makeCompound(faces).BoundBox
    pad = stroke + gap + tol + 0.5
    x0, y0 = bb.XMin - pad, bb.YMin - pad
    W, H = int((bb.XLength + 2 * pad) / res) + 1, int((bb.YLength + 2 * pad) / res) + 1
    px = lambda w: [((p.x - x0) / res, (p.y - y0) / res) for p in w.discretize(Deflection=res / 4)]

    def raster(fs):
        img = Image.new('1', (W, H), 0)
        draw = ImageDraw.Draw(img)
        for f in fs:
            draw.polygon(px(f.OuterWire), fill=1)
            for w in f.Wires:
                if not w.isSame(f.OuterWire):
                    draw.polygon(px(w), fill=0)
        return np.array(img, dtype=bool)
    m = raster(faces)
    r_s, r_g = stroke / 2 / res, gap / 2 / res
    close = lambda a: edt(edt(~a) <= r_g) > r_g          # dilate, then erode
    opened = edt(~(edt(m) > r_s)) <= r_s                 # erode, then dilate
    closed = close(m)
    own = np.zeros_like(m)                               # gaps inside one letter / part
    for g in (groups_of(shape) if letters else []):
        own |= close(raster(top(g)))
    out = []
    for lost, keep in ((m & ~opened, opened), (closed & ~m & ~own, ~closed)):
        if not lost.any():
            out.append([]); continue
        d = edt(~keep) * res if keep.any() else np.full(m.shape, 99.0)
        d[~lost] = 0
        blobs, n = label(d > tol)
        fails = []
        for k in range(1, n + 1):
            ys, xs = np.nonzero(blobs == k)
            j = np.argmax(d[ys, xs])
            fails.append((float(d[ys[j], xs[j]]), (x0 + xs[j] * res, y0 + ys[j] * res)))
        out.append(sorted(fails, reverse=True))
    return tuple(out)


# ---------------------------------------------------------------- monoline lettering
# A single-line letter set for small markings: every stroke is `w` wide with
# round ends, and counters and letter gaps are built to at least MIN_GAP, so
# the printer's limits hold by construction (DejaVu at 3 mm caps fails them:
# sharp terminals, 0.4 mm counters). Glyphs are centre lines in a box of
# width a (per letter) and height b = cap - w; only the letters the case uses.

def _ell(cx, cy, rx, ry, a0, a1, n=24):
    import math
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _glyph(ch, a, b):
    """(width factor, centre-line polylines); a closed polyline repeats its
    first point. An open polyline must not run back onto itself (the offset
    turns the overlap into a hole): draw a stem as its own stroke. Bowls of two-storey letters are b/4 tall so each counter is
    b/2 - w; the cap height is chosen so that is >= MIN_GAP."""
    r, q = a / 2, b / 4
    if ch == ' ':
        return 0.6, []
    if ch in 'O0':
        k = 1.0 if ch == 'O' else 0.9
        a = a * k; r = a / 2
        return k, [_ell(r, b - r, r, r, 180, 0) + _ell(r, r, r, r, 0, -180) + [(0, b - r)]]
    if ch == '1':
        return 0.7, [[(0, b * 0.78), (a * 0.7, b), (a * 0.7, 0)]]
    if ch == '2':
        return 1.0, [_ell(r, b - r, r, r, 165, -25) + [(0, 0), (a, 0)]]
    if ch == '3':
        return 1.0, [_ell(r, b - q, r, q, 155, -90) + _ell(r, q, r, q, 90, -155)]
    if ch == '4':
        a = a * 1.25
        return 1.25, [[(0, b), (0, b * 0.35), (a, b * 0.35)], [(a * 0.72, b * 0.72), (a * 0.72, 0)]]
    if ch == '6':
        p = b * 0.3
        return 1.0, [_ell(r, p, r, p, 0, 360), [(0, p), (0, b - r)] + _ell(r, b - r, r, r, 180, 30)]
    if ch == 'A':
        return 1.0, [[(0, 0)] + _ell(r, b - r, r, r, 180, 0) + [(a, 0)], [(0, b * 0.42), (a, b * 0.42)]]
    if ch == 'B':
        return 1.0, [[(0, 0), (0, b)], [(0, b), (r, b)] + _ell(r, b - q, r, q, 90, -90) + [(0, b / 2)],
                     [(0, b / 2), (r, b / 2)] + _ell(r, q, r, q, 90, -90) + [(0, 0)]]
    if ch == 'C':
        return 1.0, [_ell(r, b - r, r, r, 35, 180) + _ell(r, r, r, r, 180, 325)]
    if ch == 'D':
        return 1.0, [[(0, 0), (0, b)] + _ell(r, b - r, r, r, 90, 0) + _ell(r, r, r, r, 0, -90) + [(0, 0)]]
    if ch == 'E':
        return 1.0, [[(a, b), (0, b), (0, 0), (a, 0)], [(0, b / 2), (a * 0.85, b / 2)]]
    if ch == 'G':
        a = a * 1.3; r2 = a / 2
        return 1.3, [_ell(r2, b - r2, r2, r2, 50, 180) + _ell(r2, r2, r2, r2, 180, 360)
                     + [(a, b * 0.45), (a - 0.6, b * 0.45)]]
    if ch == 'H':
        return 1.0, [[(0, 0), (0, b)], [(a, 0), (a, b)], [(0, b / 2), (a, b / 2)]]
    if ch == 'I':
        return 0.0, [[(0, 0), (0, b)]]
    if ch == 'L':
        return 0.9, [[(0, b), (0, 0), (a * 0.9, 0)]]
    if ch == 'M':
        a = a * 1.6
        return 1.6, [[(0, 0), (0, b), (a / 2, b * 0.35), (a, b), (a, 0)]]
    if ch == 'N':
        a = a * 1.1
        return 1.1, [[(0, 0), (0, b), (a, 0), (a, b)]]
    if ch == 'P':
        p = b * 0.28
        return 1.0, [[(0, 0), (0, b)], [(0, b), (r, b)] + _ell(r, b - p, r, p, 90, -90) + [(0, b - 2 * p)]]
    if ch == 'R':
        return 1.0, [[(0, 0), (0, b)], [(0, b), (r, b)] + _ell(r, b - q, r, q, 90, -90) + [(0, b / 2)],
                     [(r, b / 2), (a, 0)]]
    if ch == 'S':
        return 1.0, [_ell(r, b - q, r, q, 35, 270) + _ell(r, q, r, q, 90, -145)]
    if ch == 'T':
        a = a * 1.2
        return 1.2, [[(0, b), (a, b)], [(a / 2, b), (a / 2, 0)]]
    if ch == 'U':
        return 1.0, [[(0, b)] + _ell(r, r, r, r, 180, 360) + [(a, b)]]
    if ch == 'V':
        a = a * 1.2
        return 1.2, [[(0, b), (a / 2, 0), (a, b)]]
    if ch == 'W':
        a = a * 1.9
        return 1.9, [[(0, b), (a * 0.22, 0), (a / 2, b * 0.75), (a * 0.78, 0), (a, b)]]
    if ch == '-':
        return 0.6, [[(0, b / 2), (a * 0.6, b / 2)]]
    if ch == '=':
        return 0.85, [[(0, b / 2 - 0.6), (a * 0.85, b / 2 - 0.6)], [(0, b / 2 + 0.6), (a * 0.85, b / 2 + 0.6)]]
    if ch == '.':
        return 0.0, [[(0, 0)]]
    if ch == ':':
        return 0.0, [[(0, b * 0.15)], [(0, b * 0.75)]]
    if ch == '(':
        return 0.25, [_ell(a / 2, b / 2, a / 2, b / 2, 120, 240)]
    if ch == ')':
        return 0.25, [_ell(-a / 4, b / 2, a / 2, b / 2, -60, 60)]
    raise ValueError('no monoline glyph for %r' % ch)


def _capsule(p, q, w):
    """A straight stroke from p to q drawn with a round pen of width w."""
    import math
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0)
    ends = [disc(x0, y0, w / 2), disc(x1, y1, w / 2)]
    if L < 1e-9:
        return ends[0]
    nx, ny = -(y1 - y0) / L * w / 2, (x1 - x0) / L * w / 2
    band = poly([(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)])
    return band.fuse(ends)


def _stroke(pts, w):
    """A centre line drawn with a round pen of width w (round ends and joins)."""
    if len(pts) == 1:
        return [disc(pts[0][0], pts[0][1], w * 0.6)]
    if len(pts) == 2:                  # one line defines no plane to offset in
        return [_capsule(pts[0], pts[1], w)]
    wire = Part.makePolygon([V(x, y, 0) for x, y in pts])
    if wire.isClosed():
        f = Part.Face(wire)
        return [f.makeOffset2D(w / 2, 0).cut(f.makeOffset2D(-w / 2, 0))]
    return [Part.Face(wire.makeOffset2D(w / 2, 0, False, False, False))]


def mono_text(s, cap, halign='c', w=0.64, gap=0.6):
    """Monoline text: cap height `cap` (outside of the strokes), stroke `w`,
    `gap` between letters. Returns a compound with one sub-compound per
    letter (printability() treats a letter's own corners as by design)."""
    b = cap - w
    a = 0.6 * b
    x, glyphs = 0.0, []
    for ch in s:
        if ch == '\u2022':                # bullet: a round dot, centred on the caps
            glyphs.append(Part.makeCompound([disc(x + 0.55, cap / 2, 0.55)]))
            x += 1.1 + gap
            continue
        if ch == '\u00a9':                # copyright: a C in a ring, centred on the caps
            # Smallest that holds the limits: the C's opening needs its
            # centre-line radius 0.8 (ends 48 deg off the axis are a gap
            # apart), then a gap and the ring: 4.6 mm across, taller than the caps.
            rc, gp = 0.8, gap - 0.05
            rr = rc + w + gp
            cx, cy = x + rr + w / 2, cap / 2
            g = union(*[f for p in (_ell(cx, cy, rr, rr, 0, 360, 72), _ell(cx, cy, rc, rc, 48, 312, 36))
                        for sh in _stroke(p, w) for f in sh.Faces])
            glyphs.append(Part.makeCompound([Part.makeFace([Part.makePolygon(wi.discretize(Deflection=0.01), True)
                                                            for wi in f.Wires], 'Part::FaceMakerBullseye')
                                             for f in g.Faces]))
            x += 2 * rr + w + gap
            continue
        k, lines = _glyph(ch, a, b)
        if lines:
            g = union(*[f for p in lines for sh in _stroke(p, w) for f in sh.Faces])
            # Fused arcs and short segments mesh with gaps; trace them as polylines.
            # Fusing a stroke onto a stem can leave a pinhole at the join; drop it.
            g = Part.makeCompound([Part.makeFace([Part.makePolygon(wi.discretize(Deflection=0.01), True)
                                                  for wi in f.Wires
                                                  if wi.isSame(f.OuterWire) or Part.Face(wi).Area > 0.02],
                                                 'Part::FaceMakerBullseye')
                                   for f in g.Faces])
            glyphs.append(Part.makeCompound([f.translate(V(x + w / 2, w / 2, 0)) for f in g.Faces]))
        x += k * a + w + gap
    c = Part.makeCompound(glyphs)
    bb = c.BoundBox
    dx = {'c': -(bb.XMin + bb.XMax) / 2, 'r': -bb.XMax, 'l': -bb.XMin}[halign]
    c.translate(V(dx, -cap / 2, 0))
    return c
