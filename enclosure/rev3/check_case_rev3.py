"""Check project-case-rev3.FCStd against the Rev 1.3 board, then export.

Run headless (FreeCAD 1.1):
    freecadcmd enclosure/rev3/check_case_rev3.py

Reads the model as it is now, including any spreadsheet edits, so run it
after changing parameters. It:
  1. recomputes, and reports any feature that errors or changes no material,
     a body whose Tip isn't its last feature, a blocked vent slot, an open
     keyhole, and a marking that runs off the flat face or into a vent
  2. checks the case for interference with every board part, and lists the
     closest approach for the parts that matter (connectors, tall and
     underside parts)
  3. re-solves with deliberately changed parameters to prove the model
     survives edits (in memory; the file is not modified)
  4. exports STLs (tray, lid, and the lid's two inlays) to exports/ and
     preview PNGs to renders/
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
prints = [doc.getObject('TrayPrint'), doc.getObject('LidPrint')]     # bodies minus markings
inlays = [doc.getObject('InlayBrand'), doc.getObject('InlayLabels')]

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
    solid = [f for f in body.Group if f.TypeId.startswith('PartDesign::') and f.TypeId != 'PartDesign::Body']
    if body.Tip != solid[-1]:
        problems.append('%s Tip is %s, not the last feature %s: the body stops early'
                        % (body.Name, body.Tip.Name, solid[-1].Name))
    s = body.Shape
    print('  %-6s valid=%s solids=%d  %.1f x %.1f x %.1f mm' % (
        body.Name, s.isValid(), len(s.Solids), s.BoundBox.XLength, s.BoundBox.YLength, s.BoundBox.ZLength))


def keyholes_closed():
    """Probe each keyhole (entry hole and slot) with a vertical line: open from
    below, closed by the cap from inside. Returns (problems, head channel height)."""
    g = lambda k: float(doc.getObject('Params').get(k))
    bad, gap = [], None
    for kx in (-g('kh_dx'), g('kh_dx')):
        for y in (g('kh_y'), g('kh_y') + g('kh_slot_len') - g('kh_slot_w') / 2):
            line = Part.makeLine(V(kx, y, -20), V(kx, y, 0))
            segs = sorted((e.BoundBox.ZMin, e.BoundBox.ZMax) for e in prints[0].Shape.common(line).Edges)
            if len(segs) != 1:
                bad.append('keyhole at x=%.1f y=%.1f: solid above it %s (want one cap)' % (kx, y, segs))
            else:
                ch = -g('standoff_h') - g('board_play') - g('kh_recess')
                gap = segs[0][0] - ch
    return bad, gap

def vents_open():
    """Probe the centre of every vent slot with a line through the lid wall or
    top; each must pass clean through. Returns the list of blocked slots."""
    g = lambda k: float(doc.getObject('Params').get(k))
    lid = prints[1].Shape
    ow = g('board_w') / 2 + g('board_gap') + g('wall'); ol = g('board_l') / 2 + g('board_gap') + g('wall')
    zc = g('board_t') + g('headroom')
    probes = []
    for y0, n in ((g('tv_y0'), g('tv_n')), (g('tvb_y0'), g('tvb_n'))):
        for i in range(int(n)):
            x, y = g('tv_x0') + g('tv_len') / 2, y0 + i * g('tv_pitch')
            probes.append(('top y=%.1f' % y, V(x, y, zc - 1), V(x, y, zc + g('lid_t') + 1)))
    svz = g('board_t') + g('sv_z0') + g('sv_len') / 2
    for i in range(int(g('sv_n'))):
        for side, x0 in ((1, g('svp_x0')), (-1, g('svm_x0'))):
            x = x0 + i * g('sv_pitch')
            probes.append(('%sY x=%.1f' % ('+' if side > 0 else '-', x),
                           V(x, side * (ol - g('wall') - 0.5), svz), V(x, side * (ol + 1), svz)))
    return [n for n, a, b in probes if lid.common(Part.makeLine(a, b)).Edges], len(probes)

def marks_whole():
    """Every mark must sit entirely in solid material, mark_d deep: an inlay
    that runs into a vent, off the flat face onto the edge fillet, or past the
    wall comes out smaller than the mark's own area x depth."""
    md = float(doc.getObject('Params').get('mark_d'))
    bad = []
    for grp, body in (('MarksBrand', bodies[1]), ('MarksLabels', bodies[1]), ('MarksUnder', bodies[0])):
        for m in doc.getObject(grp).Links:
            if abs(m.Shape.BoundBox.ZLength - (md + 0.5)) > 1e-3:
                bad.append('%s depth is stale: re-run build_case_rev3.py after changing mark_d' % m.Name)
                continue
            want = m.Shape.Volume * md / (md + 0.5)
            got = body.Shape.common(m.Shape).Volume
            if abs(got - want) > 0.005 * want:
                bad.append('%s is only %.1f%% inside solid material' % (m.Name, 100 * got / want))
    return bad

mb = marks_whole()
problems += mb
print('  markings whole and on flat faces: %s' % ('yes' if not mb else 'NO'))
print('  inlays: brand %.0f mm3 (%d pieces), labels %.0f mm3 (%d pieces)'
      % (inlays[0].Shape.Volume, len(inlays[0].Shape.Solids), inlays[1].Shape.Volume, len(inlays[1].Shape.Solids)))

vb, vn = vents_open()
problems += ['vent slot blocked: ' + n for n in vb]
print('  vent slots open: %d of %d' % (vn - len(vb), vn))

kb, kgap = keyholes_closed()
problems += kb
print('  keyholes closed from inside: %s, head channel %.2f mm tall'
      % ('yes' if not kb else 'NO', kgap or 0))

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
case = [b.Shape for b in prints]
live = [(l, s) for l, s in parts if not l.startswith(DNP)]

# Spatial pre-filter. The case is a shell, so a part can only touch it if it
# reaches a wall, the floor features, the ceiling, or a screw post. Parts
# entirely inside the open cavity are skipped (booleans on all ~300 parts
# take the better part of an hour).
v = lambda k: float(sheet.get(k))
sheet = doc.getObject('Params')
iw = v('board_w') / 2 + v('board_gap'); il = v('board_l') / 2 + v('board_gap')
floor_feat = -v('standoff_h') - v('board_play') + max(v('din_boss_h'), v('kh_plate_t') + v('kh_cap_t'))
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
for b, cs in zip(prints, case):
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
          {'headroom': 16.0, 'r_out': 4.0}, {'din_spacing': 36.0, 'side_cy': 3.0}]
original = {k: sheet.get(k) for t in trials for k in t}
for t in trials:
    for k, v in t.items():
        sheet.set(sheet.getCellFromAlias(k), str(v))
    doc.recompute()
    bad = [f.Name for b in bodies for f in b.Group if f.State and any(s in ('Invalid', 'Error') for s in f.State)]
    bad += keyholes_closed()[0]
    bad += ['vent ' + n for n in vents_open()[0]]
    bad += marks_whole()
    ok = all(b.Shape.isValid() and len(b.Shape.Solids) == 1 for b in prints) and not bad
    print('  %-45s %s' % (t, 'ok' if ok else 'FAILED %s' % bad))
    if not ok:
        problems.append('robustness %s: %s' % (t, bad))
    for k, v in original.items():
        sheet.set(sheet.getCellFromAlias(k), str(v))
    doc.recompute()

print('== 4. exports')
os.makedirs(os.path.join(HERE, 'exports'), exist_ok=True)
for o, name in zip(prints + inlays, ('bottom', 'lid', 'lid-inlay-brand', 'lid-inlay-labels')):
    path = os.path.join(HERE, 'exports', 'project-case-rev3-%s.stl' % name)
    Mesh.export([o], path)
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
    render([(lid, '#d8a07a', 1), (bot, '#7aa6d8', 1)], 'side-mount-minusX.png', 5, 180, 'Side mount face (-X): DIN clip holes above USB / LEDs')
    render([(bot, '#7aa6d8', 1)], 'tray-underside.png', -89, -90, 'Tray underside (keyholes, DIN clip holes)')
    render([(lid, '#d8a07a', 1)], 'lid-underside.png', -50, -60, 'Lid from below (posts, groove)')

    from matplotlib.collections import PolyCollection

    def face_on(items, name, title, mirror=False):
        """Flat view of one outer face: faces pointing at the viewer (n.z
        sign `nz`) within a z band, drawn in the order given."""
        fig, ax = plt.subplots(figsize=(8, 9), dpi=110); ax.set_facecolor('#c8d4c0')
        for shape, nz, zlo, zhi, color in items:
            v, f = shape.tessellate(0.05)
            v = np.array([[p.x, p.y, p.z] for p in v]); tri = v[np.array(f)]
            n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
            zc = tri[:, :, 2].mean(1)
            tri = tri[(n[:, 2] * nz > 0) & (zc > zlo) & (zc < zhi)][:, :, :2]
            if mirror:
                tri[:, :, 0] *= -1
            ax.add_collection(PolyCollection(tri, facecolor=color, edgecolor=color, linewidth=0.2))
        b = lid.BoundBox
        ax.set_xlim(b.XMin - 1, b.XMax + 1); ax.set_ylim(b.YMin - 1, b.YMax + 1)
        ax.set_aspect('equal'); ax.set_title(title)
        plt.tight_layout(); fig.savefig(os.path.join(HERE, 'renders', name)); plt.close(fig)
        print('  ', 'renders/' + name)

    zt, zb = lid.BoundBox.ZMax, bot.BoundBox.ZMin
    md = float(sheet.get('mark_d'))
    face_on([(lid, 1, zt - md - 0.1, zt + 1, '#1a1a1a'),
             (inlays[0].Shape, 1, zt - 0.01, zt + 1, '#2f6fd0'),
             (inlays[1].Shape, 1, zt - 0.01, zt + 1, '#f4f4f4')],
            'lid-top-markings.png', 'Lid top from outside, +Y up (case black, brand blue, labels white)')
    face_on([(bot, -1, zb - 1, zb + 0.05, '#1a1a1a'), (bot, -1, zb + md - 0.05, zb + md + 0.05, '#9a9a9a')],
            'tray-underside-markings.png', 'Tray underside from outside, +Y up (debossed in grey)', mirror=True)
except ImportError as e:
    print('  renders skipped:', e)

print('== result:', 'PASS' if not problems else 'PROBLEMS')
for p in problems:
    print('  -', p)
