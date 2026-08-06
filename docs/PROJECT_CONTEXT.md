# HALO Project Context

> Source of Truth for the HALO project.
> Read this document before making any design, CAD or software decision.

---

# Vision

HALO is not a tablet holder.

HALO is an architectural wall-mounted smart home interface.

The goal is to make the tablet appear as if it was designed as part of the apartment.

Long term the project may evolve into:

- custom hardware
- dedicated OS
- custom dashboard
- e-paper companion display
- status LED
- commercial product

---

# Product Philosophy

Quality > Time

Every design decision must improve at least one of:

- aesthetics
- usability
- manufacturability
- reliability

Never add features because they are possible.

Only solve real problems.

---

# Design Language

Inspired by:

- Apple
- Sonos
- Basalte

Characteristics:

- minimal
- timeless
- hidden mounting
- invisible cable
- soft radii
- matte finish
- architectural object

---

# Current Hardware

Device:

Samsung Galaxy Tab A11 SM-X130

Current assumptions:

- bezel 6 mm
- screen lip 0.5 mm
- screen recess 0.8 mm
- total projection ≈18 mm
- wall shadow gap 1.5 mm
- PETG
- matte black

Wall mounting:

3M Dual Lock only.

No screws.

No visible fasteners.

---

# Development Process

GitHub is the source of truth.

Workflow:

Issue
↓

Codex implementation
↓

Pull Request
↓

Review
↓

Merge
↓

Next Sprint

Never merge without review.

---

# Completed Work

## Sprint 1

Repository foundation

CAD architecture

Parametric generator

Faceplate

Tablet envelope

DockBody foundation

Merged

---

## Sprint 2

Mechanical geometry

Side guides

Lower shelf

Retention concept

Dual Lock concept

Shadow gap

Merged

---

## Sprint 3

External print candidate

Status:

IN PROGRESS

Goals:

- manufacturing package
- fit coupons
- vendor documentation
- first printable prototype

---

# Printing Strategy

No in-house printer.

All parts are printed by an external company.

Always validate using coupons before ordering full-size parts.

---

# Long Term Roadmap

Phase 1

Perfect Dock

↓

Phase 2

Electronics

↓

Phase 3

LED status

↓

Phase 4

e-paper companion

↓

Phase 5

Custom Dashboard

↓

Phase 6

HALO OS

↓

Phase 7

Commercial Product

---

# Definition of Done

A sprint is complete only when:

- PR reviewed
- merged
- documentation updated
- GitHub clean
- manufacturing impact assessed

---

# Golden Rule

If a decision improves appearance but hurts usability:

don't do it.

If a decision improves engineering but hurts appearance:

think twice.

HALO must always feel like architecture, not electronics.

## Rev A physical fit state — 2026-08-06

Supplier PETG coupons (printer reported as Bambu Lab X2D) close the tablet fit choices: 0.20 mm nominal clearance per side and R8.5 device corners are selected. The 0.30/0.40 mm clearances are rejected as too loose, while R8 and R9 remain valid historical coupon cases. The existing shelf width, its approximately 1 mm total lateral clearance, and its support height remain accepted; the floor-drop break drives hidden root strengthening only. USB-C X alignment and width remain accepted for the straight cable, with +0.30 mm downward relief and +0.20 mm rear relief required.

Accepted architectural intent remains unchanged: 6.0 mm bezel, 0.5 mm screen lip, 0.8 mm recess, 1.5 mm wall shadow gap, approximately 18 mm projection, open-top service path, matte black exterior, 3M Dual Lock mounting with a separate engaged-thickness parameter, signed Iteration 2 left/right datums, camera keep-out and button relief. The 3.5 mm jack and microSD access remain intentionally excluded.

Native full-model Fusion execution, timeline rebuild, interference analysis, F3D/STEP/STL exports, and visual inspection are still required before release.
