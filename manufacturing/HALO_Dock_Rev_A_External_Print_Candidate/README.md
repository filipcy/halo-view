# HALO Dock Rev A — external print candidate manufacturing specification

**Package:** Sprint 3 external print candidate  
**Disposition:** coupon-first quotation and fit study; **not a production release**  
**Units:** millimetres

## Supplier baseline

| Requirement | Baseline |
|---|---|
| Process | FFF/FDM |
| Material | PETG |
| Colour/finish | Matte black; uniform commercial print finish |
| Layer height | 0.20 mm |
| Supports | None permitted |
| Quantity | One of each coupon initially; full-size parts only after written coupon approval |
| Dimensional source | Supplied STEP is authoritative; STL is the print mesh companion |

The supplier **must print at exactly 100% scale**. Scaling, shrink compensation applied by changing model scale, unit conversion by assumption, and build-volume “fit” scaling are prohibited. The supplier must not run automatic mesh repair, healing, remeshing, wall thickening, hole closing, or geometry simplification. If a file is rejected by preflight, stop and report the filename and error; do not alter it.

## Coupon-first sequence

1. Quote and print the three per-side clearance coupons: 0.2 mm, 0.3 mm, and 0.4 mm.
2. Print the representative Faceplate corner/lip section to review the visible corner, lip overlap, layer quality, and front-face finish.
3. Print the side-guide + lower-shelf section to test tablet insertion, shelf seating, guide stiffness, and support-free orientation.
4. Print the wall-stack coupon to review the two flat Dual Lock mounting fields and visible 1.5 mm shadow-gap concept.
5. Ship coupons for receiving inspection. Do not start the full-size Faceplate or DockBody without written purchaser authorization identifying the accepted coupon result.

## Full-size print candidates

The full-size `Faceplate_PRINT_CANDIDATE` and `DockBody_PRINT_CANDIDATE` files are **PRINT CANDIDATE ONLY**. They are included for quotation and manufacturability review, not as authorization to manufacture. They are not production-released, and neither may be substituted for a coupon-first approval.

Provisional orientation is Faceplate front face down and DockBody wall-side face down. The supplier must propose any orientation change before slicing and show that it remains support-free. Do not add support-contact scars to visible or tablet-contact faces.

## Process controls and reporting

- Use one identified matte-black PETG material lot for the coupon set; report manufacturer, product, colour, and lot/batch when available.
- Use 0.20 mm layers and no supports. Record nozzle diameter, perimeter count, top/bottom layers, infill type/percentage, temperatures, cooling, orientation, slicer name/version, and machine model.
- Do not sand, vapor smooth, fill, coat, dye, tumble, or heat-form unless separately authorized.
- Remove only normal brim/skirt material without changing functional edges.
- Preserve part labels and filenames in quote, traveller, packing list, and inspection report.
- Bag parts separately to prevent scratching; identify any warp, stringing, void, delamination, contamination, or handling damage.

## Design and validation limitations

Fusion 360 was unavailable when this package source was prepared. Native execution, parametric rebuild testing, interference checks, and generated F3D/STEP/STL/PNG exports remain unverified. Generated files must therefore receive purchaser-side Fusion review and checksum-controlled release before transmission to a supplier. Supplier preflight is not design validation and must not be represented as such.
