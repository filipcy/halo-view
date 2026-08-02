# HALO Dock Rev A source

`HALO_Dock_Rev_A.py` is a Fusion 360 Python generator for the portrait Samsung Galaxy Tab A11 SM-X130 dock. Run it from **Utilities → Add-Ins → Scripts and Add-Ins** in an open, empty Fusion Design.

The generator creates named user parameters and separate components so prototype assumptions remain editable. Values marked `Reserved` or `Keep-outs` document interfaces that still do not create geometry.

## Iteration 2 scope

The model now contains:

- `TabletEnvelope`, a non-manufacturing reference body;
- `Faceplate`, the visible front lip plus rear perimeter skirt; and
- `DockBody`, with its projection-controlled backing, paired side guides, lower support shelf, and explicitly non-final paired upper side-detent concept; and
- `WallInterface`, with two hidden flat 3M Dual Lock mounting-field bodies spanning the physical shadow gap.

`Assembly` remains a named placeholder. The portrait top has no crossbar and the guides stop below it, preserving a fully open insertion path. USB routing, a final latch, and final fillets/chamfers or cosmetic finishing are explicitly deferred.

The Faceplate component intentionally contains separate front-lip and rear-skirt solids. The lip preserves the 0.8 mm screen recess in front of the tablet display plane, while the skirt provides the remaining prototype structural depth only outside the tablet envelope.

The wall datum and flat mounting fields realize `wall_shadow_gap` as a nominal 1.5 mm separation. The generator checks `wall_shadow_gap + dock_back_thickness + device_thickness + screen_recess` against `total_projection_target`; current values produce 18.0 mm. New feature sizes and locations are user parameters or expressions derived from them, and nominal guide, shelf, and retention-concept boundaries remain outside `TabletEnvelope`.

## Output

When generation completes inside Fusion 360, the export hook writes F3D, STEP, STL, and PNG deliverables to `~/Documents/HALO_Dock_Rev_A_Iteration_2/`. The hook creates the directory automatically and replaces existing files with the same names. Two print meshes are written, one each for the Faceplate and DockBody. WallInterface mounting fields remain review geometry in the assembly export rather than a released print mesh.

## Prototype printing assumption

- Print the **Faceplate front face down** on a clean, smooth build plate.
- Print the **DockBody wall-side face down**.
- Support-free printing is an **unverified prototype assumption** now that guides, shelf, and retention studies are present.
- The tablet envelope and placeholder components are not printable release parts.

This orientation/support guidance is provisional. No full-size print is released until physical fit, open insertion, active-display overlap, cable envelope, retention, mounting interface, shadow gap, and installed projection are validated. If Fusion 360 is unavailable, native execution, rebuild testing, interference checks, and generated exports remain unverified.
