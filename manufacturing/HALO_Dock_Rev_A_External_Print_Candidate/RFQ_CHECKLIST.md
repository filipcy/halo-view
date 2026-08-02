# RFQ checklist

## Before sending any coupon RFQ

- [ ] Native Fusion run and parameter audit recorded.
- [ ] +1 mm width/height rebuild and symmetry checks passed.
- [ ] Each Part ID has matching STEP + STL filenames and SHA-256 values recorded against the manifest.
- [ ] STL inspected at 100% for bounding box, orientation, thin walls, supports, manifold state, and build volume.
- [ ] Vendor instructed: 100% scale; no automatic repair/healing; no geometry, wall, orientation, or support changes without written approval.
- [ ] PETG matte black and finish/process are explicitly confirmed rather than inferred.
- [ ] Quote identifies every coupon separately and excludes full-size parts.

## Functional coupon instructions

- Guide/shelf: use the real bare tablet; lower it vertically through the fully open top between both shortened rails until the complete lower edge seats on the shelf. Record entry force, free clearance/no clamp, rail parallelism, full-width seating, rocking, and removal.
- Faceplate: place the open L on the matching real tablet corner with the rest of the tablet projecting freely beyond both arm ends. Inspect actual outer radius, top/side bezel, screen-lip coverage, screen recess, pocket clearance, rear skirt, and visible front finish. Reject any export that behaves as a closed ring.
- Clearance gauges: test all three without forcing; select clearance only from recorded physical results.
- Wall stack: do not request until the exact selected mated Dual Lock pair is measured. The left and right fields are separate controlled Part IDs, never loose bodies in one file. Bond a real sample flat into each recess; verify the 1.5 mm open shadow-gap witness, direct pad-to-pocket-floor contact, and left/right equivalence.

## Full-size exclusion

- [ ] RFQ states: **FULL-SIZE PRINTING PROHIBITED until coupon approval and separate written authorization.**
- [ ] No Faceplate or DockBody mesh is attached to a coupon RFQ.
- [ ] No root-design STEP is supplied; full-size vendor files, if separately authorized later, are component-scoped Faceplate and DockBody STEP + STL pairs only.
