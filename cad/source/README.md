# HALO Dock Rev A source

`HALO_Dock_Rev_A.py` is a Fusion 360 Python generator for the portrait Samsung Galaxy Tab A11 SM-X130 dock. Run it from **Utilities → Add-Ins → Scripts and Add-Ins** in an open, empty Fusion Design.

The generator creates named user parameters and separate components so prototype assumptions remain editable. Values marked `Reserved` or `Keep-outs` document required interfaces but do not create Iteration 1 geometry.

## Iteration 1 scope

The model is intentionally limited to:

- `TabletEnvelope`, a non-manufacturing reference body;
- `Faceplate`, the visible front frame; and
- `DockBody`, the preliminary wall-side shell.

`WallInterface` and `Assembly` are named component placeholders. USB routing, the top latch, side guides, lower shelf, 3M Dual Lock fields, and final fillets/chamfers are explicitly deferred.

## Output

When generation completes inside Fusion 360, the export hook writes F3D, STEP, STL, and PNG deliverables to `~/Documents/HALO_Dock_Rev_A_Iteration_1/`. The hook creates the directory automatically and replaces existing files with the same names. Two print meshes are written, one each for the Faceplate and DockBody.

## Prototype printing assumption

- Print the **Faceplate front face down** on a clean, smooth build plate.
- Print the **DockBody wall-side face down**.
- Both parts are designed around an **FDM, no-support assumption** for the current simple planar geometry.
- The tablet envelope and placeholder components are not printable release parts.

This orientation/support guidance is provisional. No full-size print is released until physical fit, active-display overlap, cable envelope, retention, and mounting interfaces are validated.
