"""Lid-top proof print: the top 1.2 mm of the real lid with all its inlays,
about 8 g of PETG, to check the markings before printing a whole lid.

History (README, "Inlay test tile"): tile v1 settled mark_d = 0.6; tile v2
measured the printer (0.6 mm lines and 0.5 mm gaps print clean) and led to
the monoline lettering and 1.4x icons. Its script is in git history as
build_test_tile.py. This proof slices the model instead, so it is always
exactly the lid's current layout.

Run headless (FreeCAD 1.1), after check_case_rev3.py passes:
    freecadcmd enclosure/rev3/build_lid_proof.py

Reads project-case-rev3.FCStd; writes exports/lid-proof-{base,blue,white}.stl
and renders/lid-proof.png. Print it like the lid: one object, three parts,
marked face down, Elephant foot compensation 0, Arachne walls.
"""
import os
import sys

import FreeCAD as App
import MeshPart
import Part
from FreeCAD import Vector as V

HERE = os.path.dirname(os.path.abspath(
    globals().get('__file__') or os.environ.get('CASE_SCRIPT') or sys.argv[-1]))
PROOF_T = 1.2                       # thickness from the lid's top face

doc = App.openDocument(os.path.join(HERE, 'project-case-rev3.FCStd'))
doc.recompute()
lid = doc.getObject('LidPrint').Shape
zt = lid.BoundBox.ZMax
b = lid.BoundBox
slab = Part.makeBox(b.XLength + 2, b.YLength + 2, PROOF_T, V(b.XMin - 1, b.YMin - 1, zt - PROOF_T))
parts = {'base': lid.common(slab).removeSplitter(),
         'blue': doc.getObject('InlayBrand').Shape.common(slab),
         'white': doc.getObject('InlayLabels').Shape.common(slab)}

problems = []
for n, s in parts.items():
    print('%-6s valid=%s solids=%d volume=%.0f mm3' % (n, s.isValid(), len(s.Solids), s.Volume))
    if not s.isValid():
        problems.append(n + ' invalid')
if len(parts['base'].Solids) != 1:
    problems.append('base is %d solids' % len(parts['base'].Solids))
for n in ('InlayBrand', 'InlayLabels'):           # the inlays must be whole in the slice
    full = doc.getObject(n).Shape.Volume
    got = parts['blue' if n == 'InlayBrand' else 'white'].Volume
    if abs(full - got) > 0.001 * full:
        problems.append('%s is cut by the slice (%.0f of %.0f mm3)' % (n, got, full))
print('PETG weight about %.1f g (1.27 g/cm3, 100%% infill)'
      % (sum(s.Volume for s in parts.values()) / 1000 * 1.27))

os.makedirs(os.path.join(HERE, 'exports'), exist_ok=True)
for n, s in parts.items():
    path = os.path.join(HERE, 'exports', 'lid-proof-%s.stl' % n)
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
    fig, ax = plt.subplots(figsize=(8, 9), dpi=130); ax.set_facecolor('#c8d4c0')
    for s, color in ((parts['base'], '#1a1a1a'), (parts['blue'], '#01c7fc'), (parts['white'], '#f4f4f4')):
        v, f = s.tessellate(0.02)
        v = np.array([[p.x, p.y, p.z] for p in v]); tri = v[np.array(f)]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        tri = tri[(n[:, 2] > 0) & (tri[:, :, 2].mean(1) > zt - 0.01)][:, :, :2]
        ax.add_collection(PolyCollection(tri, facecolor=color, edgecolor=color, linewidth=0.2))
    ax.set_xlim(b.XMin - 1, b.XMax + 1); ax.set_ylim(b.YMin - 1, b.YMax + 1)
    ax.set_aspect('equal')
    ax.set_title('Lid-top proof, marked face (black PETG, Digital Blue #01C7FC, white)')
    plt.tight_layout()
    os.makedirs(os.path.join(HERE, 'renders'), exist_ok=True)
    fig.savefig(os.path.join(HERE, 'renders', 'lid-proof.png')); plt.close(fig)
    print('   renders/lid-proof.png')
except ImportError as e:
    print('  render skipped:', e)

print('RESULT:', 'PASS' if not problems else 'FAIL')
for p in problems:
    print('  -', p)
