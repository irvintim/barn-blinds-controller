"""Build the VSP-WSC-4 enclosure Rev 3 as a spreadsheet-driven FreeCAD model.

Run headless (FreeCAD 1.1):
    freecadcmd enclosure/rev3/build_case_rev3.py

Writes enclosure/rev3/project-case-rev3.FCStd: two PartDesign bodies
(Bottom = tray, Lid = top) whose every dimension is an expression on the
`Params` spreadsheet. After this first build, edit dimensions in the
spreadsheet in the FreeCAD GUI. Re-running this script rebuilds the file from
the DEFAULTS below and overwrites spreadsheet edits.

Coordinates: origin at the board centre, z = 0 at the board's underside.
+X = terminal-block / barrel-jack wall, -X = USB / LED wall,
+Y = the board edge nearest the ESP32 antenna (KiCad's top edge).
Measurements behind the defaults: enclosure/rev3/README.md.
"""
import os
import sys

import FreeCAD as App
import Part
import Sketcher
from FreeCAD import Placement, Rotation, Vector as V

HERE = os.path.dirname(os.path.abspath(
    globals().get('__file__') or os.environ.get('CASE_SCRIPT') or sys.argv[-1]))
OUT = os.path.join(HERE, 'project-case-rev3.FCStd')
BOARD_STEP = os.path.join(HERE, '..', 'reference', 'vsp-wsc4-rev1.3-board.step')
# Board centre in the KiCad STEP export's coordinates (Edge.Cuts bbox centre).
BOARD_CX, BOARD_CY = 109.498, -85.967

# name: (value, description). Sections become header rows in the spreadsheet.
DEFAULTS = [
    ('Board (Rev 1.3, measured)', None),
    ('board_w', 65.004, 'PCB width, X'),
    ('board_l', 73.935, 'PCB length, Y'),
    ('board_t', 1.6, 'PCB thickness (fabbed 1.6; split line sits on the board top)'),
    ('hole_xl', -28.913, 'Mounting holes H2/H4 X'),
    ('hole_xr', 29.034, 'Mounting holes H1/H3 X'),
    ('hole_yt', 33.370, 'Mounting holes H1/H2 Y'),
    ('hole_yb', -33.401, 'Mounting holes H3/H4 Y'),
    ('Shell', None),
    ('board_gap', 0.25, 'Board edge to inner wall'),
    ('wall', 2.5, 'Side wall thickness'),
    ('floor_t', 2.5, 'Tray floor thickness'),
    ('lid_t', 2.5, 'Lid top thickness'),
    ('r_out', 3.0, 'Outer vertical corner radius'),
    ('r_in', 2.0, 'Inner vertical corner radius (board corners are R3)'),
    ('edge_r', 2.0, 'Fillet on the tray bottom and lid top perimeter'),
    ('standoff_h', 3.0, 'Tray standoff height (floor to board underside)'),
    ('board_play', 0.15, 'Vertical play between standoff top and board'),
    ('headroom', 14.34, 'Board top to lid ceiling (tallest part: plug, 12.05 above board top)'),
    ('Board clamp', None),
    ('standoff_d', 8.0, 'Tray corner standoff block size around each hole'),
    ('screw_d', 3.2, 'M3 clearance hole through tray'),
    ('cbore_d', 6.0, 'Counterbore under the tray for the screw head'),
    ('cbore_depth', 2.4, 'Counterbore depth'),
    ('post_d', 6.0, 'Lid post outer diameter'),
    ('post_hole_d', 2.8, 'Lid post hole (M3 self-tap); 2.8 is what Rev 2 printed with'),
    ('Tongue and groove', None),
    ('ridge_inset', 0.825, 'Ridge outer face, inset from outer wall'),
    ('ridge_w', 0.55, 'Ridge width'),
    ('ridge_h', 0.5, 'Ridge height'),
    ('ridge_chamfer', 0.25, 'Ridge top chamfer, 45 deg, both edges (as Rev 2; keep > 0)'),
    ('groove_clear', 0.125, 'Groove clearance each side of ridge'),
    ('groove_depth', 0.9, 'Groove depth into the lid rim'),
    ('-X wall: USB and LEDs', None),
    ('usb_cy', -24.96, 'J2 Micro-USB centre Y'),
    ('usb_cz', 2.745, 'J2 opening centre Z'),
    ('usb_w', 8.4, 'USB slot width (shell 7.4)'),
    ('usb_h', 3.3, 'USB slot height (shell 2.31)'),
    ('usb_rw', 13.0, 'USB outer recess width (plug overmould)'),
    ('usb_rh', 8.0, 'USB outer recess height'),
    ('usb_rdepth', 1.5, 'USB outer recess depth (Micro-B plug reach)'),
    ('led_d', 3.0, 'LED window diameter'),
    ('led_dz', 1.0, 'LED window centre above board top'),
    ('led3_y', 18.59, 'D3 red (status) Y, -X wall'),
    ('led4_y', 27.41, 'D4 white Y, -X wall'),
    ('+X wall: terminal block, jack, D5', None),
    ('term_cy', 6.70, 'J4 header centre Y'),
    ('term_w', 36.6, 'J4 cutout width (header 35.8)'),
    ('term_top', 12.8, 'J4 cutout top, above board underside (header 12.4)'),
    ('jack_cy', -24.06, 'J1 barrel jack centre Y (body 9.3 wide in the wall)'),
    ('jack_w', 9.7, 'J1 cutout width (Rev 2 had 9.0, narrower than the jack)'),
    ('jack_top', 12.4, 'J1 cutout top, above board underside'),
    ('led5_y', -16.53, 'D5 blue Y, +X wall'),
    ('Vents', None),
    ('tv_x0', 2.0, 'Top vents: slot start X'),
    ('tv_len', 10.0, 'Top vents: slot length (X)'),
    ('tv_w', 1.0, 'Top vents: slot width'),
    ('tv_y0', 2.47, 'Top vents: first slot centre Y'),
    ('tv_pitch', 5.2, 'Top vents: pitch'),
    ('tv_n', 6, 'Top vents: count'),
    ('sv_w', 1.0, 'Side vents: slot width'),
    ('sv_len', 10.0, 'Side vents: slot height'),
    ('sv_z0', 1.75, 'Side vents: bottom, above board top'),
    ('sv_pitch', 5.2, 'Side vents: pitch'),
    ('sv_n', 6, 'Side vents: count per wall'),
    ('svp_x0', -4.5, '+Y wall vents: first slot centre X'),
    ('svm_x0', -5.5, '-Y wall vents: first slot centre X'),
    ('Wall mount: keyholes', None),
    ('kh_dx', 13.0, 'Keyhole X, +/- from centre'),
    ('kh_y', 10.0, 'Keyhole entry-hole centre Y (slot runs toward +Y)'),
    ('kh_head_d', 7.5, 'Entry hole diameter'),
    ('kh_slot_w', 4.0, 'Slot width'),
    ('kh_slot_len', 10.0, 'Slot length, hole centre to slot end'),
    ('kh_plate_w', 45.0, 'Inside reinforcing plate width'),
    ('kh_plate_l', 25.0, 'Inside reinforcing plate length'),
    ('kh_plate_t', 0.8, 'Plate thickness'),
    ('kh_win_w', 10.0, 'Head channel width'),
    ('kh_win_l', 18.0, 'Head channel length'),
    ('kh_recess', 1.0, 'Head channel depth into the floor (leaves 1.5 mm of floor under it)'),
    ('kh_cap_t', 0.6, 'Cap over the head channel: closes the keyhole from inside (Rev 2 used 0.4)'),
    ('kh_cap_lip', 2.0, 'Cap overlap past the head channel, each side'),
    ('DIN rail clips: 2x Phoenix USA 10 (1201578) or generic 42.6 x 10 equivalent', None),
    ('din_cx', 0.0, 'Clip centre X (clips run across the rail, along X)'),
    ('din_cy', 11.5, 'Midpoint between the two clips, Y (rail runs along Y)'),
    ('din_spacing', 39.0, 'Clip centre to clip centre, Y; straddles the keyholes'),
    ('din_pitch', 12.5, 'Hole pitch (25 mm across the outer two holes)'),
    ('din_hole_d', 2.75, 'Self-cutting M3 pilot'),
    ('din_boss_d', 6.0, 'Inside boss diameter'),
    ('din_boss_h', 1.5, 'Inside boss height above floor'),
    ('Side mount: 1 DIN clip on the -X wall (terminal block facing out)', None),
    ('side_cy', 5.0, 'Clip centre Y on the -X wall (holes run along Y)'),
    ('side_cz', 10.0, 'Hole line Z, above board underside (lid wall; clear of USB recess and LEDs)'),
]
P = {r[0]: r[1] for r in DEFAULTS if r[1] is not None}


def X(expr):
    """'{a} + {b}' -> 'Params.a + Params.b' (a FreeCAD expression)."""
    return expr.format(**{k: 'Params.' + k for k in P})


def ev(expr):
    return float(eval(expr.format(**{k: '(%r)' % float(v) for k, v in P.items()})))


# Derived expressions used by many features.
IW = '({board_w} + 2*{board_gap})'
IL = '({board_l} + 2*{board_gap})'
OW = '({board_w} + 2*{board_gap} + 2*{wall})'
OL = '({board_l} + 2*{board_gap} + 2*{wall})'
Z_SPLIT = '{board_t}'
Z_FLOOR_TOP = '(-{standoff_h} - {board_play})'
Z_FLOOR_BOT = '(-{standoff_h} - {board_play} - {floor_t})'
Z_CEIL = '({board_t} + {headroom})'

doc = App.newDocument('project_case_rev3')
sheet = doc.addObject('Spreadsheet::Sheet', 'Params')
row = 1
sheet.set('A1', 'Parameter'); sheet.set('B1', 'Value (mm)'); sheet.set('C1', 'Description')
for r in DEFAULTS:
    row += 1
    if r[1] is None:
        row += 1
        sheet.set('A%d' % row, '# ' + r[0])
        continue
    name, val, desc = r
    sheet.set('A%d' % row, name)
    sheet.set('B%d' % row, str(val))
    sheet.setAlias('B%d' % row, name)
    sheet.set('C%d' % row, desc)
sheet.setColumnWidth('A', 130); sheet.setColumnWidth('C', 420)
doc.recompute()


def plane(body, role):
    return [f for f in body.Origin.OriginFeatures if f.Role == role][0]


def sketch(body, name, role, offset):
    """role XY: (u,v)=(x,y) n=+Z | XZ: (x,z) n=-Y | YZ: (y,z) n=+X."""
    sk = body.newObject('Sketcher::SketchObject', name)
    sk.AttachmentSupport = [(plane(body, role + '_Plane'), '')]
    sk.MapMode = 'FlatFace'
    sk.AttachmentOffset = Placement(V(0, 0, ev(offset)), Rotation())
    sk.setExpression('.AttachmentOffset.Base.z', X(offset))
    sk.Visibility = False
    return sk


def con(sk, kind, *args, expr=None):
    args = list(args)
    if expr is not None:
        args.append(ev(expr))
    i = sk.addConstraint(Sketcher.Constraint(kind, *args))
    if expr is not None:
        sk.setExpression('Constraints[%d]' % i, X(expr))
    return i


def anchor(sk, cx, cy):
    g = sk.addGeometry(Part.Point(V(ev(cx), ev(cy), 0)), True)
    con(sk, 'DistanceX', -1, 1, g, 1, expr=cx)
    con(sk, 'DistanceY', -1, 1, g, 1, expr=cy)
    return g


def circle(sk, cx, cy, d):
    g = sk.addGeometry(Part.Circle(V(ev(cx), ev(cy), 0), V(0, 0, 1), ev(d) / 2))
    con(sk, 'DistanceX', -1, 1, g, 3, expr=cx)
    con(sk, 'DistanceY', -1, 1, g, 3, expr=cy)
    con(sk, 'Diameter', g, expr=d)


def rect(sk, cx, cy, w, h):
    x, y, ww, hh = ev(cx), ev(cy), ev(w), ev(h)
    pts = [V(x - ww / 2, y - hh / 2, 0), V(x + ww / 2, y - hh / 2, 0),
           V(x + ww / 2, y + hh / 2, 0), V(x - ww / 2, y + hh / 2, 0)]
    L = [sk.addGeometry(Part.LineSegment(pts[i], pts[(i + 1) % 4])) for i in range(4)]
    for i in range(4):
        con(sk, 'Coincident', L[i], 2, L[(i + 1) % 4], 1)
    con(sk, 'Horizontal', L[0]); con(sk, 'Horizontal', L[2])
    con(sk, 'Vertical', L[1]); con(sk, 'Vertical', L[3])
    c = anchor(sk, cx, cy)
    con(sk, 'Symmetric', L[0], 1, L[1], 2, c, 1)
    con(sk, 'DistanceX', L[0], 1, L[0], 2, expr=w)
    con(sk, 'DistanceY', L[1], 1, L[1], 2, expr=h)


def rrect(sk, cx, cy, w, h, r):
    import math
    x, y, ww, hh, rr = ev(cx), ev(cy), ev(w), ev(h), ev(r)
    x0, x1, y0, y1 = x - ww / 2, x + ww / 2, y - hh / 2, y + hh / 2
    def arc(c, a0, a1):
        return sk.addGeometry(Part.ArcOfCircle(Part.Circle(c, V(0, 0, 1), rr), a0, a1))
    bl = arc(V(x0 + rr, y0 + rr, 0), math.pi, 1.5 * math.pi)
    l0 = sk.addGeometry(Part.LineSegment(V(x0 + rr, y0, 0), V(x1 - rr, y0, 0)))
    br = arc(V(x1 - rr, y0 + rr, 0), 1.5 * math.pi, 2 * math.pi)
    l1 = sk.addGeometry(Part.LineSegment(V(x1, y0 + rr, 0), V(x1, y1 - rr, 0)))
    tr = arc(V(x1 - rr, y1 - rr, 0), 0, 0.5 * math.pi)
    l2 = sk.addGeometry(Part.LineSegment(V(x1 - rr, y1, 0), V(x0 + rr, y1, 0)))
    tl = arc(V(x0 + rr, y1 - rr, 0), 0.5 * math.pi, math.pi)
    l3 = sk.addGeometry(Part.LineSegment(V(x0, y1 - rr, 0), V(x0, y0 + rr, 0)))
    for a, b in ((bl, l0), (l0, br), (br, l1), (l1, tr), (tr, l2), (l2, tl), (tl, l3), (l3, bl)):
        con(sk, 'Tangent', a, 2, b, 1)
    con(sk, 'Horizontal', l0); con(sk, 'Horizontal', l2)
    con(sk, 'Vertical', l1); con(sk, 'Vertical', l3)
    for a in (br, tr, tl):
        con(sk, 'Equal', bl, a)
    con(sk, 'Radius', bl, expr=r)
    c = anchor(sk, cx, cy)
    con(sk, 'Symmetric', bl, 3, tr, 3, c, 1)
    con(sk, 'DistanceX', l3, 1, l1, 1, expr=w)
    con(sk, 'DistanceY', l0, 1, l2, 1, expr=h)


def obround(sk, cx, cy, w, h):
    """Horizontal slot, overall w x h, semicircular ends."""
    import math
    x, y, ww, hh = ev(cx), ev(cy), ev(w), ev(h)
    r = hh / 2
    ra = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(x + ww / 2 - r, y, 0), V(0, 0, 1), r), -0.5 * math.pi, 0.5 * math.pi))
    lt = sk.addGeometry(Part.LineSegment(V(x + ww / 2 - r, y + r, 0), V(x - ww / 2 + r, y + r, 0)))
    la = sk.addGeometry(Part.ArcOfCircle(Part.Circle(V(x - ww / 2 + r, y, 0), V(0, 0, 1), r), 0.5 * math.pi, 1.5 * math.pi))
    lb = sk.addGeometry(Part.LineSegment(V(x - ww / 2 + r, y - r, 0), V(x + ww / 2 - r, y - r, 0)))
    for a, b in ((ra, lt), (lt, la), (la, lb), (lb, ra)):
        con(sk, 'Tangent', a, 2, b, 1)
    con(sk, 'Horizontal', lt)
    con(sk, 'Equal', ra, la)
    con(sk, 'Diameter', ra, expr=h)
    c = anchor(sk, cx, cy)
    con(sk, 'Symmetric', ra, 3, la, 3, c, 1)
    con(sk, 'DistanceX', la, 3, ra, 3, expr='(%s) - (%s)' % (w, h))


def pad(body, name, sk, length, reversed=False):
    f = body.newObject('PartDesign::Pad', name)
    f.Profile = sk; f.Length = ev(length); f.setExpression('Length', X(length))
    f.Reversed = reversed; f.Refine = True
    return f


def pocket(body, name, sk, length=None, reversed=False):
    f = body.newObject('PartDesign::Pocket', name)
    f.Profile = sk; f.Reversed = reversed; f.Refine = True
    if length is None:
        f.Type = 'ThroughAll'
    else:
        f.Length = ev(length); f.setExpression('Length', X(length))
    return f


def pattern(body, name, feature, sk, axis, n, pitch, reversed=False):
    f = body.newObject('PartDesign::LinearPattern', name)
    f.Originals = [feature]
    f.Direction = (sk, [axis])
    f.Reversed = reversed
    f.Occurrences = int(ev(n)); f.setExpression('Occurrences', X(n))
    f.Length = ev('(%s - 1) * %s' % (n, pitch))
    f.setExpression('Length', X('(%s - 1) * %s' % (n, pitch)))
    f.Refine = True
    return f


def perimeter_fillet(body, name, base, z, radius):
    doc.recompute()
    sh = base.Shape
    face = [i for i, f in enumerate(sh.Faces, 1)
            if abs(f.BoundBox.ZMin - z) < 1e-4 and abs(f.BoundBox.ZMax - z) < 1e-4][0]
    edges = ['Edge%d' % i for i, e in enumerate(sh.Edges, 1)
             if any(e.isSame(fe) for fe in sh.Faces[face - 1].Edges)]
    f = body.newObject('PartDesign::Fillet', name)
    f.Base = (base, edges)
    f.Radius = ev(radius); f.setExpression('Radius', X(radius))
    f.Refine = True
    return f


def wall_x(body, name, side, draw, length='{wall} + 2'):
    """Cut through the -X or +X wall. draw(sk) adds geometry in (y, z)."""
    off = ('(-%s/2 + 1)' % IW) if side < 0 else ('(%s/2 - 1)' % IW)
    sk = sketch(body, 'Sk_' + name, 'YZ', off)
    draw(sk)
    return pocket(body, name, sk, length, reversed=side > 0)


# ---------------------------------------------------------------- Bottom (tray)
bot = doc.addObject('PartDesign::Body', 'Bottom')
sk = sketch(bot, 'Sk_TrayOutline', 'XY', Z_FLOOR_BOT)
rrect(sk, '0', '0', OW, OL, '{r_out}')
f = pad(bot, 'TrayShell', sk, '{floor_t} + {standoff_h} + {board_play} + {board_t}')
f = perimeter_fillet(bot, 'TrayEdge', f, ev(Z_FLOOR_BOT), '{edge_r}')
sk = sketch(bot, 'Sk_TrayCavity', 'XY', Z_SPLIT)
rrect(sk, '0', '0', IW, IL, '{r_in}')
pocket(bot, 'TrayCavity', sk, '{standoff_h} + {board_play} + {board_t}')

sk = sketch(bot, 'Sk_Standoffs', 'XY', Z_FLOOR_TOP)
for hx, sx in (('{hole_xl}', -1), ('{hole_xr}', 1)):
    for hy, sy in (('{hole_yb}', -1), ('{hole_yt}', 1)):
        # block from (hole - standoff_d/2) out to the inner walls
        ex = '(%d*%s/2)' % (sx, IW); ey = '(%d*%s/2)' % (sy, IL)
        nx = '(%s - %d*{standoff_d}/2)' % (hx, sx); ny = '(%s - %d*{standoff_d}/2)' % (hy, sy)
        rect(sk, '(%s + %s)/2' % (ex, nx), '(%s + %s)/2' % (ey, ny),
             '%d*(%s - %s)' % (sx, ex, nx), '%d*(%s - %s)' % (sy, ey, ny))
pad(bot, 'Standoffs', sk, '{standoff_h}')

HOLES = [(hx, hy) for hx in ('{hole_xl}', '{hole_xr}') for hy in ('{hole_yb}', '{hole_yt}')]
sk = sketch(bot, 'Sk_ScrewHoles', 'XY', Z_FLOOR_BOT)
for hx, hy in HOLES:
    circle(sk, hx, hy, '{screw_d}')
pocket(bot, 'ScrewHoles', sk, None, reversed=True)
sk = sketch(bot, 'Sk_Counterbores', 'XY', Z_FLOOR_BOT)
for hx, hy in HOLES:
    circle(sk, hx, hy, '{cbore_d}')
pocket(bot, 'Counterbores', sk, '{cbore_depth}', reversed=True)

sk = sketch(bot, 'Sk_Ridge', 'XY', Z_SPLIT)
rrect(sk, '0', '0', '%s - 2*{ridge_inset}' % OW, '%s - 2*{ridge_inset}' % OL, '{r_out} - {ridge_inset}')
rrect(sk, '0', '0', '%s - 2*({ridge_inset} + {ridge_w})' % OW,
      '%s - 2*({ridge_inset} + {ridge_w})' % OL, '{r_out} - {ridge_inset} - {ridge_w}')
pad(bot, 'Ridge', sk, '{ridge_h} - {ridge_chamfer}')
# Top of the ridge, chamfered 45 degrees on both edges without referencing
# edges by name (so it survives parameter edits): a solid cap over the outer
# outline tapered inward, then a pocket of the inner outline tapered outward
# going up, which hollows the cap back out to a ring.
Z_CH = '%s + {ridge_h} - {ridge_chamfer}' % Z_SPLIT
sk = sketch(bot, 'Sk_RidgeChamferOuter', 'XY', Z_CH)
rrect(sk, '0', '0', '%s - 2*{ridge_inset}' % OW, '%s - 2*{ridge_inset}' % OL, '{r_out} - {ridge_inset}')
f = pad(bot, 'RidgeChamferOuter', sk, '{ridge_chamfer}')
f.TaperAngle = -45
sk = sketch(bot, 'Sk_RidgeChamferInner', 'XY', Z_CH)
rrect(sk, '0', '0', '%s - 2*({ridge_inset} + {ridge_w})' % OW,
      '%s - 2*({ridge_inset} + {ridge_w})' % OL, '{r_out} - {ridge_inset} - {ridge_w}')
f = pocket(bot, 'RidgeChamferInner', sk, '{ridge_chamfer}', reversed=True)
f.TaperAngle = 45

# Keyholes: entry hole + slot through the floor; inside, a reinforcing plate
# with a head channel recessed into the floor around each keyhole, and a cap
# over the channel. The cap keeps the wall screw or nail head off the board
# underside, as in Rev 2; the head slides in the closed channel beneath it.
KH = (('-{kh_dx}'), ('{kh_dx}'))
sk = sketch(bot, 'Sk_KeyholePlate', 'XY', Z_FLOOR_TOP)
rect(sk, '0', '{kh_y} + {kh_plate_l}/2 - 9', '{kh_plate_w}', '{kh_plate_l}')
for kx in KH:
    rect(sk, kx, '{kh_y} + {kh_win_l}/2 - 6', '{kh_win_w}', '{kh_win_l}')
pad(bot, 'KeyholePlate', sk, '{kh_plate_t}')
sk = sketch(bot, 'Sk_KeyholeChannel', 'XY', Z_FLOOR_TOP)
for kx in KH:
    rect(sk, kx, '{kh_y} + {kh_win_l}/2 - 6', '{kh_win_w}', '{kh_win_l}')
pocket(bot, 'KeyholeChannel', sk, '{kh_recess}')
sk = sketch(bot, 'Sk_KeyholeEntry', 'XY', Z_FLOOR_BOT)
for kx in KH:
    circle(sk, kx, '{kh_y}', '{kh_head_d}')
pocket(bot, 'KeyholeEntry', sk, None, reversed=True)
sk = sketch(bot, 'Sk_KeyholeSlot', 'XY', Z_FLOOR_BOT)
for kx in KH:
    rect(sk, kx, '{kh_y} + {kh_slot_len}/2', '{kh_slot_w}', '{kh_slot_len}')
pocket(bot, 'KeyholeSlot', sk, None, reversed=True)
sk = sketch(bot, 'Sk_KeyholeCap', 'XY', Z_FLOOR_TOP + ' + {kh_plate_t}')
for kx in KH:
    rect(sk, kx, '{kh_y} + {kh_win_l}/2 - 6', '{kh_win_w} + 2*{kh_cap_lip}', '{kh_win_l} + 2*{kh_cap_lip}')
pad(bot, 'KeyholeCap', sk, '{kh_cap_t}')

DIN = ('{din_cx} - {din_pitch}', '{din_cx}', '{din_cx} + {din_pitch}')
DIN_Y = ('{din_cy} - {din_spacing}/2', '{din_cy} + {din_spacing}/2')   # two clips
sk = sketch(bot, 'Sk_DinBosses', 'XY', Z_FLOOR_TOP)
for dy in DIN_Y:
    for dx in DIN:
        circle(sk, dx, dy, '{din_boss_d}')
pad(bot, 'DinBosses', sk, '{din_boss_h}')
sk = sketch(bot, 'Sk_DinHoles', 'XY', Z_FLOOR_BOT)
for dy in DIN_Y:
    for dx in DIN:
        circle(sk, dx, dy, '{din_hole_d}')
pocket(bot, 'DinHoles', sk, None, reversed=True)

LED_Z = '({board_t} + {led_dz})'
def usb_slot(sk): obround(sk, '{usb_cy}', '{usb_cz}', '{usb_w}', '{usb_h}')
def leds_m(sk):
    circle(sk, '{led3_y}', LED_Z, '{led_d}'); circle(sk, '{led4_y}', LED_Z, '{led_d}')
def led_p(sk): circle(sk, '{led5_y}', LED_Z, '{led_d}')
def usb_recess(body, name):
    sk = sketch(body, 'Sk_' + name, 'YZ', '(-%s/2 - 1)' % OW)
    obround(sk, '{usb_cy}', '{usb_cz}', '{usb_rw}', '{usb_rh}')
    pocket(body, name, sk, '1 + {usb_rdepth}', reversed=True)

# J4 and J1 sit on the board at the split line and reach into the +X wall, so
# the tray's tongue (ridge) must be notched under their lid openings.
def notch(sk, cy, w):
    # z from 0.3 below the rim (parts overhanging the board edge dip slightly
    # below the board top) up past the ridge
    rect(sk, cy, '{board_t} + 0.85', w, '2.3')
wall_x(bot, 'RidgeNotchTerminal', 1, lambda s: notch(s, '{term_cy}', '{term_w}'))
wall_x(bot, 'RidgeNotchJack', 1, lambda s: notch(s, '{jack_cy}', '{jack_w}'))

wall_x(bot, 'UsbSlot', -1, usb_slot)
usb_recess(bot, 'UsbRecess')
wall_x(bot, 'LedWindowsD3D4', -1, leds_m)
wall_x(bot, 'LedWindowD5', 1, led_p)

# ---------------------------------------------------------------- Lid (top)
lid = doc.addObject('PartDesign::Body', 'Lid')
sk = sketch(lid, 'Sk_LidOutline', 'XY', Z_SPLIT)
rrect(sk, '0', '0', OW, OL, '{r_out}')
f = pad(lid, 'LidShell', sk, '{headroom} + {lid_t}')
f = perimeter_fillet(lid, 'LidEdge', f, ev('%s + {lid_t}' % Z_CEIL), '{edge_r}')
sk = sketch(lid, 'Sk_LidCavity', 'XY', Z_SPLIT)
rrect(sk, '0', '0', IW, IL, '{r_in}')
pocket(lid, 'LidCavity', sk, '{headroom}', reversed=True)

sk = sketch(lid, 'Sk_Posts', 'XY', Z_CEIL)
for hx, hy in HOLES:
    circle(sk, hx, hy, '{post_d}')
    circle(sk, hx, hy, '{post_hole_d}')
pad(lid, 'Posts', sk, '{headroom}', reversed=True)

sk = sketch(lid, 'Sk_Groove', 'XY', Z_SPLIT)
gin = '({ridge_inset} - {groove_clear})'
gout = '({ridge_inset} + {ridge_w} + {groove_clear})'
rrect(sk, '0', '0', '%s - 2*%s' % (OW, gin), '%s - 2*%s' % (OL, gin), '{r_out} - %s' % gin)
rrect(sk, '0', '0', '%s - 2*%s' % (OW, gout), '%s - 2*%s' % (OL, gout), '{r_out} - %s' % gout)
pocket(lid, 'Groove', sk, '{groove_depth}', reversed=True)

def up_from_split(sk, cy, w, top):
    # rectangle from 1 mm below the split line up to `top`
    rect(sk, cy, '(({board_t} - 1) + %s)/2' % top, w, '%s - ({board_t} - 1)' % top)
wall_x(lid, 'TerminalBlock', 1, lambda s: up_from_split(s, '{term_cy}', '{term_w}', '{term_top}'))
wall_x(lid, 'BarrelJack', 1, lambda s: up_from_split(s, '{jack_cy}', '{jack_w}', '{jack_top}'))
wall_x(lid, 'LedWindowD5', 1, led_p)
wall_x(lid, 'LedWindowsD3D4', -1, leds_m)
wall_x(lid, 'UsbSlot', -1, usb_slot)
usb_recess(lid, 'UsbRecess')

# Side mount: one DIN clip on the -X wall, holes along Y, bosses inside the lid.
SIDE = ('{side_cy} - {din_pitch}', '{side_cy}', '{side_cy} + {din_pitch}')
sk = sketch(lid, 'Sk_SideClipBosses', 'YZ', '-%s/2' % IW)       # inner face of -X wall
for sy in SIDE:
    circle(sk, sy, '{side_cz}', '{din_boss_d}')
pad(lid, 'SideClipBosses', sk, '{din_boss_h}')                   # YZ normal is +X: inward
sk = sketch(lid, 'Sk_SideClipHoles', 'YZ', '(-%s/2 - 1)' % OW)
for sy in SIDE:
    circle(sk, sy, '{side_cz}', '{din_hole_d}')
pocket(lid, 'SideClipHoles', sk, '1 + {wall} + {din_boss_h}', reversed=True)

# Side vents: one slot cut through each Y wall, then patterned along +X.
SV_Z = '({board_t} + {sv_z0} + {sv_len}/2)'
sk = sketch(lid, 'Sk_VentsPlusY', 'XZ', '(-%s/2 + 1)' % IL)    # XZ normal is -Y
rect(sk, '{svp_x0}', SV_Z, '{sv_w}', '{sv_len}')
v = pocket(lid, 'VentPlusY', sk, '{wall} + 2')
pattern(lid, 'VentsPlusY', v, sk, 'H_Axis', '{sv_n}', '{sv_pitch}')
sk = sketch(lid, 'Sk_VentsMinusY', 'XZ', '(%s/2 - 1)' % IL)
rect(sk, '{svm_x0}', SV_Z, '{sv_w}', '{sv_len}')
v = pocket(lid, 'VentMinusY', sk, '{wall} + 2', reversed=True)
pattern(lid, 'VentsMinusY', v, sk, 'H_Axis', '{sv_n}', '{sv_pitch}')
sk = sketch(lid, 'Sk_VentsTop', 'XY', '%s - 1' % Z_CEIL)
rect(sk, '{tv_x0} + {tv_len}/2', '{tv_y0}', '{tv_len}', '{tv_w}')
v = pocket(lid, 'VentTop', sk, '{lid_t} + 2', reversed=True)
pattern(lid, 'VentsTop', v, sk, 'V_Axis', '{tv_n}', '{tv_pitch}')

# ---------------------------------------------------------------- reference board
if os.path.exists(BOARD_STEP):
    shape = Part.read(BOARD_STEP)
    keep = [s for s in shape.Solids if s.BoundBox.DiagonalLength > 2.0]
    ref = doc.addObject('Part::Feature', 'Board_Rev1_3')
    ref.Shape = Part.makeCompound(keep)
    ref.Placement = Placement(V(-BOARD_CX, -BOARD_CY, 0), Rotation())
    ref.Label = 'Board Rev 1.3 (reference, not printed)'

doc.recompute()
bad = [o.Name for o in doc.Objects if 'Invalid' in o.State or 'Error' in str(o.State)]
for body in (bot, lid):
    s = body.Shape
    print('%-7s valid=%s solids=%d volume=%.0f mm3 bbox=%s'
          % (body.Name, s.isValid(), len(s.Solids), s.Volume, s.BoundBox))
print('features with errors:', bad or 'none')
doc.saveAs(OUT)
print('saved', OUT)
