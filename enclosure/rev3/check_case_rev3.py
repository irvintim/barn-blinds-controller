"""Check project-case-rev3.FCStd against the Rev 1.3 board, then export.

Run headless (FreeCAD 1.1):
    freecadcmd enclosure/rev3/check_case_rev3.py

Reads the model as it is now, including any spreadsheet edits, so run it
after changing parameters. It:
  1. recomputes, and reports any feature that errors or changes no material
  2. checks the case for interference with every board part, and lists the
     closest approach for the parts that matter (connectors, tall and
     underside parts)
  3. re-solves with deliberately changed parameters to prove the model
     survives edits (in memory; the file is not modified)
  4. exports STLs to exports/ and preview PNGs to renders/
The output is also written to check-report.txt.
"""
import os
import sys

import FreeCAD as App
import Mesh
import Part
from FreeCAD import Placement, Rotation, Vector as V

HERE = os.path.dirname(os.path.abspath(
    globals().get('__file__') or os.environ.get('CASE_SCRIPT') or sys.argv[-1]))
FCSTD = os.path.join(HERE, 'project-case-rev3.FCStd')
BOARD_STEP = os.path.join(HERE, '..', 'reference', 'vsp-wsc4-rev1.3-board.step')
BOARD_CX, BOARD_CY = 109.498, -85.967
DNP = ('PinHeader_1x07',)          # J3 is not populated
OUTSIDE = ('1790182',)             # mating plug: lives outside the case, checked only for clearance
problems = []
_report = open(os.path.join(HERE, 'check-report.txt'), 'w', buffering=1)
_print = print
def print(*a, **k):                # freecadcmd buffers stdout; keep a live report
    _print(*a, **k); _print(*a, file=_report)

doc = App.openDocument(FCSTD)
doc.recompute()
bodies = [doc.getObject('Bottom'), doc.getObject('Lid')]

print('== 1. features')
for body in bodies:
    for f in body.Group:
        if not f.TypeId.startswith('PartDesign::') or f.TypeId == 'PartDesign::Body':
            continue
        if f.State and any(s in ('Invalid', 'Error') for s in f.State):
            problems.append('%s.%s state %s' % (body.Name, f.Name, f.State))
        base = getattr(f, 'BaseFeature', None)
        if base is not None and f.Shape.isValid():
            dv = f.Shape.Volume - base.Shape.Volume
            if abs(dv) < 1e-3:
                problems.append('%s.%s changes no material' % (body.Name, f.Name))
    for f in body.Group:
        if f.TypeId == 'Sketcher::SketchObject':
            dof = f.solve()
            if dof != 0 or f.MalformedConstraints or f.ConflictingConstraints:
                problems.append('%s.%s solve=%s malformed=%s conflicting=%s'
                                % (body.Name, f.Name, dof, f.MalformedConstraints, f.ConflictingConstraints))
    s = body.Shape
    print('  %-6s valid=%s solids=%d  %.1f x %.1f x %.1f mm' % (
        body.Name, s.isValid(), len(s.Solids), s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength))

print('== 2. fit against the Rev 1.3 board')
bdoc = App.newDocument('board')
import Import
Import.insert(BOARD_STEP, bdoc.Name)
move = Placement(V(-BOARD_CX, -BOARD_CY, 0), Rotation())
root = max((o for o in bdoc.Objects if o.TypeId == 'App::Part' and o.Shape.Solids),
           key=lambda o: o.Shape.BoundBox.DiagonalLength)
parts = []
for o in root.Group:                # one App::Part per placed component
    if not hasattr(o, 'Shape') or not o.Shape.Solids:
        continue
    s = o.Shape.copy(); s.Placement = move.multiply(s.Placement)
    parts.append((o.Label, s))
pcb = [o for o in bdoc.Objects if o.TypeId == 'Part::Feature' and o.Label.endswith('_PCB')]
if pcb:
    s = pcb[0].Shape.copy(); s.Placement = move.multiply(s.Placement); parts.append(('PCB', s))
case = [b.Shape for b in bodies]
live = [(l, s) for l, s in parts if not l.startswith(DNP)]

# Spatial pre-filter. The case is a shell, so a part can only touch it if it
# reaches a wall, the floor features, the ceiling, or a screw post. Parts
# entirely inside the open cavity are skipped (booleans on all ~300 parts
# take the better part of an hour).
v = lambda k: float(sheet.get(k))
sheet = doc.getObject('Params')
iw = v('board_w') / 2 + v('board_gap'); il = v('board_l') / 2 + v('board_gap')
floor_feat = -v('standoff_h') - v('board_play') + max(v('din_boss_h'), v('kh_plate_t'))
ceiling = v('board_t') + v('headroom')
holes = [(v(a), v(b)) for a in ('hole_xl', 'hole_xr') for b in ('hole_yb', 'hole_yt')]
reach = v('standoff_d') / 2 + 1.5
M = 0.5
def candidate(s):
    b = s.BoundBox
    if b.XMin < -iw + M or b.XMax > iw - M or b.YMin < -il + M or b.YMax > il - M:
        return True
    if b.ZMin < floor_feat + M or b.ZMax > ceiling - M:
        return True
    return any(b.XMin - reach < hx < b.XMax + reach and b.YMin - reach < hy < b.YMax + reach for hx, hy in holes)
cands = [(l, s) for l, s in live if candidate(s)]
print('  %d of %d parts can reach the case; testing those' % (len(cands), len(live)))
hits = []
for b, cs in zip(bodies, case):
    for label, s in cands:
        if s.BoundBox.intersect(cs.BoundBox):
            com = cs.common(s)
            if com.Volume > 1e-3:
                bb = com.BoundBox
                hits.append('%s intersects %s by %.3f mm3 at x[%.2f,%.2f] y[%.2f,%.2f] z[%.2f,%.2f]'
                            % (label, b.Name, com.Volume, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
problems += hits
print('  interference:', 'none' if not hits else '\n    ' + '\n    '.join(hits))

watch = [(l, s) for l, s in cands
         if s.BoundBox.ZMax > 8 or s.BoundBox.ZMin < -1.0
         or l.startswith(('USB_Micro', 'D_0805', '1786918', '1790182', 'Barrel', 'PCB'))]
print('  closest approach (mm):')
dist = [(min(cs.distToShape(s)[0] for cs in case), l, s) for l, s in watch]
for c, l, s in sorted(dist, key=lambda t: t[0]):
    bb = s.BoundBox
    flag = '  <-- tight' if c < 0.2 else ''
    print('    %6.2f  %-40s x[%.1f,%.1f] y[%.1f,%.1f] z[%.2f,%.2f]%s'
          % (c, l[:40], bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, flag))

print('== 3. parameter robustness')
sheet = doc.getObject('Params')
trials = [{'board_l': 80.0}, {'wall': 3.0, 'edge_r': 1.5}, {'kh_dx': 12.0, 'tv_n': 7, 'sv_n': 5},
          {'headroom': 16.0, 'r_out': 4.0}]
original = {k: sheet.get(k) for t in trials for k in t}
for t in trials:
    for k, v in t.items():
        sheet.set(sheet.getCellFromAlias(k), str(v))
    doc.recompute()
    bad = [f.Name for b in bodies for f in b.Group if f.State and any(s in ('Invalid', 'Error') for s in f.State)]
    ok = all(b.Shape.isValid() and len(b.Shape.Solids) == 1 for b in bodies) and not bad
    print('  %-45s %s' % (t, 'ok' if ok else 'FAILED %s' % bad))
    if not ok:
        problems.append('robustness %s: %s' % (t, bad))
    for k, v in original.items():
        sheet.set(sheet.getCellFromAlias(k), str(v))
    doc.recompute()

print('== 4. exports')
os.makedirs(os.path.join(HERE, 'exports'), exist_ok=True)
for b in bodies:
    path = os.path.join(HERE, 'exports', 'project-case-rev3-%s.stl' % b.Name.lower())
    Mesh.export([b], path)
    print('  ', os.path.relpath(path, HERE))

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import numpy as np
    os.makedirs(os.path.join(HERE, 'renders'), exist_ok=True)
    light = np.array([0.4, -0.5, 0.8]); light /= np.linalg.norm(light)

    def render(items, name, elev, azim, title):
        fig = plt.figure(figsize=(9, 7), dpi=110)
        ax = fig.add_subplot(111, projection='3d')
        pts = []
        for shape, color, alpha in items:
            v, f = shape.tessellate(0.2)
            if not f:
                continue
            v = np.array([[p.x, p.y, p.z] for p in v]); tri = v[np.array(f)]
            n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
            shade = 0.35 + 0.65 * np.abs(n @ light)
            col = np.clip(np.array(matplotlib.colors.to_rgb(color))[None, :] * shade[:, None], 0, 1)
            ax.add_collection3d(Poly3DCollection(tri, facecolors=np.c_[col, np.full(len(col), alpha)], edgecolors='none'))
            pts.append(v)
        a = np.vstack(pts); c = (a.min(0) + a.max(0)) / 2; r = (a.max(0) - a.min(0)).max() / 2
        ax.set_xlim(c[0] - r, c[0] + r); ax.set_ylim(c[1] - r, c[1] + r); ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_box_aspect((1, 1, 1)); ax.view_init(elev=elev, azim=azim)
        ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z'); ax.set_title(title)
        plt.tight_layout(); fig.savefig(os.path.join(HERE, 'renders', name)); plt.close(fig)
        print('  ', 'renders/' + name)

    board = Part.makeCompound([s for l, s in parts if not l.startswith(DNP) and s.BoundBox.DiagonalLength > 2.5])
    bot, lid = case
    render([(lid, '#d8a07a', 1), (bot, '#7aa6d8', 1)], 'assembled-plusX.png', 15, 20, 'Rev 3 assembled, +X wall (terminal block, jack, D5)')
    render([(lid, '#d8a07a', 1), (bot, '#7aa6d8', 1)], 'assembled-minusX.png', 15, -160, 'Rev 3 assembled, -X wall (USB, D3/D4)')
    render([(bot, '#7aa6d8', 1), (board, '#3a8a4a', 1)], 'tray-with-board.png', 40, -60, 'Tray with Rev 1.3 board')
    render([(bot, '#7aa6d8', 1)], 'tray-inside.png', 60, -60, 'Tray, inside')
    render([(bot, '#7aa6d8', 1)], 'tray-underside.png', -89, -90, 'Tray underside (keyholes, DIN clip holes)')
    render([(lid, '#d8a07a', 1)], 'lid-underside.png', -50, -60, 'Lid from below (posts, groove)')
except ImportError as e:
    print('  renders skipped:', e)

print('== result:', 'PASS' if not problems else 'PROBLEMS')
for p in problems:
    print('  -', p)
