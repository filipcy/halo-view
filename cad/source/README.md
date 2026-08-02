# HALO Dock Rev A source

`HALO_Dock_Rev_A.py` is a Fusion 360 Python generator for the portrait Samsung Galaxy Tab A11 SM-X130 dock. Run it from **Utilities → Add-Ins → Scripts and Add-Ins** in an open, empty Fusion Design.

The generator creates named user parameters and separate components so prototype assumptions remain editable. Values marked `Reserved` or `Keep-outs` document interfaces that still do not create geometry.

## Sprint 3 external print candidate scope

The model now contains:

- `TabletEnvelope`, a non-manufacturing reference body;
- `Faceplate`, the visible front lip plus rear perimeter skirt; and
- `DockBody`, with its projection-controlled backing, paired side guides, lower support shelf, and explicitly non-final paired upper side-detent concept; and
- `WallInterface`, with two discrete hidden flat 3M Dual Lock mounting-field bodies inside, but not filling, the physical shadow gap.
- three compact U-channel fit coupons for 0.2, 0.3, and 0.4 mm clearance per tablet side;
- a representative Faceplate rounded corner/lip coupon;
- a side-guide + lower-shelf insertion coupon; and
- a wall-stack coupon with paired Dual Lock fields and the visible shadow gap.

`Assembly` remains a named placeholder. The portrait top has no crossbar and the guides stop below it, preserving a fully open insertion path. USB routing, a final latch, and final fillets/chamfers or cosmetic finishing are explicitly deferred.

The Faceplate component intentionally contains separate front-lip and rear-skirt solids. The lip preserves the 0.8 mm screen recess in front of the tablet display plane, while the skirt provides the remaining prototype structural depth only outside the tablet envelope.

The wall datum realizes `wall_shadow_gap` as a nominal 1.5 mm separation. Discrete pad fields use the separate 1.0 mm `dual_lock_engaged_thickness`, leaving visible open volume around them rather than turning the shadow gap into a solid slab. The generator checks `wall_shadow_gap + dock_back_thickness + device_thickness + screen_recess` against `total_projection_target`; current values produce 18.0 mm. New feature sizes and locations are user parameters or expressions derived from them, and nominal guide, shelf, and retention-concept boundaries remain outside `TabletEnvelope`.

## Output

When generation completes inside Fusion 360, the export hook writes F3D, assembly STEP, part-level STEP and STL, and PNG deliverables to `~/Documents/HALO_Dock_Rev_A_External_Print_Candidate/`. Every coupon and both full-size candidates receive matching STEP and STL outputs. Full-size filenames include `PRINT_CANDIDATE`; they are not production releases. See the [part manifest](../../manufacturing/HALO_Dock_Rev_A_External_Print_Candidate/PART_MANIFEST.md).

## Prototype printing assumption

- Print the **Faceplate front face down** on a clean, smooth build plate.
- Print the **DockBody wall-side face down**.
- Support-free printing is an **unverified prototype assumption** now that guides, shelf, and retention studies are present.
- The tablet envelope and placeholder components are not printable release parts.

This orientation/support guidance is provisional. No full-size print is released until physical fit, open insertion, active-display overlap, cable envelope, retention, mounting interface, shadow gap, and installed projection are validated. If Fusion 360 is unavailable, native execution, rebuild testing, interference checks, and generated exports remain unverified.

The vendor baseline is matte black PETG, 0.20 mm layer height, and no supports. Supplier scaling and automatic mesh repair are prohibited. Coupon-first ordering, RFQ questions, process records, and receiving checks are controlled by the [external print candidate manufacturing specification](../../manufacturing/HALO_Dock_Rev_A_External_Print_Candidate/README.md).
