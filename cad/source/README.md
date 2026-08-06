# HALO Dock Rev A source

`HALO_Dock_Rev_A.py` is the native Fusion 360 parametric source generator. Sprint 3 retains accepted Iteration 2 full-part geometry and adds test coupons, measured Dual Lock recess logic, and gated exports. Static Python checks are not native CAD validation.

## Native validation setup and rerun safety

Every validation run must start in a **fresh, empty Hybrid Design** document. The generator creates multiple internal components, which Fusion does not permit in a Part Design document. If Fusion reports that Part Design documents can contain only one component, open or convert the document to Hybrid Design and begin again in a fresh empty document.

A failed run can leave partial generated components behind. The generator is not transactional and deliberately does not delete existing components, because they may be unrelated user work. Do not rerun it in the document left by a failed validation; discard that document and repeat the validation in another fresh empty Hybrid Design.

## Export modes

`EXPORT_MODE` defaults to `COUPONS_ONLY` and writes controlled STEP + STL pairs for coupon parts to `~/Documents/HALO_Dock_Rev_A/coupons/`. It never exports full Faceplate/DockBody meshes or assembly F3D/STEP/PNG. The 0.2/0.3/0.4 mm clearance gauges, open L corner/lip coupon, and full-pocket-width guide/shelf coupon are included. The separately named left and right single-field wall articles are included only after a valid physical Dual Lock measurement; no STL contains loose wall-coupon bodies.

`FULL_SIZE_PRINT_CANDIDATE` writes to `~/Documents/HALO_Dock_Rev_A/print-candidate/`, but only after the measured wall stack and every explicit evidence flag passes. Flags cover native execution, +1 mm rebuild, interference checks, coupon approval, clearance selection, slicer review, and written authorization. Full parts remain `PRINT CANDIDATE ONLY`. Full mode emits separate component-scoped STEP + STL pairs for Faceplate and DockBody; it never exports the contaminated design root.

## Measurement blocker

`dual_lock_engaged_thickness` defaults to `0 mm`, meaning **NOT MEASURED**. It is labeled `REQUIRED PHYSICAL MEASUREMENT — exact selected Dual Lock pair`. Do not substitute a catalog claim or estimate. The wall coupon and all full-size exports remain blocked until the exact selected, mated pair is measured and the derived recess leaves positive structural backing.

Follow `cad/reviews/HALO_Dock_Rev_A_Sprint_3.md`. No Fusion execution, export, slicer review, or physical validation was performed in this repository environment.

## Physical fit selection

The current source-of-truth values are the physically selected 0.20 mm nominal per-side clearance and R8.5 device corner radius. The 0.20/0.30/0.40 clearance gauges and R8/R8.5/R9 corner coupons remain available; their presence does not make rejected alternatives active geometry. The full DockBody uses explicit `usb_pocket_vertical_relief_delta = 0.30 mm` and `usb_pocket_depth_relief_delta = 0.20 mm`, preserving tested straight-cable alignment and width. The accepted shelf width and support height are unchanged; hidden structure is at least 3.0 mm and receives root fillets.

See the [physical fit validation review](../reviews/HALO_Dock_Rev_A_Physical_Fit_Validation.md). Fusion native execution, timeline rebuild, interference analysis, F3D/STEP/STL generation, and visual inspection remain unverified and are release blockers.
