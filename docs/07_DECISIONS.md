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

## ADR-005 — USB-C from bottom

**Status:** Accepted

Charging enters at the tablet's bottom edge and is routed through a protected service chamber using a low-profile 90-degree connector.

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
