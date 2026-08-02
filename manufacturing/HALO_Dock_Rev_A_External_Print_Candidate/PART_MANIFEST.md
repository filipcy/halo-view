# Part manifest — HALO Dock Rev A external print candidate

**Generated package basename:** `HALO_Dock_Rev_A_External_Print_Candidate`  
**Units/scale:** mm, 100% only  
**Neutral + mesh policy:** every printable item has both STEP and STL; no supplier scaling or automatic repair.

| Part ID / generated suffix | Qty for coupon order | Status | Purpose |
|---|---:|---|---|
| `Coupon_Clearance_0p2mm_Per_Side` | 1 | FIT COUPON | Tablet-thickness slot with 0.2 mm clearance on each side |
| `Coupon_Clearance_0p3mm_Per_Side` | 1 | FIT COUPON | Tablet-thickness slot with 0.3 mm clearance on each side |
| `Coupon_Clearance_0p4mm_Per_Side` | 1 | FIT COUPON | Tablet-thickness slot with 0.4 mm clearance on each side |
| `Coupon_Faceplate_Corner_Lip` | 1 | FIT/FINISH COUPON | Representative rounded Faceplate corner, skirt, bezel, and display lip |
| `Coupon_Side_Guide_Lower_Shelf` | 1 | INSERTION COUPON | Representative paired-guide and lower-shelf insertion section |
| `Coupon_Wall_Stack_Shadow_Gap` | 1 | WALL CONCEPT COUPON | Paired flat Dual Lock fields and visible 1.5 mm shadow-gap stack |
| `Faceplate_PRINT_CANDIDATE` | 0 unless separately authorized | **FULL-SIZE PRINT CANDIDATE ONLY** | Full-size Rev A Faceplate quotation/preflight |
| `DockBody_PRINT_CANDIDATE` | 0 unless separately authorized | **FULL-SIZE PRINT CANDIDATE ONLY** | Full-size Rev A DockBody quotation/preflight |

For each suffix above, the Fusion generator writes:

- `HALO_Dock_Rev_A_External_Print_Candidate_<suffix>.step`
- `HALO_Dock_Rev_A_External_Print_Candidate_<suffix>.stl`

The generator also writes the complete assembly archive/neutral/reference outputs:

- `HALO_Dock_Rev_A_External_Print_Candidate.f3d`
- `HALO_Dock_Rev_A_External_Print_Candidate.step`
- `HALO_Dock_Rev_A_External_Print_Candidate.png`

## Release-state warning

This repository does not contain generated exports from a verified Fusion run. Before RFQ transmission, a CAD owner must execute the generator natively in Fusion 360, rebuild it, perform interference and visual mesh checks, verify every expected file, record checksums, and issue a controlled package. Until that occurs, this manifest is a generation target rather than evidence that deliverables were validated.
