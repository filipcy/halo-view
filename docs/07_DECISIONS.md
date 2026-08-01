# Decision Log

## ADR-001 — Dedicated tablet fit

**Status:** Accepted

HALO View V1 is designed specifically for the bare Samsung Galaxy Tab A11 SM-X130. Universal compatibility would weaken proportions, retention and finish quality.

## ADR-002 — Portrait orientation

**Status:** Accepted

Portrait orientation follows the vertical architectural rhythm of the target hallway and avoids the kiosk/browser layout issues observed in landscape mode.

## ADR-003 — Two-part architecture

**Status:** Accepted

The product consists of a wall-side Dock and visible Faceplate/tablet carrier. The Dock handles mounting, stiffness and cable routing; the Faceplate handles fit, service and appearance.

## ADR-004 — No drilling

**Status:** Accepted

V1 mounts to tile using a removable high-strength reclosable fastener, currently 3M Dual Lock SJ3550 or validated equivalent. Screws, wall plugs and permanent mechanical fixings are out of scope.

## ADR-005 — USB-C from bottom using a standard cable envelope

**Status:** Accepted

Charging enters at the tablet's bottom edge and is routed through a protected service chamber. V1 must not require a proprietary or unusually specific cable. A standard straight USB-C cable is the default design basis unless physical packaging proves unacceptable; a low-profile angled cable remains an allowed optimisation, not a product requirement.

## ADR-006 — Matte dark finish

**Status:** Accepted

The visible hardware uses matte black or near-black charcoal to join the apartment's existing black details and remain visually quiet against grey tile and wood.

## ADR-007 — Future lighting provision only

**Status:** Accepted

V1 contains no LED hardware. A small invisible routing or packaging reserve may be included only when it does not delay, weaken or visibly compromise V1.

## ADR-008 — Quality over schedule

**Status:** Accepted

The desired two-day print-release target is subordinate to fit, safety, manufacturability and visual approval.

## ADR-009 — Faceplate bezel width: 6 mm

**Status:** Accepted  
**Date:** 2026-08-01

The visible Faceplate bezel is fixed at **6 mm**. A 7 mm alternative was visually reviewed with the tablet both on and off and was rejected because it appeared heavier and more visually dominant.

### Rationale

- 6 mm preserves the intended architectural-panel presence without reading as an added protective case.
- It gives the display a better screen-to-product proportion.
- It integrates more quietly with the grey tile, oak slats and mirror.
- It retains enough material for stiffness and a controlled internal screen lip.

### Consequences

- The active CAD parameter for bezel width is 6.0 mm.
- The internal edge may overlap the glass by 0.5 mm, subject to active-display verification.
- Any later change to bezel width requires a new visual review and an explicit superseding decision.

## ADR-010 — Initial body clearance: +0.3 mm per side

**Status:** Accepted for Rev A validation  
**Date:** 2026-08-01

The initial tablet pocket uses a nominal clearance of **+0.3 mm per side**. This value is a prototype assumption and must be validated with a fit coupon or first prototype before production release.

## ADR-011 — V1 scope remains hardware-only

**Status:** Accepted  
**Date:** 2026-08-01

Current work is limited to the HALO Dock V1 mechanical product: Faceplate, Dock, USB-C routing and Dual Lock mounting. Lighting, e-paper, custom electronics and HALO UI development remain backlog items and may not delay the mechanical MVP.

## ADR-012 — Tablet inserts from the top

**Status:** Accepted  
**Date:** 2026-08-01

The tablet is inserted vertically from the top. Gravity assists retention, the bottom edge can provide a positive mechanical datum, and routine service does not require flexing the visible Faceplate.

## ADR-013 — Display recess: 0.8 mm

**Status:** Accepted for Rev A  
**Date:** 2026-08-01

The display surface is recessed approximately **0.8 mm** behind the visible Faceplate plane. This creates a controlled shadow line, protects the glass edge and avoids a visually flat case-like appearance. The Faceplate must not press on the active display surface.

## ADR-014 — Wall shadow gap: 1.5 mm

**Status:** Accepted for Rev A  
**Date:** 2026-08-01

The visible assembly uses a nominal **1.5 mm** shadow gap to the wall datum. The gap must remain visually even and must not expose Dual Lock, cable routing or service features from normal viewing positions.

## ADR-015 — Total wall projection target: 18 mm

**Status:** Accepted as Rev A packaging target  
**Date:** 2026-08-01

The complete installed product targets approximately **18 mm total projection from the tile surface to the front Faceplate plane**. This is a packaging target, not an absolute release limit. It may be revised only if cable bend radius, structural stiffness or serviceability cannot be achieved without compromising quality.

## ADR-016 — Visible finish is matte

**Status:** Accepted  
**Date:** 2026-08-01

The visible Faceplate finish is fully matte rather than satin or gloss. Material, print orientation and finishing method must minimise layer glare, fingerprints and reflections in the hallway mirror.
