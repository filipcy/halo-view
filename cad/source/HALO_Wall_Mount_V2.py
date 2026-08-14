"""Dependency-free reference generator for the HALO tablet wall mount V2.

The generated STL is a design-review mesh.  Dimensions are millimetres and the
wall datum is Z=0.  Run with Python 3; no CAD kernel is required.
"""

from pathlib import Path
import math

DEVICE_W, DEVICE_H, DEVICE_T, DEVICE_R = 125.0, 211.0, 8.0, 8.5
CLEARANCE_X = CLEARANCE_Y = 0.20       # physically validated Rev A fit
WALL_CONTACT_Z = 0.0
TABLET_REAR_Z = 3.0                     # installed tablet datum, not support thickness
REAR_CLEARANCE_Z = 0.30                 # physically validated Rev A rear clearance
REAR_SUPPORT_MAX_Z = TABLET_REAR_Z - REAR_CLEARANCE_Z
REAR_SUPPORT_T = REAR_SUPPORT_MAX_Z - WALL_CONTACT_Z
TABLET_FRONT_Z = TABLET_REAR_Z + DEVICE_T
# Preserve the Rev A 8.6 mm Z-clearance concept as a reference envelope, while
# constraining every printable V2 feature to the real 8 mm tablet thickness.
VALIDATED_POCKET_DEPTH = DEVICE_T + 0.60
GUIDE_DEPTH = VALIDATED_POCKET_DEPTH     # compatibility name; not a solid extent
PRINTABLE_FORWARD_DEPTH = TABLET_FRONT_Z - TABLET_REAR_Z
SIDE_W, SHELF_H = 3.0, 3.0
LIP_OVERLAP, LIP_T = 1.25, 0.8
# Retainers occupy the front-most 0.8 mm of the real tablet thickness.  They
# capture the bezel edge without crossing the actual tablet-front plane.
RETAINER_MAX_Z = TABLET_FRONT_Z
RETAINER_MIN_Z = RETAINER_MAX_Z - LIP_T
EDGE_CHAMFER = 2.0                       # exposed top/bottom plan edges only
BUTTON_OLD = (146.0, 192.0)
BUTTON_SHIFT = -22.0
BUTTON_V2 = tuple(v + BUTTON_SHIFT for v in BUTTON_OLD)
# PROVISIONAL: never production-approved until the selected adapter is measured.
USB_POCKET = (22.0, 30.0)
USB_CHANNEL_W = 12.0
USB_CENTRE_X = 62.0                     # retained Rev A edge datum
WALL_EXIT_Y = 35.0
CAMERA_FROM_REAR_LEFT = 15.5
CAMERA_FROM_BOTTOM = 196.0
CAMERA_SIZE = 18.0
CAMERA_RELIEF_DEPTH = 2.0
# Model X is defined looking at the tablet front.  Rear-view left is therefore
# +X: this deliberately corrects the mirrored Rev A camera keep-out.
CAMERA_CENTER_X = DEVICE_W - CAMERA_FROM_REAR_LEFT
CAMERA_CENTER_Y = CAMERA_FROM_BOTTOM

OUT = Path(__file__).resolve().parents[1] / "v2"


def box(name, x0, y0, z0, x1, y1, z1):
    """Return a named rectangular printable solid."""
    return (name, (x0, y0, z0), (x1, y1, z1))


def prism(name, points, z0, z1):
    """Return a convex XY prism; used for exterior-only edge chamfers."""
    return (name, tuple(points), z0, z1)


def solids():
    """Skeleton, guides and retainers; overlaps are intentional FDM unions."""
    pw, ph = DEVICE_W + 2 * CLEARANCE_X, DEVICE_H + 2 * CLEARANCE_Y
    x0, x1, y0, y1 = -CLEARANCE_X, DEVICE_W + CLEARANCE_X, -CLEARANCE_Y, DEVICE_H + CLEARANCE_Y
    parts = [
        # Projection-neutral rear skeleton. The open centre is not a chamber.
        box("back-left", x0, y0, WALL_CONTACT_Z, 18, y1, REAR_SUPPORT_MAX_Z),
        # Right rear rail is split around the correctly oriented camera relief.
        box("back-right-low", DEVICE_W - 18, y0, WALL_CONTACT_Z, x1, CAMERA_CENTER_Y - CAMERA_SIZE / 2, REAR_SUPPORT_MAX_Z),
        box("back-right-high", DEVICE_W - 18, CAMERA_CENTER_Y + CAMERA_SIZE / 2, WALL_CONTACT_Z, x1, y1, REAR_SUPPORT_MAX_Z),
        box("camera-relief-floor", DEVICE_W - 18, CAMERA_CENTER_Y - CAMERA_SIZE / 2, 0,
            CAMERA_CENTER_X + CAMERA_SIZE / 2, CAMERA_CENTER_Y + CAMERA_SIZE / 2,
            REAR_SUPPORT_MAX_Z - CAMERA_RELIEF_DEPTH),
        box("camera-relief-outer-rail", CAMERA_CENTER_X + CAMERA_SIZE / 2,
            CAMERA_CENTER_Y - CAMERA_SIZE / 2, WALL_CONTACT_Z, x1,
            CAMERA_CENTER_Y + CAMERA_SIZE / 2, REAR_SUPPORT_MAX_Z),
        prism("back-top-chamfered", [(18, DEVICE_H - 18), (DEVICE_W - 18, DEVICE_H - 18),
              (DEVICE_W - 18, y1 - EDGE_CHAMFER), (DEVICE_W - 18 - EDGE_CHAMFER, y1),
              (18 + EDGE_CHAMFER, y1), (18, y1 - EDGE_CHAMFER)], WALL_CONTACT_Z, REAR_SUPPORT_MAX_Z),
        box("back-mid", 18, 92, WALL_CONTACT_Z, DEVICE_W - 18, 110, REAR_SUPPORT_MAX_Z),
        box("back-bottom-left", 18, y0, WALL_CONTACT_Z, USB_CENTRE_X - USB_POCKET[0] / 2, 18, REAR_SUPPORT_MAX_Z),
        box("back-bottom-right", USB_CENTRE_X + USB_POCKET[0] / 2, y0, WALL_CONTACT_Z, DEVICE_W - 18, 18, REAR_SUPPORT_MAX_Z),
        # Left guide and its minimal front safety lip.
        box("guide-left", x0 - SIDE_W, y0, TABLET_REAR_Z, x0, y1, TABLET_FRONT_Z),
        box("lip-left", x0 - SIDE_W, y0, RETAINER_MIN_Z, LIP_OVERLAP, y1, RETAINER_MAX_Z),
        # Right guide is split at the button access, exactly 22 mm lower.
        box("guide-right-low", x1, y0, TABLET_REAR_Z, x1 + SIDE_W, BUTTON_V2[0], TABLET_FRONT_Z),
        box("guide-right-high", x1, BUTTON_V2[1], TABLET_REAR_Z, x1 + SIDE_W, y1, TABLET_FRONT_Z),
        box("lip-right-low", DEVICE_W - LIP_OVERLAP, y0, RETAINER_MIN_Z, x1 + SIDE_W, BUTTON_V2[0], RETAINER_MAX_Z),
        box("lip-right-high", DEVICE_W - LIP_OVERLAP, BUTTON_V2[1], RETAINER_MIN_Z, x1 + SIDE_W, y1, RETAINER_MAX_Z),
        # Continuous lower load shelf, interrupted only by the connector pocket.
        prism("shelf-left-chamfered", [(x0, y0), (USB_CENTRE_X - USB_POCKET[0] / 2, y0),
              (USB_CENTRE_X - USB_POCKET[0] / 2, y0 - SHELF_H),
              (x0 + EDGE_CHAMFER, y0 - SHELF_H), (x0, y0 - SHELF_H + EDGE_CHAMFER)],
              TABLET_REAR_Z, TABLET_FRONT_Z),
        prism("shelf-right-chamfered", [(USB_CENTRE_X + USB_POCKET[0] / 2, y0), (x1, y0),
              (x1, y0 - SHELF_H + EDGE_CHAMFER), (x1 - EDGE_CHAMFER, y0 - SHELF_H),
              (USB_CENTRE_X + USB_POCKET[0] / 2, y0 - SHELF_H)], TABLET_REAR_Z, TABLET_FRONT_Z),
    ]
    return parts


def triangles(part):
    if len(part) == 4:
        _, points, z0, z1 = part
        bottom = [(x, y, z0) for x, y in points]
        top = [(x, y, z1) for x, y in points]
        result = []
        for i in range(1, len(points) - 1):
            result.extend(((bottom[0], bottom[i + 1], bottom[i]),
                           (top[0], top[i], top[i + 1])))
        for i in range(len(points)):
            j = (i + 1) % len(points)
            result.extend(((bottom[i], bottom[j], top[j]),
                           (bottom[i], top[j], top[i])))
        return result
    _, a, b = part
    x0, y0, z0 = a; x1, y1, z1 = b
    v = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0),
         (x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    faces = [(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
             (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
    return [(v[i], v[j], v[k]) for i,j,k in faces]


def solid_max_z(part):
    """Return the forward-most Z for either a box or convex-prism solid."""
    return part[3] if len(part) == 4 else part[2][2]


def normal(t):
    a,b,c=t; u=tuple(b[i]-a[i] for i in range(3)); v=tuple(c[i]-a[i] for i in range(3))
    n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    q=math.sqrt(sum(x*x for x in n)) or 1
    return tuple(x/q for x in n)


def write_stl(parts):
    path = OUT / "HALO_Wall_Mount_V2_review.stl"
    with path.open("w", encoding="ascii") as f:
        f.write("solid HALO_Wall_Mount_V2\n")
        for part in parts:
            for tri in triangles(part):
                n=normal(tri); f.write(" facet normal %.6g %.6g %.6g\n  outer loop\n" % n)
                for p in tri: f.write("   vertex %.6g %.6g %.6g\n" % p)
                f.write("  endloop\n endfacet\n")
        f.write("endsolid HALO_Wall_Mount_V2\n")
    return path


def svg(name, title, body, width=820, height=620):
    style="background:#eee;fill:#151515;stroke:#555;stroke-width:1.2;stroke-linejoin:round"
    text_style="font-family:Arial,sans-serif;fill:#222;stroke:none"
    data=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#f4f4f2"/><g style="{style}">{body}</g><text x="28" y="38" font-size="24" style="{text_style}">{title}</text><text x="28" y="596" font-size="15" style="{text_style}">HALO V2 · dimensions in mm · review geometry</text></svg>'''
    (OUT / name).write_text(data, encoding="utf-8")


def views():
    # Orthographic review drawings are deliberately dimension-led, not photorealistic.
    front='''<rect x="227" y="55" width="366" height="506" rx="22"/><rect x="236" y="63" width="348" height="490" rx="19" fill="#303236"/><rect x="252" y="80" width="316" height="456" rx="10" fill="#090909"/><path d="M227 553h150m66 0h150" stroke="#999"/><path d="M593 264v110" stroke="#f4f4f2" stroke-width="10"/>'''
    back='''<rect x="227" y="55" width="366" height="506" rx="22"/><rect x="245" y="75" width="48" height="466" fill="#333"/><rect x="527" y="75" width="48" height="466" fill="#333"/><rect x="293" y="75" width="234" height="43" fill="#333"/><rect x="293" y="278" width="234" height="44" fill="#333"/><path d="M293 541h91v-70h58v70h85" fill="#333"/><rect x="245" y="105" width="40" height="44" fill="#777" stroke="#d8a737" stroke-width="4"/><text x="300" y="133" fill="#222" stroke="none">camera · rear-left</text><path d="M395 541v-72h34v-72" fill="none" stroke="#d8a737" stroke-width="12"/><circle cx="429" cy="397" r="22" fill="#f4f4f2" stroke="#d8a737" stroke-width="5"/>'''
    side='''<path d="M260 85h16v470h-16z"/><path d="M276 85h34v470h-34z" fill="#303236"/><path d="M310 85h12v470h-12z"/><path d="M308 85h14v470h-14z" fill="#555"/><path d="M220 555h145" stroke="#999"/><path d="M260 570v-30M310 570v-30M260 568h50" stroke="#333"/><text x="280" y="590" fill="#222" stroke="none">11.0 to tablet + retainer front</text>'''
    top='''<path d="M145 260h530v24H145z"/><path d="M157 284h506v138H157z" fill="#303236"/><path d="M145 422h530v15H145z"/><path d="M135 260h10v177h-10zM675 260h10v177h-10z" fill="#222"/>'''
    bottom='''<path d="M145 260h202v177H145zM473 260h202v177H473z"/><rect x="347" y="300" width="126" height="137" fill="#f4f4f2" stroke="#d8a737" stroke-width="5"/><path d="M410 300v-70" stroke="#d8a737" stroke-width="12"/><text x="323" y="470" fill="#222" stroke="none">90° USB-C pocket</text>'''
    section='''<rect x="90" y="95" width="28" height="430" fill="#ddd"/><rect x="118" y="125" width="70" height="370"/><rect x="188" y="125" width="8" height="370" fill="#d8a737"/><rect x="196" y="125" width="208" height="370" fill="#303236"/><rect x="384" y="125" width="20" height="370" fill="#555"/><path d="M90 555v-35M404 555v-35M90 548h314" stroke="#333"/><text x="205" y="580" fill="#222" stroke="none">11.0 wall → actual tablet / retainer front</text><text x="95" y="80" fill="#222" stroke="none">wall</text><text x="118" y="115" fill="#222" stroke="none">2.7 support</text><text x="160" y="515" fill="#222" stroke="none">0.30 rear clearance</text><text x="255" y="115" fill="#222" stroke="none">8.0 tablet</text><text x="350" y="105" fill="#222" stroke="none">retainer Z 10.2–11.0</text>'''
    usb='''<rect x="120" y="80" width="580" height="430" rx="18"/><rect x="270" y="350" width="280" height="160" fill="#303236"/><rect x="345" y="410" width="130" height="100" fill="#f4f4f2" stroke="#d8a737" stroke-width="6"/><path d="M410 410v-145q0-45 45-45h80" fill="none" stroke="#d8a737" stroke-width="18"/><circle cx="535" cy="220" r="34" fill="#f4f4f2" stroke="#d8a737" stroke-width="6"/><text x="500" y="170" fill="#222" stroke="none">wall exit</text><text x="310" y="545" fill="#222" stroke="none">22 × 30 plug envelope</text>'''
    svg('01_front.svg','1 · Front',front); svg('02_rear.svg','2 · Rear skeleton + hidden cable route',back)
    svg('03_left.svg','3 · Left side',side); svg('04_right.svg','4 · Right side · button opening 22 mm lower',side)
    svg('05_top.svg','5 · Open top',top); svg('06_bottom.svg','6 · Bottom',bottom)
    svg('07_section.svg','7 · Section: wall + holder + tablet',section); svg('08_usb_c_detail.svg','8 · USB-C 90° pocket and bend channel',usb)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    parts=solids(); write_stl(parts); views()
    maximum_z = max(solid_max_z(part) for part in parts)
    print(f"V2: wall-contact-to-actual-tablet-front={TABLET_FRONT_Z - WALL_CONTACT_Z:.1f} mm; max-printable-holder-z={maximum_z:.1f} mm; parts={len(parts)}; output={OUT}")


if __name__ == '__main__':
    main()
