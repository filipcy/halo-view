# HALO wall mount V2 — design review package

V2 preserves the physically selected Rev A tablet envelope and sliding fit:
125 × 211 × 8 mm, R8.5 corners, 0.20 mm X/Y clearance and 0.30 mm depth
clearance per face. The old 18 mm enclosure stack is replaced by a 3 mm rear
skeleton directly against the wall. The 11 mm dimension is explicitly measured
from the wall-contact plane (Z=0) to the actual front surface of the 8 mm tablet
(Z=3+8), not to a clearance-envelope or printed-retainer face.

The top is open. A split 3 mm bottom shelf carries the tablet; 1.25 mm side lips
prevent forward release while leaving the Samsung bezel dominant. The right
button opening retains its 46 mm span and is moved from 146–192 mm to 124–170 mm
from the bottom datum: exactly 22 mm lower.

The 22 × 30 mm 90-degree USB-C pocket and 12 mm route are review envelopes, not
a released or production-approved cable fit. Both remain configurable and the
selected adapter, housing and bend radius must be measured before print release.
The route is an opening in the skeleton leading to a wall exit behind
the tablet, so it does not add to global projection.

The camera relief is on the physical **left when the SM-X130 is viewed from the
rear**. Because model X is defined while looking at the front, this is the +X
(right in front view) side. This intentionally fixes the mirrored Rev A relief.

The exposed upper and lower plan edges use a subtle 2 mm chamfer. It is confined
to the exterior outline: the tablet pocket, 0.20 mm side clearance, 1.25 mm
retainers and the Z=11 mm tablet-front plane are unchanged.

## Regenerate

```bash
python3 cad/source/HALO_Wall_Mount_V2.py
```

The command writes the review STL and eight SVG views here. The STL consists of
overlapping closed solids intended to be unioned by the slicer; a native Fusion
rebuild and interference check remain required before manufacturing.

## FDM orientation

Print with the broad rear skeleton on the build plate (wall face down). This
keeps the visible guide walls vertical and avoids supports in the tablet pocket.
Use 0.2 mm layers, at least four perimeters, and bridge the 1.25 mm retention
lips. A brim is preferable to sanding the visible sides.
