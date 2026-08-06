# HALO Dock Rev A — physical fit validation correction

**Date:** 2026-08-06

**Status:** Fit selections recorded; full-size release remains gated

## Accepted observations

- The physical clearance series selects 0.20 mm per side for the tablet pocket in X and Y. All 0.2, 0.3, and 0.4 mm coupon definitions and manufacturing records remain available.
- The physical corner series selects an 8.5 mm device corner radius. R8, R8.5, and R9 coupons remain available as traceable validation articles.
- The accepted lower-shelf width (`device_width + 2 * pocket_clearance_x`), top datum, and 3.0 mm functional height are preserved. The 3.0 mm hidden structural-thickness parameter drives joined internal gussets contained entirely within the existing shelf/guide overlap and DockBody outline.
- Connector fit requires 0.30 mm additional downward relief and 0.20 mm additional rear/depth relief. The edge-based horizontal centre and 18 mm pocket width are unchanged.

## Load path and cable constraint

The tablet must seat on the continuous lower shelf around the connector opening. Verify a visible/feeler clearance between the seated tablet and the straight USB-C connector body so the connector carries no tablet load. A 90-degree connector is neither required nor the design basis.

## Physical revalidation checklist

1. Reprint the selected 0.20 mm and R8.5 articles alongside retained comparison coupons; confirm free insertion without clamp or corner rocking.
2. Seat the tablet on the lower shelf and confirm the shelf, not the connector, establishes the vertical datum.
3. Connect the selected straight USB-C cable and inspect the added downward and rear clearance, bend freedom, and absence of housing contact.
4. Confirm the camera keep-out, right button relief, lower speaker opening, USB-C horizontal alignment, and USB-C pocket width against the source parameters.
5. Record native Fusion rebuild, interference review, paired STEP/STL checksums, slicer orientation, and photographs before any authorization.

Coupon approval does not authorize full-size manufacture. Dual Lock measurement, native timeline health, export verification, and every existing release gate remain open until separately signed off.
