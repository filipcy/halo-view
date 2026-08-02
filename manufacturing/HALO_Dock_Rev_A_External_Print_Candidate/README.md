# HALO Dock Rev A — external print-candidate package

**Release state: NOT READY FOR EXTERNAL PRINT. Full-size printing is prohibited until coupon approval and separate written authorization.**

The generator defaults to `COUPONS_ONLY`. It produces five currently eligible coupon meshes (three clearance gauges, an open L Faceplate corner, and a full-width guide/shelf test) under `~/Documents/HALO_Dock_Rev_A/coupons/`. The wall-stack coupon is conditionally omitted because the exact selected Dual Lock pair has not been measured.

`FULL_SIZE_PRINT_CANDIDATE` is a consciously selected, fail-closed mode. It requires native Fusion execution, a 125→126 mm width and 211→212 mm height rebuild, interference/path checks, coupon approval, selected clearance, physical Dual Lock measurement, slicer review, and written full-size authorization. Its output is isolated under `~/Documents/HALO_Dock_Rev_A/print-candidate/`.

**BLOCKED — exact Dual Lock pair must be selected and measured before print release.** `0 mm` explicitly means not measured. The intended design retains a 1.5 mm visible open shadow gap and pockets only measured excess thickness into two symmetric, discrete DockBody recesses. Dual Lock bonds to the pocket floors so the load path is wall → Dual Lock → DockBody; no full-area spacer may fill the gap.

## Vendor controls

- Never scale: import and print at **100%**.
- Do not run automatic mesh repair, healing, wall thickening, hole closing, or orientation changes without written approval.
- Support-free printing is a requirement pending native/slicer confirmation; report any perceived need for supports instead of adding them.
- Material is PETG, matte black, pending final vendor/process approval.
- Quote coupons separately. Do not quote or print full-size parts without explicit written authorization identifying checksums.

No native Fusion run, actual export, slicer review, or physical test has been performed in this environment. Use the CAD checklist and receiving inspection; static checks cannot release parts.
