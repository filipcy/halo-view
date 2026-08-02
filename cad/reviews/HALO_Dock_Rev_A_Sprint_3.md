# HALO Dock Rev A — Sprint 3 CAD review checklist

**Status: source ready for native validation; no generated artifact or print release**

## Coupon review

- The guide/shelf coupon has an inner rail spacing of `device_width + 2 × coupon_guide_clearance`; at current temporary device input and selected 0.3 mm clearance that expression evaluates nominally to 125.6 mm. This is an unevaluated CAD input, not an inspected print dimension. Its joined 30 mm rails are open at the top and overlap a connected shelf whose seating area spans the whole pocket, allowing the real tablet to descend vertically and fully seat.
- `Coupon_Faceplate_Open_Corner_L` uses a single open L profile, with top and side arms joined by concentric outer and inner arcs. The outer arc is `device_corner_radius + bezel_width`; each inner arc is derived from its lip/skirt band so neither layer has a square corner that can collide with the real tablet. It includes separate visible lip and rear-skirt layers. There is no nested profile or closed ring around the device; the tablet extends freely beyond both arm ends.
- Clearance coupons are connected U-shaped process/slot gauges at 0.2, 0.3, and 0.4 mm per side; their rails overlap and join a parametric base rather than exporting as loose bodies.
- The wall coupon is omitted while `dual_lock_measured_engaged_thickness == 0 mm`. **BLOCKED — exact Dual Lock pair must be selected and measured before print release.**

## Dual Lock section intent

`wall_shadow_gap` remains the visible 1.5 mm perimeter gap. Once an exact mated pair is measured, `dual_lock_recess_depth = dual_lock_measured_engaged_thickness - wall_shadow_gap`. Two symmetric, discrete rear pockets receive any measured excess; each real pad stack terminates on its pocket floor, forming wall → Dual Lock → DockBody contact. The generator rejects negative recess, through-depth recess, asymmetric fields, and non-positive remaining backing. Open space remains around and between fields; there is no printable full-area spacer.

The generator preserves a non-zero `dual_lock_measured_engaged_thickness` already entered in Fusion when rerun; it must not reset physical evidence to the source default. A measured thickness exactly equal to the shadow gap is valid and produces a zero-depth recess without asking Fusion to create an invalid zero-distance cut.

## Mandatory native Fusion 360 and slicer checklist

1. Open an empty **parametric** Fusion Design.
2. Run the generator with `EXPORT_MODE = COUPONS_ONLY`.
3. Confirm there are no exceptions; record the Fusion version and run log.
4. Inspect every named parameter and identify measured, verified, temporary, and placeholder values.
5. Change `device_width` from 125 to 126 mm and `device_height` from 211 to 212 mm.
6. Rebuild and record the result.
7. Verify left/right symmetry for side guides, retention, fit rails, guide-coupon rails, Dual Lock fields, and wall-coupon fields.
8. Restore 125 × 211 mm and rebuild.
9. Run interference/path checks: TabletEnvelope vs Faceplate; TabletEnvelope vs DockBody; vertical tablet insertion path; Dual Lock recess vs DockBody.
10. Capture section views of Faceplate lip, guide + shelf, and wall stack.
11. Export coupons (the wall coupon only after entering the physical measurement).
12. Open every STL in the intended slicer at exactly 100% scale.
13. Check and record bounding dimensions, orientation, thin walls, supports, manifold geometry, and build volume.
14. Save screenshots, logs, slicer project/version, file hashes, and pass/fail results.
15. Only after coupon manufacture and written approval consider `FULL_SIZE_PRINT_CANDIDATE`; separately satisfy every in-source gate and obtain written authorization.

Fusion 360 and a slicer are unavailable in this development environment. Native execution, rebuild, interference/path analysis, actual export, mesh inspection, and physical testing have **not** been performed.
