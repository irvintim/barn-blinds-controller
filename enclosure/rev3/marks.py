"""Marking geometry shared by the case builder and the inlay test tile:
text, SVG artwork and the LED / USB icons, all as flat faces at z = 0.
Needs FreeCAD (Part); sizes are in mm.
"""
import Part
from FreeCAD import Vector as V

import svgpaths


def faces_of(shape):
    return Part.makeCompound(shape.Faces)


def text(s, font, cap, halign='c', grow=0.0):
    """Text as flat faces: cap height `cap`, capitals centred on y = 0,
    x anchored at its centre ('c'), right end ('r') or left end ('l').
    `grow` emboldens every outline by that much per side (thin strokes)."""
    H = Part.makeWireString('H', font, 10.0, 0)[0]
    k = cap / Part.makeCompound(H).BoundBox.YLength
    faces = [Part.makeFace(ch, 'Part::FaceMakerBullseye')
             for ch in Part.makeWireString(s, font, 10.0, 0) if ch]
    c = Part.makeCompound(faces); c.scale(k)
    if grow:
        # Offset curves are approximations whose edges mesh with gaps (an
        # STL with open edges), so trace them as fine polylines instead.
        c = Part.makeCompound([
            Part.makeFace([Part.makePolygon(w.discretize(Deflection=0.005), True)
                           for w in f.makeOffset2D(grow).Wires], 'Part::FaceMakerBullseye')
            for f in c.Faces])
    b = c.BoundBox
    dx = {'c': -(b.XMin + b.XMax) / 2, 'r': -b.XMax, 'l': -b.XMin}[halign]
    c.translate(V(dx, -cap / 2, 0))
    return c


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
    return union(poly([(0.9, 2.3), (-1.3, -0.25), (-0.05, -0.25), (-0.9, -2.3),
                       (1.3, 0.45), (0.05, 0.45)]))


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
