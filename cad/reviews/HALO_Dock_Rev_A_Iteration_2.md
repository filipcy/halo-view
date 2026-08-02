# HALO Dock Rev A — Iteration 2 review

**Date:** 2026-08-01  
**Status:** Parametric mechanical layout review; not a print release  
**Device:** Samsung Galaxy Tab A11 SM-X130, portrait

## Review intent

Iteration 2 turns the accepted Iteration 1 package into a parameter-driven mechanical fit study. It adds paired side guides, a lower support shelf, a deliberately non-final upper side-detent concept, and two hidden flat 3M Dual Lock mounting fields. The portrait top edge has no crossbar or overhanging feature, so the top insertion path remains fully open.

## Generated geometry

| Component | Iteration 2 content | Manufacturing status |
|---|---|---|
| `TabletEnvelope` | 125 × 211 × 8 mm rounded reference envelope | Reference only; measurements require validation |
| `Faceplate` | Existing split front lip and rear perimeter skirt | Fit/visual study only |
| `DockBody` | Projection-controlled backing, paired side guides, lower shelf, and paired upper side-detent studies | Mechanical layout only |
| `WallInterface` | Two discrete 25 × 50 mm flat fields with provisional 1.0 mm engaged thickness inside the 1.5 mm wall separation | Mounting concept only; 3M stack/specification unvalidated |
| `Assembly` | Named placeholder | Joints and service motion deferred |

Every new size and location is controlled by a named Fusion user parameter or an expression derived from one. Side guides start outside `device_width / 2 + pocket_clearance_x`; the shelf starts below `-device_height / 2 - pocket_clearance_y`; and the side detent concept occupies only the side-clearance band. These construction rules prevent new solid geometry from entering `TabletEnvelope` at nominal values.

## Open insertion and retention concept

The two guides terminate below the tablet's top edge, and no geometry spans between them. The tablet therefore retains a fully open, straight top insertion path. The small paired features near the upper sides are named **NOT FINAL** in the Fusion timeline and bodies. They record only a possible side-detent location; they are not a released latch, do not close the top, and require insertion-force, tolerance, wear, and accessibility studies.

## Wall stack, shadow gap, and projection check

The wall datum is modeled at `-dock_back_thickness - wall_shadow_gap`. The discrete mounting-field bodies start on that plane and use the separate `dual_lock_engaged_thickness` parameter, provisionally 1.0 mm. They intentionally do not fill the 1.5 mm separation: open shadow-gap volume remains around the two pad fields and between their forward faces and the DockBody datum. This makes the wall stack reviewable without representing the entire shadow gap as solid mounting material.

The nominal installed projection is checked by the generator before body creation:

`wall_shadow_gap + dock_back_thickness + device_thickness + screen_recess`

With the current parameter expressions this is `1.5 + 7.7 + 8.0 + 0.8 = 18.0 mm`. `dock_back_thickness` is derived from `total_projection_target`, so changes to the target or other stack elements rebuild the rear depth. This is a packaging check, not an installed-product measurement.

## Explicitly out of scope

Iteration 2 does **not** include:

- USB-C routing, connector/service volume, or cable exit geometry;
- a final latch, spring selection, snap validation, or assembly motion;
- final fillets, chamfers, texture, edge breaks, or cosmetic finishing;
- camera, speaker, microphone, or button relief geometry;
- a released 3M Dual Lock part number, adhesive stack, installation template, or load rating.

## Review and release gates

1. Native Fusion 360 execution, parametric rebuild, body-to-body interference inspection, and generated F3D/STEP/STL/PNG exports must pass before physical release.
2. Verify TabletEnvelope dimensions and corner radius by caliper and coupon, then inspect guide, shelf, and detent clearance across tolerance extremes.
3. Demonstrate an unobstructed top insertion sweep in Fusion and with a physical fit article.
4. Confirm the actual wall, Dual Lock product, engaged thickness, field size, edge offsets, installation load, and removal access.
5. Measure installed wall-to-front projection; the CAD target is 18.0 mm, but the approximately 18 mm requirement remains unverified physically.
6. Develop USB routing and final retention in later iterations without consuming TabletEnvelope or the open insertion path.

## Environment verification status

Fusion 360 is unavailable in the development environment used for this change. Native execution, rebuild testing, interference checks, and generated exports therefore remain **unverified**. Static Python compilation and repository text checks do not replace these release gates.

**Decision:** Accept for Iteration 2 CAD review only. Do not release, install, or merge on the strength of static checks alone.
