# HALO-DWG-001 — Dock Rev A Architecture

**Document status:** Design freeze candidate  
**Product:** HALO View  
**Device:** Samsung Galaxy Tab A11 SM-X130  
**Orientation:** Portrait  
**Date:** 2026-08-01

## Purpose

This document freezes the mechanical architecture inputs required to begin the first parametric CAD model. It is not a manufacturing release drawing.

## Product stack

From wall to user:

1. tiled wall;
2. 3M Dual Lock adhesive interface;
3. wall-side Dock;
4. tablet pocket and cable service volume;
5. bare SM-X130 tablet;
6. visible matte Faceplate.

## Accepted Rev A parameters

| Parameter | Rev A value | Release status |
|---|---:|---|
| Tablet orientation | portrait | fixed |
| Tablet insertion direction | from top | fixed |
| Visible bezel | 6.0 mm | fixed |
| Inner screen lip | 0.5 mm target | verify against active display |
| Display recess from Faceplate plane | 0.8 mm | fixed for Rev A |
| Tablet pocket clearance | +0.3 mm per side | prototype assumption |
| Wall shadow gap | 1.5 mm | fixed for Rev A |
| Total projection from tile | approximately 18 mm | packaging target |
| Wall mounting | 3M Dual Lock only | fixed |
| Visible finish | matte black / near-black charcoal | fixed |
| Visible screws | none | fixed |
| Cable exit | bottom, downward | fixed |
| Cable type | standard USB-C envelope preferred | validate during CAD |

## Functional architecture

### Dock

The Dock carries structural loads, provides the wall interface, controls the shadow gap and contains the cable service volume. The adhesive side of the Dual Lock remains attached to the tile during normal tablet service.

### Faceplate

The Faceplate controls the visible geometry, screen recess, edge language and tablet retention. It must not clamp the active glass or require visible fasteners.

### Tablet insertion

The tablet enters from the top, follows side guides and lands on a positive lower datum. Retention must prevent forward movement and rattle while allowing deliberate removal without tools.

### Cable path

The cable connects at the bottom edge near the confirmed 59 mm horizontal datum from the left device edge. The service volume must avoid side-loading the USB-C port and must allow the cable to leave vertically downward. Final chamber geometry remains blocked by cable-envelope validation.

## CAD parameters to expose

The source CAD must expose at least:

- device width, height and thickness;
- device corner profile;
- bezel width;
- inner lip overlap;
- screen recess;
- pocket clearance X/Y/Z;
- front thickness;
- wall shadow gap;
- total projection target;
- Dual Lock pad size and position;
- USB port datum and connector envelope;
- lower support thickness;
- retention feature clearance;
- camera, speaker, microphone and button keep-out zones.

## Open engineering decisions

The following are deliberately not yet frozen:

1. Faceplate structural thickness.
2. Exact outer corner spline/radius after geometric reconstruction.
3. Outer-edge fillet/chamfer treatment.
4. Retention geometry at the top.
5. Exact standard cable and bend envelope.
6. Dual Lock field size and spacing.
7. Print material and manufacturing orientation.

## Rev A review criteria

The first CAD review must show:

- front, rear and side orthographic views;
- section through the screen edge;
- section through the bottom USB service volume;
- exploded view of Dock, tablet and Faceplate;
- wall interface and 1.5 mm shadow gap;
- tablet insertion and removal path;
- proposed print orientation and support strategy.

## Release gate

No full-size print is released until:

- the open dimensions are resolved or explicitly accepted as prototype assumptions;
- a fit coupon validates the +0.3 mm pocket clearance and screen-edge geometry;
- the cable chamber is validated against a physical cable;
- the Product Owner approves the rendered front and side proportions.
