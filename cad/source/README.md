# HALO Dock Rev A source

`HALO_Dock_Rev_A.py` is the native Fusion 360 parametric source generator. Sprint 3 retains accepted Iteration 2 full-part geometry and adds test coupons, measured Dual Lock recess logic, and gated exports. Static Python checks are not native CAD validation.

## Export modes

`EXPORT_MODE` defaults to `COUPONS_ONLY` and writes controlled STEP + STL pairs for coupon parts to `~/Documents/HALO_Dock_Rev_A/coupons/`. It never exports full Faceplate/DockBody meshes or assembly F3D/STEP/PNG. The 0.2/0.3/0.4 mm clearance gauges, open L corner/lip coupon, and full-pocket-width guide/shelf coupon are included. The separately named left and right single-field wall articles are included only after a valid physical Dual Lock measurement; no STL contains loose wall-coupon bodies.

`FULL_SIZE_PRINT_CANDIDATE` writes to `~/Documents/HALO_Dock_Rev_A/print-candidate/`, but only after the measured wall stack and every explicit evidence flag passes. Flags cover native execution, +1 mm rebuild, interference checks, coupon approval, clearance selection, slicer review, and written authorization. Full parts remain `PRINT CANDIDATE ONLY`. Full mode emits separate component-scoped STEP + STL pairs for Faceplate and DockBody; it never exports the contaminated design root.

## Measurement blocker

`dual_lock_measured_engaged_thickness` defaults to `0 mm`, meaning **NOT MEASURED**. It is labeled `REQUIRED PHYSICAL MEASUREMENT — exact selected Dual Lock pair`. Do not substitute a catalog claim or estimate. The wall coupon and all full-size exports remain blocked until the exact selected, mated pair is measured and the derived recess leaves positive structural backing.

Follow `cad/reviews/HALO_Dock_Rev_A_Sprint_3.md`. No Fusion execution, export, slicer review, or physical validation was performed in this repository environment.
