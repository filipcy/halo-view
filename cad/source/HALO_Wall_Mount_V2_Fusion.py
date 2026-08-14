"""Native Fusion 360 generator for the validated HALO wall mount V2.

Run this file from Fusion 360's ``Scripts and Add-Ins`` dialog.  Fusion uses
centimetres internally; all design values and status messages below are mm.
The USB-C keep-out remains PROVISIONAL pending measurement of the final plug.
"""

import os
import traceback

import adsk.core
import adsk.fusion


DEVICE_W = 125.0
DEVICE_H = 211.0
DEVICE_T = 8.0
DEVICE_R = 8.5
CLEARANCE_X = 0.20
CLEARANCE_Y = 0.20
WALL_CONTACT_Z = 0.0
TABLET_REAR_Z = 3.0
REAR_CLEARANCE_Z = 0.30
REAR_SUPPORT_MAX_Z = 2.7
TABLET_FRONT_Z = 11.0
SIDE_W = 3.0
SHELF_H = 3.0
LIP_OVERLAP = 1.25
LIP_T = 0.8
RETAINER_MIN_Z = 10.2
RETAINER_MAX_Z = 11.0
EDGE_CHAMFER = 2.0
BUTTON_OLD = (146.0, 192.0)
BUTTON_SHIFT = -22.0
BUTTON_V2 = tuple(value + BUTTON_SHIFT for value in BUTTON_OLD)
USB_POCKET = (22.0, 30.0)  # PROVISIONAL: verify against the selected adapter.
USB_CHANNEL_W = 12.0
USB_CENTRE_X = 62.0
WALL_EXIT_Y = 35.0
CAMERA_FROM_REAR_LEFT = 15.5
CAMERA_FROM_BOTTOM = 196.0
CAMERA_SIZE = 18.0
CAMERA_RELIEF_DEPTH = 2.0
# Front-view +X is physical rear-left (the corrected, non-mirrored side).
CAMERA_CENTER_X = DEVICE_W - CAMERA_FROM_REAR_LEFT
CAMERA_CENTER_Y = CAMERA_FROM_BOTTOM

COMPONENT_NAME = "HALO_Wall_Mount_V2"
ENVELOPE_NAME = "TabletEnvelope"


def _cm(mm):
    """Convert public millimetre dimensions to Fusion's internal centimetres."""
    return mm / 10.0


def _extrude_polygon(component, name, points, z0, z1):
    """Create a native sketch/extrude feature and return its new BRep body."""
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = name + " Sketch"
    lines = sketch.sketchCurves.sketchLines
    vertices = [adsk.core.Point3D.create(_cm(x), _cm(y), 0) for x, y in points]
    for index, vertex in enumerate(vertices):
        lines.addByTwoPoints(vertex, vertices[(index + 1) % len(vertices)])
    profile = sketch.profiles.item(0)
    extrudes = component.features.extrudeFeatures
    feature_input = extrudes.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    feature_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
        adsk.core.ValueInput.createByString(f"{z0} mm"))
    feature_input.setOneSideExtent(
        adsk.fusion.DistanceExtentDefinition.create(
            adsk.core.ValueInput.createByString(f"{z1 - z0} mm")),
        adsk.fusion.ExtentDirections.PositiveExtentDirection)
    feature = extrudes.add(feature_input)
    body = feature.bodies.item(0)
    body.name = name
    return body


def _box(component, name, x0, y0, z0, x1, y1, z1):
    return _extrude_polygon(component, name,
                            ((x0, y0), (x1, y0), (x1, y1), (x0, y1)), z0, z1)


def _holder_parts(component):
    """Build the open-top rear skeleton, guides, lips, and split lower shelf."""
    x0, x1 = -CLEARANCE_X, DEVICE_W + CLEARANCE_X
    y0, y1 = -CLEARANCE_Y, DEVICE_H + CLEARANCE_Y
    camera_low = CAMERA_CENTER_Y - CAMERA_SIZE / 2
    camera_high = CAMERA_CENTER_Y + CAMERA_SIZE / 2
    bodies = []
    add_box = lambda name, *bounds: bodies.append(_box(component, name, *bounds))

    add_box("Back Left", x0, y0, 0, 18, y1, REAR_SUPPORT_MAX_Z)
    add_box("Back Right Low", DEVICE_W - 18, y0, 0, x1, camera_low, REAR_SUPPORT_MAX_Z)
    add_box("Back Right High", DEVICE_W - 18, camera_high, 0, x1, y1, REAR_SUPPORT_MAX_Z)
    add_box("Camera Relief Floor", DEVICE_W - 18, camera_low, 0,
            CAMERA_CENTER_X + CAMERA_SIZE / 2, camera_high,
            REAR_SUPPORT_MAX_Z - CAMERA_RELIEF_DEPTH)
    add_box("Camera Outer Rail", CAMERA_CENTER_X + CAMERA_SIZE / 2, camera_low, 0,
            x1, camera_high, REAR_SUPPORT_MAX_Z)
    bodies.append(_extrude_polygon(component, "Back Top Chamfered",
        ((18, DEVICE_H - 18), (DEVICE_W - 18, DEVICE_H - 18),
         (DEVICE_W - 18, y1 - EDGE_CHAMFER), (DEVICE_W - 18 - EDGE_CHAMFER, y1),
         (18 + EDGE_CHAMFER, y1), (18, y1 - EDGE_CHAMFER)), 0, REAR_SUPPORT_MAX_Z))
    add_box("Back Mid", 18, 92, 0, DEVICE_W - 18, 110, REAR_SUPPORT_MAX_Z)
    add_box("Back Bottom Left", 18, y0, 0, USB_CENTRE_X - USB_POCKET[0] / 2, 18, REAR_SUPPORT_MAX_Z)
    add_box("Back Bottom Right", USB_CENTRE_X + USB_POCKET[0] / 2, y0, 0, DEVICE_W - 18, 18, REAR_SUPPORT_MAX_Z)

    # These outside-edge spines bridge the deliberate 0.30 mm tablet/rear gap.
    # They sit outside the tablet envelope and preserve the real rear clearance.
    add_box("Left Spine", x0 - SIDE_W, y0, 0, x0, y1, TABLET_REAR_Z)
    add_box("Guide Left", x0 - SIDE_W, y0, TABLET_REAR_Z, x0, y1, TABLET_FRONT_Z)
    add_box("Lip Left", x0 - SIDE_W, y0, RETAINER_MIN_Z, LIP_OVERLAP, y1, RETAINER_MAX_Z)
    for suffix, low, high in (("Low", y0, BUTTON_V2[0]), ("High", BUTTON_V2[1], y1)):
        add_box("Right Spine " + suffix, x1, low, 0, x1 + SIDE_W, high, TABLET_REAR_Z)
        add_box("Guide Right " + suffix, x1, low, TABLET_REAR_Z, x1 + SIDE_W, high, TABLET_FRONT_Z)
        add_box("Lip Right " + suffix, DEVICE_W - LIP_OVERLAP, low,
                RETAINER_MIN_Z, x1 + SIDE_W, high, RETAINER_MAX_Z)

    left_usb = USB_CENTRE_X - USB_POCKET[0] / 2
    right_usb = USB_CENTRE_X + USB_POCKET[0] / 2
    bodies.append(_extrude_polygon(component, "Shelf Left Chamfered",
        ((x0, y0), (left_usb, y0), (left_usb, y0 - SHELF_H),
         (x0 + EDGE_CHAMFER, y0 - SHELF_H), (x0, y0 - SHELF_H + EDGE_CHAMFER)),
        TABLET_REAR_Z, TABLET_FRONT_Z))
    bodies.append(_extrude_polygon(component, "Shelf Right Chamfered",
        ((right_usb, y0), (x1, y0), (x1, y0 - SHELF_H + EDGE_CHAMFER),
         (x1 - EDGE_CHAMFER, y0 - SHELF_H), (right_usb, y0 - SHELF_H)),
        TABLET_REAR_Z, TABLET_FRONT_Z))
    return bodies


def _join_holder(component, bodies):
    target = bodies[0]
    tools = adsk.core.ObjectCollection.create()
    for body in bodies[1:]:
        tools.add(body)
    combine_input = component.features.combineFeatures.createInput(target, tools)
    combine_input.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    combine_input.isKeepToolBodies = False
    component.features.combineFeatures.add(combine_input)
    target.name = "HALO Wall Mount V2 Holder"
    return target


def _create_component(root, name):
    occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def _validate_and_report(ui, holder_component, holder, envelope_component):
    if holder_component.bRepBodies.count != 1:
        raise RuntimeError(f"Holder body count is {holder_component.bRepBodies.count}, expected 1")
    if envelope_component is holder_component or envelope_component.bRepBodies.count != 1:
        raise RuntimeError("Tablet envelope is not a separate single-body component")
    bounds = holder.boundingBox
    max_z = bounds.maxPoint.z * 10.0
    if max_z > TABLET_FRONT_Z + 1e-6:
        raise RuntimeError(f"Holder exceeds tablet front plane: max Z={max_z:.4f} mm")
    dimensions = tuple((high - low) * 10.0 for low, high in (
        (bounds.minPoint.x, bounds.maxPoint.x),
        (bounds.minPoint.y, bounds.maxPoint.y),
        (bounds.minPoint.z, bounds.maxPoint.z)))
    ui.messageBox(
        "HALO V2 generated and validated\n\n"
        f"Holder BRep bodies: {holder_component.bRepBodies.count}\n"
        f"Overall holder (X × Y × Z): {dimensions[0]:.2f} × {dimensions[1]:.2f} × {dimensions[2]:.2f} mm\n"
        f"Holder maximum Z: {max_z:.2f} mm\n"
        f"Wall-to-tablet-front target: {TABLET_FRONT_Z:.2f} mm\n"
        f"Rear support maximum Z: {REAR_SUPPORT_MAX_Z:.2f} mm\n"
        f"Real rear clearance: {REAR_CLEARANCE_Z:.2f} mm")


def _export(design, holder_component, holder):
    output = os.path.expanduser("~/Documents/HALO_Wall_Mount_V2")
    os.makedirs(output, exist_ok=True)
    manager = design.exportManager
    step_path = os.path.join(output, "HALO_Wall_Mount_V2.step")
    stl_path = os.path.join(output, "HALO_Wall_Mount_V2.stl")
    if not manager.execute(manager.createSTEPExportOptions(step_path, holder_component)):
        raise RuntimeError("STEP export failed")
    stl_options = manager.createSTLExportOptions(holder, stl_path)
    stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    if not manager.execute(stl_options):
        raise RuntimeError("STL export failed")


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(document.products.itemByProductType("DesignProductType"))
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        holder_component = _create_component(root, COMPONENT_NAME)
        holder = _join_holder(holder_component, _holder_parts(holder_component))
        envelope_component = _create_component(root, ENVELOPE_NAME)
        envelope = _box(envelope_component, "Tablet Envelope", 0, 0, TABLET_REAR_Z,
                        DEVICE_W, DEVICE_H, TABLET_FRONT_Z)
        envelope.isLightBulbOn = True
        _validate_and_report(ui, holder_component, holder, envelope_component)
        _export(design, holder_component, holder)
    except Exception:
        ui.messageBox("HALO V2 Fusion generator failed:\n\n" + traceback.format_exc())

