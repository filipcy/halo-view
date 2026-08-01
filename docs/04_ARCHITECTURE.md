# Hardware Architecture

## Components

### HALO Dock

The wall-side structure responsible for:

- adhesive mounting interface;
- structural stiffness;
- alignment;
- cable routing and connector relief;
- controlled wall offset;
- service access.

### HALO Faceplate

The visible product surface responsible for:

- visually integrating the tablet;
- continuing the tablet corner language;
- retaining the tablet without loading the display;
- hiding mechanical interfaces;
- allowing tool-free service access.

### Tablet

Samsung Galaxy Tab A11 SM-X130, bare, portrait orientation. The tablet is not an adhesive mounting surface and should not carry structural loads from the wall interface.

## Assembly concept

```text
Faceplate / carrier
        │
     Tablet
        │
      Dock
        │
  3M Dual Lock
        │
      Tile
```

## Engineering rules

- Model from a central datum and symmetric reference geometry where practical.
- Tablet contact should occur on safe enclosure surfaces, not through pressure on the active display area.
- Allow manufacturing and tablet tolerances; do not use catalogue dimensions as exact fit dimensions without validation.
- Protect the USB-C connector from bending load.
- Hide service openings from normal viewing angles.
- Prefer geometry that prints without visible support damage on exterior surfaces.

## Expansion reserve

V1 may reserve internal routing volume for a future small indicator or ambient-light module. Any reserve must remain invisible, must not increase V1 complexity materially and must not compromise stiffness or printability.
