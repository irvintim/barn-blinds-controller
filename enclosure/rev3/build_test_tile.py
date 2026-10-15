"""Inlay test tile v2 for the Rev 3 lid markings (about 7 g of PETG).

Tile v1 (2026-10-14) settled the depth: 0.6, 0.8 and 1.0 mm inlays looked the
same, so mark_d stays 0.6. Its small labels, icons and tagline came out
blurry, and the bolt lost its tips. v2 measures what the printer resolves and
compares the current lid sizes with bolder ones. Print it with Elephant foot
compensation 0 and the Arachne wall generator (README, "Inlay test tile").

Run headless (FreeCAD 1.1):
    freecadcmd enclosure/rev3/build_test_tile.py

Writes exports/inlay-test-tile-{base,blue,white}.stl and
renders/inlay-test-tile.png. Rows, top to bottom (all 0.6 mm deep):
  Ladders     white lines 0.4 0.5 0.6 0.7 0.8 1.0 mm wide (left), and black
              gaps of the same widths in a white block (right), thin to thick
  Labels      SW1 / GND / SH4 stacked at the real J4 pitch, then TOP=UP, in
              three versions: A as on the lid now (2.5 mm condensed),
              B the same font at 3.0 mm, C DejaVu Sans Bold at 3.0 mm
  Icons       the four LED / USB icons at the current size, then 1.4x
  Tagline     blue: SHADE CONTROLLER \u2022 4 as now, then SHADE CONTROLLER in
              DejaVu Sans Bold at 3.0 mm
"""
import os
import sys

import Part
import MeshPart
from FreeCAD import Vector as V

HERE = os.path.dirname(os.path.abspath(
    globals().get('__file__') or os.environ.get('CASE_SCRIPT') or sys.argv[-1]))
sys.path.insert(0, HERE)
from marks import icon_bolt, icon_power, icon_status, icon_usb, text  # noqa: E402

FONTS = os.path.join(HERE, 'fonts')
F_LABEL = os.path.join(FONTS, 'DejaVuSansCondensed-Bold.ttf')
F_TAG = os.path.join(FONTS, 'DejaVuSansMono-Bold.ttf')

F_BOLD = os.path.join(FONTS, 'DejaVuSans-Bold.ttf')

# Same values as build_case_rev3.py DEFAULTS (mark_d, lbl_h, j4_pitch, tag_w).
MARK_D, LBL_H, PITCH, TAG_W = 0.6, 2.5, 3.5, 40.0
WIDTHS = (0.4, 0.5, 0.6, 0.7, 0.8, 1.0)
TILE_W, TILE_H, TILE_T, TILE_R = 64.0, 61.0, 1.6, 3.0
EDGE_MIN = 1.5                      # every mark stays this far inside the tile


def at(faces, x, y):
    return faces.copy().translate(V(x, y, 0))


def box(x0, y0, x1, y1):
    pts = [V(x0, y0, 0), V(x1, y0, 0), V(x1, y1, 0), V(x0, y1, 0)]
    return Part.Face(Part.makePolygon(pts + [pts[0]]))


def faces(*shapes):
    return Part.makeCompound([f for sh in shapes for f in sh.Faces])


# (name, colour, depth, faces); y runs down the tile from the top edge.
marks = []
y = TILE_H / 2 - 2.5                                            # top of row 1
xs = [-28 + i * 3.0 for i in range(len(WIDTHS))]               # line ladder
marks.append(('line ladder', 'white', MARK_D,
              faces(*[box(x - w / 2, y - 6, x + w / 2, y) for x, w in zip(xs, WIDTHS)])))
gap = box(6, y - 6, 29, y)                                      # gap ladder
for i, w in enumerate(WIDTHS):
    x = 9 + i * 3.4
    gap = gap.cut(box(x - w / 2, y - 5, x + w / 2, y - 1))
marks.append(('gap ladder', 'white', MARK_D, faces(gap)))

y -= 6 + 3.5 + 1.5                                              # first label row centre
VARIANTS = (('A', F_LABEL, LBL_H, 0.0, F_LABEL, 2.0, 0.06),     # as on the lid now
            ('B', F_LABEL, 3.0, 0.0, F_LABEL, 3.0, 0.0),
            ('C', F_BOLD, 3.0, 0.0, F_BOLD, 3.0, 0.0))
for (v, font, cap, grow, kfont, kcap, kgrow), cx in zip(VARIANTS, (-20.0, 0.0, 20.0)):
    rows = [text(t, font, cap, grow=grow).translate(V(0, -i * PITCH, 0))
            for i, t in enumerate(('SW1', 'GND', 'SH4'))]
    key = text('TOP=UP', kfont, kcap, grow=kgrow).translate(V(0, -2 * PITCH - 5.0, 0))
    marks.append(('labels ' + v, 'white', MARK_D, at(faces(*rows, key), cx, y)))

y -= 2 * PITCH + 5.0 + 3.0 + 5.5                                # current-size icons
ICONS = (icon_power, icon_status, icon_bolt, icon_usb)
for k, (name, xs_) in enumerate((('icons 1.0x', (-15.0, -5.0, 4.0, 14.0)),
                                 ('icons 1.4x', (-21.0, -7.0, 5.0, 19.0)))):
    sc = 1.0 if k == 0 else 1.4
    parts = []
    for fn, x in zip(ICONS, xs_):
        f = fn().copy(); f.scale(sc)
        parts.append(f.translate(V(x, 0, 0)))
    marks.append((name, 'white', MARK_D, at(faces(*parts), 0, y)))
    y -= 5.0 + 4.5 if k == 0 else 3.5 + 3.0 + 1.5

tl = text('SHADE CONTROLLER \u2022 4', F_TAG, 1.0); tl.scale(TAG_W / tl.BoundBox.XLength)
marks.append(('tagline current', 'blue', MARK_D, at(tl, 0, y)))          # as on the lid now
marks.append(('tagline bold', 'blue', MARK_D, at(text('SHADE CONTROLLER', F_BOLD, 3.0), 0, y - 5.5)))

# ---------------------------------------------------------------- solids
slab = Part.makeBox(TILE_W, TILE_H, TILE_T, V(-TILE_W / 2, -TILE_H / 2, 0))
slab = slab.makeFillet(TILE_R, [e for e in slab.Edges
                                if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > TILE_T / 2])


def prism(faces, d):                # d below the top face to 0.5 above it
    return [f.translate(V(0, 0, TILE_T - d)).extrude(V(0, 0, d + 0.5)) for f in faces.Faces]


tools = {c: Part.makeCompound([s for n, cc, d, f in marks if cc == c for s in prism(f, d)])
         for c in ('blue', 'white')}
base = slab.cut(Part.makeCompound(list(tools.values()))).removeSplitter()
inlay = {c: slab.common(t).removeSplitter() for c, t in tools.items()}

# ---------------------------------------------------------------- checks
problems = []
for n, s in [('base', base)] + sorted(inlay.items()):
    print('%-6s valid=%s solids=%d volume=%.0f mm3' % (n, s.isValid(), len(s.Solids), s.Volume))
    if not s.isValid():
        problems.append(n + ' invalid')
if len(base.Solids) != 1:
    problems.append('base is %d solids' % len(base.Solids))
gap = abs(base.Volume + sum(s.Volume for s in inlay.values()) - slab.Volume)
if gap > 0.5:
    problems.append('base + inlays differ from the slab by %.2f mm3' % gap)
for n, c, d, f in marks:
    bb = f.BoundBox
    if (bb.XMin < -TILE_W / 2 + EDGE_MIN or bb.XMax > TILE_W / 2 - EDGE_MIN
            or bb.YMin < -TILE_H / 2 + EDGE_MIN or bb.YMax > TILE_H / 2 - EDGE_MIN):
        problems.append('%s is within %.1f mm of the tile edge' % (n, EDGE_MIN))
for i in range(len(marks)):
    for k in range(i + 1, len(marks)):
        fi, fk = marks[i][3], marks[k][3]
        if fi.BoundBox.intersect(fk.BoundBox) and fi.common(fk).Area > 1e-3:
            problems.append('%s overlaps %s' % (marks[i][0], marks[k][0]))
grams = sum(s.Volume for s in [base] + list(inlay.values())) / 1000 * 1.27
print('PETG weight about %.1f g (1.27 g/cm3, 100%% infill)' % grams)

# ---------------------------------------------------------------- outputs
os.makedirs(os.path.join(HERE, 'exports'), exist_ok=True)
for n, s in [('base', base), ('blue', inlay['blue']), ('white', inlay['white'])]:
    path = os.path.join(HERE, 'exports', 'inlay-test-tile-%s.stl' % n)
    m = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.01, AngularDeflection=0.1, Relative=False)
    m.write(path)
    closed = m.isSolid() and not m.hasNonManifolds()
    print('  ', os.path.relpath(path, HERE), 'closed' if closed else 'NOT CLOSED')
    if not closed:
        problems.append('%s: open or non-manifold mesh' % os.path.basename(path))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    import numpy as np
    fig, ax = plt.subplots(figsize=(9, 6.6), dpi=130); ax.set_facecolor('#c8d4c0')
    for s, color in ((base, '#1a1a1a'), (inlay['blue'], '#01c7fc'), (inlay['white'], '#f4f4f4')):
        v, f = s.tessellate(0.02)
        v = np.array([[p.x, p.y, p.z] for p in v]); tri = v[np.array(f)]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        tri = tri[(n[:, 2] > 0) & (tri[:, :, 2].mean(1) > TILE_T - 0.01)][:, :, :2]
        ax.add_collection(PolyCollection(tri, facecolor=color, edgecolor=color, linewidth=0.2))
    ax.set_xlim(-TILE_W / 2 - 1, TILE_W / 2 + 1); ax.set_ylim(-TILE_H / 2 - 1, TILE_H / 2 + 1)
    ax.set_aspect('equal')
    ax.set_title('Inlay test tile, marked face (black PETG, Digital Blue #01C7FC, white)')
    plt.tight_layout()
    os.makedirs(os.path.join(HERE, 'renders'), exist_ok=True)
    fig.savefig(os.path.join(HERE, 'renders', 'inlay-test-tile.png')); plt.close(fig)
    print('   renders/inlay-test-tile.png')
except ImportError as e:
    print('  render skipped:', e)

print('RESULT:', 'PASS' if not problems else 'FAIL')
for p in problems:
    print('  -', p)
