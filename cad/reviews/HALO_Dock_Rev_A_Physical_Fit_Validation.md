# HALO Dock Rev A — Physical Fit Validation

**Status:** Physical coupon decisions incorporated; native full-model validation pending
**Review date:** 2026-08-06

## Test record

The supplier reported a **Bambu Lab X2D** printer. The manufacturing package records **PETG** for the fit coupons, so PETG is retained as the test material. These results apply only to the tested coupons and do not replace a native Fusion 360 rebuild or full-assembly inspection.

## Accepted physical decisions

| Feature | Result | Rev A disposition |
|---|---|---|
| Tablet side clearance | 0.20 mm per side fits; 0.30 mm and 0.40 mm are too loose | Select parameter-driven 0.20 mm for the Faceplate pocket, DockBody, guides, shelf, and selected guide/shelf coupon. Preserve all three clearance gauges as test history. |
| Device corner radius | R8, R8.5, and R9 all fit | Select R8.5 as the balanced value. Preserve R8/R8.5/R9 coupon generators and identify R8.5 as selected. |
| Lower shelf lateral fit | Approximately 1 mm total clearance between the tablet and shelf ends | Accepted. Preserve shelf width and do not reduce lateral clearance. |
| Lower shelf robustness | Coupon broke only after falling onto the floor | Robustness observation, not a fit failure. Keep support height; use at least 3.0 mm hidden structure, joined support transitions, and generous hidden root fillets without enlarging visible front geometry. |
| USB-C alignment and width | Accepted; tested straight connector plugs fully with deliberate finger pressure and does not lift the tablet | Preserve horizontal alignment and pocket width; do not require a 90-degree cable. |
| USB-C freedom | Upward motion accepted; downward motion constrained; additional rear room needed | Add 0.30 mm usable relief below the connector and 0.20 mm rear/depth relief. Keep the shelf as the tablet support so the plug carries no tablet load. |

## Required follow-up

The source generator has been statically checked only. Fusion 360 was unavailable in this environment. A fresh empty Hybrid Design must still complete:

1. Native generator execution and full parametric timeline rebuild, including a +1 mm rebuild exercise.
2. Interference analysis for `TabletEnvelope`, Faceplate, DockBody, strengthened shelf roots, USB-C plug body, and cable bend envelope.
3. Confirmation that the tablet rests on the shelf and neither the plug nor cable transfers bending force into the tablet port.
4. Visual inspection of the minimal front edge, open top insertion/removal path, camera keep-out, button relief, and signed left/right placement.
5. Controlled F3D, component-scoped STEP, and STL generation followed by slicer inspection.

Until those checks pass, no generated F3D/STEP/STL is a manufacturing release.
