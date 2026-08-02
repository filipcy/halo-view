"""HALO Dock Rev A Sprint 3 parametric generator for Autodesk Fusion 360.

Sprint 3 adds coupon-first exports and measurement-gated wall-mount geometry to
the accepted Iteration 2 model.  It does not constitute a manufacturing release.
Run this script from Fusion 360's Scripts and Add-Ins dialog.
"""

import adsk.core
import adsk.fusion
import adsk.cam
import os
import traceback

APP = adsk.core.Application.get()
UI = APP.userInterface if APP else None

COUPONS_ONLY = 'COUPONS_ONLY'
FULL_SIZE_PRINT_CANDIDATE = 'FULL_SIZE_PRINT_CANDIDATE'
EXPORT_MODE = COUPONS_ONLY

# These declarations are deliberately false in source control.  Set every gate
# true only in the local Fusion session after recording the corresponding
# evidence.  Selecting FULL_SIZE_PRINT_CANDIDATE alone is never authorization.
FULL_SIZE_RELEASE_GATES = {
    'native_fusion_run': False,
    'rebuild_plus_1_mm': False,
    'interference_check': False,
    'coupons_approved': False,
    'clearance_selected': False,
    'corner_radius_selected': False,
    'slicer_stl_review': False,
    'written_full_size_authorization': False,
}
COUPON_PART_IDS = {
    '0.2': 'HALO_Dock_Rev_A_Clearance_0_2mm',
    '0.3': 'HALO_Dock_Rev_A_Clearance_0_3mm',
    '0.4': 'HALO_Dock_Rev_A_Clearance_0_4mm',
    'corner_R8_0': 'HALO_Dock_Rev_A_Faceplate_Open_Corner_L_R8_0',
    'corner_R8_5': 'HALO_Dock_Rev_A_Faceplate_Open_Corner_L_R8_5',
    'corner_R9_0': 'HALO_Dock_Rev_A_Faceplate_Open_Corner_L_R9_0',
    'faceplate_cable': 'HALO_Dock_Rev_A_Faceplate_USB_C_Cable_Pocket',
    'guide': 'HALO_Dock_Rev_A_Side_Guide_Lower_Shelf',
    'wall_right': 'HALO_Dock_Rev_A_Wall_Stack_Shadow_Gap_Right',
    'wall_left': 'HALO_Dock_Rev_A_Wall_Stack_Shadow_Gap_Left',
}
FULL_SIZE_PART_IDS = {
    'faceplate': 'HALO_Dock_Rev_A_Faceplate_PRINT_CANDIDATE_ONLY',
    'dock_body': 'HALO_Dock_Rev_A_DockBody_PRINT_CANDIDATE_ONLY',
}
PARAMETERS = (
    # Captured device envelope.
    ('device_width', '125 mm', 'Device', 'Bare tablet width; validate by caliper'),
    ('device_height', '211 mm', 'Device', 'Bare tablet height; validate by caliper'),
    ('device_thickness', '8 mm', 'Device', 'Maximum bare tablet thickness; validate by caliper'),
    ('device_corner_radius', '8.5 mm', 'Device', 'PROVISIONAL AND UNVERIFIED; select only after coupon fit validation'),
    # Accepted Rev A interface values.
    ('bezel_width', '6 mm', 'Faceplate', 'Visible bezel around tablet'),
    ('inner_lip_overlap', '0.5 mm', 'Faceplate', 'Target overlap; verify against active display'),
    ('screen_recess', '0.8 mm', 'Faceplate', 'Display recess from Faceplate plane'),
    ('pocket_clearance_x', '0.3 mm', 'Fit', 'Clearance per tablet side'),
    ('pocket_clearance_y', '0.3 mm', 'Fit', 'Clearance per tablet end'),
    ('pocket_clearance_z', '0.3 mm', 'Fit', 'Clearance behind tablet'),
    ('pocket_depth', 'device_thickness + 2 * pocket_clearance_z', 'Fit', 'Usable pocket depth; matches the selected clearance-coupon slot width'),
    # Open engineering parameters selected for the Iteration 2 model.
    ('front_thickness', '2.4 mm', 'Faceplate', 'Prototype Faceplate structural thickness'),
    ('wall_shadow_gap', '1.5 mm', 'Dock', 'Gap between tile and DockBody'),
    ('total_projection_target', '18 mm', 'Dock', 'Packaging target from tile to front face'),
    ('dock_back_thickness', 'total_projection_target - wall_shadow_gap - pocket_depth - screen_recess', 'Dock', 'Derived rear depth that closes the installed projection stack'),
    ('dock_side_wall', '3 mm', 'Dock', 'Prototype perimeter wall width'),
    ('lower_support_thickness', '3 mm', 'Dock', 'Reserved lower tablet support thickness'),
    ('retention_clearance', '0.3 mm', 'Fit', 'Reserved retention feature clearance'),
    ('guide_depth', 'pocket_depth', 'Dock', 'Side-guide and shelf depth equals the usable tablet pocket depth'),
    ('guide_center_x', 'device_width / 2 + pocket_clearance_x + dock_side_wall / 2', 'Dock', 'Side-guide centre magnitude'),
    ('guide_center_x_left', '-guide_center_x', 'Dock', 'Left side-guide centre'),
    ('guide_center_y', '-dock_side_wall / 2', 'Dock', 'Side-guide vertical centre leaves the top insertion edge open'),
    ('guide_height', 'device_height + 2 * pocket_clearance_y - dock_side_wall', 'Dock', 'Side-guide height below the open top edge'),
    ('shelf_center_y', '-device_height / 2 - pocket_clearance_y - lower_support_thickness / 2', 'Dock', 'Lower support centre below TabletEnvelope'),
    ('shelf_width', 'device_width + 2 * pocket_clearance_x', 'Dock', 'Lower support width between guides'),
    ('retention_concept_height', '12 mm', 'Dock', 'Non-final upper side detent study height'),
    ('retention_concept_width', '1 mm', 'Dock', 'Non-final detent width outside the tablet envelope'),
    ('retention_center_x', 'device_width / 2 + retention_concept_width / 2', 'Dock', 'Non-final detent reaches the TabletEnvelope boundary without crossing it'),
    ('retention_center_x_left', '-retention_center_x', 'Dock', 'Left non-final detent centre'),
    ('retention_center_y', 'device_height / 2 - retention_concept_height / 2', 'Dock', 'Non-final side detent location below the open top'),
    ('dock_center_x', '0 mm', 'Dock', 'Shared horizontal centre datum for DockBody features'),
    # Sprint 3 coupons.
    ('coupon_guide_clearance', '0.3 mm', 'Coupons', 'Selected per-side clearance for the guide/shelf coupon'),
    ('coupon_guide_length', '30 mm', 'Coupons', 'Short guide engagement length; tablet inserts through open top'),
    ('coupon_guide_inner_width', 'device_width + 2 * coupon_guide_clearance', 'Coupons', 'Actual tablet pocket width between coupon rails'),
    ('coupon_guide_center_x', 'coupon_guide_inner_width / 2 + dock_side_wall / 2', 'Coupons', 'Right guide coupon rail centre magnitude'),
    ('coupon_guide_center_x_left', '-coupon_guide_center_x', 'Coupons', 'Left guide coupon rail centre'),
    ('coupon_guide_center_y', '-lower_support_thickness / 2', 'Coupons', 'Rail centre provides structural overlap with the lower shelf'),
    ('coupon_shelf_width', 'coupon_guide_inner_width + 2 * dock_side_wall', 'Coupons', 'Shelf seating area spans the pocket and joins both rails'),
    ('coupon_shelf_center_y', '-coupon_guide_length / 2 - lower_support_thickness / 2', 'Coupons', 'Shelf below the shortened guides'),
    ('coupon_corner_arm_length', '52 mm', 'Coupons', 'Length of each open L coupon arm from the real corner'),
    ('coupon_corner_radius_R8_0', '8.0 mm', 'Coupons', 'Explicit SM-X130 corner-radius candidate'),
    ('coupon_corner_radius_R8_5', '8.5 mm', 'Coupons', 'Explicit SM-X130 corner-radius candidate'),
    ('coupon_corner_radius_R9_0', '9.0 mm', 'Coupons', 'Explicit SM-X130 corner-radius candidate'),
    ('coupon_corner_outer_width', 'device_width + 2 * bezel_width', 'Coupons', 'Reference Faceplate outer width'),
    ('coupon_corner_outer_height', 'device_height + 2 * bezel_width', 'Coupons', 'Reference Faceplate outer height'),
    ('coupon_fit_rail_length', '30 mm', 'Coupons', 'Compact clearance-gauge rail length'),
    ('coupon_fit_rail_width', '3 mm', 'Coupons', 'Clearance-gauge structural rail width'),
    ('coupon_fit_base_height', '3 mm', 'Coupons', 'Clearance-gauge connecting base height'),
    ('selected_clearance_coupon_slot_width', 'device_thickness + 2 * 0.3 mm', 'Coupons', '0.3 mm candidate slot selected provisionally for full-model depth parity'),
    # Exact engaged thickness must be measured on the selected mated pair.
    ('dual_lock_pad_width', '25 mm', 'Wall interface', 'Flat hidden mounting field width'),
    ('dual_lock_pad_height', '50 mm', 'Wall interface', 'Flat hidden mounting field height'),
    ('dual_lock_pad_edge_offset', '12 mm', 'Wall interface', 'Field offset from DockBody side edge'),
    ('dual_lock_center_x', 'device_width / 2 + pocket_clearance_x + dock_side_wall - dual_lock_pad_edge_offset - dual_lock_pad_width / 2', 'Wall interface', 'Hidden mounting field centre magnitude'),
    ('dual_lock_center_x_left', '-dual_lock_center_x', 'Wall interface', 'Left hidden mounting field centre'),
    ('dual_lock_center_y', '0 mm', 'Wall interface', 'Hidden mounting field vertical centre'),
    ('dual_lock_measured_engaged_thickness', '0 mm', 'Wall interface', 'REQUIRED PHYSICAL MEASUREMENT — exact selected Dual Lock pair; 0 mm means NOT MEASURED'),
    ('dual_lock_recess_depth', 'dual_lock_measured_engaged_thickness - wall_shadow_gap', 'Wall interface', 'Measured stack excess received by the DockBody rear recess'),
    ('dual_lock_remaining_back_thickness', 'dock_back_thickness - dual_lock_recess_depth', 'Wall interface', 'Reported structural backing thickness below each recess'),
    ('wall_coupon_margin', '6 mm', 'Coupons', 'Open shadow-gap witness area around each Dual Lock pad'),
    ('wall_coupon_field_spacing', '8 mm', 'Coupons', 'Open separation between symmetric wall coupon fields'),
    ('wall_coupon_backing_width', 'dual_lock_pad_width + 2 * wall_coupon_margin', 'Coupons', 'Discrete DockBody witness block width around each pad recess'),
    ('wall_coupon_backing_height', 'dual_lock_pad_height + 2 * wall_coupon_margin', 'Coupons', 'Discrete DockBody witness block height around each pad recess'),
    ('wall_coupon_center_x', 'wall_coupon_backing_width / 2 + wall_coupon_field_spacing / 2', 'Coupons', 'Right wall coupon field centre magnitude'),
    ('wall_coupon_center_x_left', '-wall_coupon_center_x', 'Coupons', 'Left wall coupon field centre'),
    # Dashboard-critical openings and blind keep-outs. Positions are measured
    # from physical tablet edges, then converted to centred model coordinates.
    ('cable_pocket_edge_x', '62 mm', 'Keep-outs', 'Cable-pocket centre from tablet left edge'),
    ('cable_pocket_center_x', '-device_width / 2 + cable_pocket_edge_x', 'Keep-outs', 'Centred cable-pocket X datum'),
    ('cable_pocket_width', '18 mm', 'Keep-outs', 'Generic plug/cable width envelope'),
    ('cable_pocket_height', '8 mm', 'Keep-outs', 'Generic plug/cable height envelope'),
    ('cable_pocket_run_depth', '20 mm', 'Keep-outs', 'Cable run below the tablet bottom edge'),
    ('cable_pocket_center_y', '-device_height / 2 - cable_pocket_run_depth / 2', 'Keep-outs', 'Open-bottom cable-run centre'),
    ('camera_keepout_edge_x', '15.5 mm', 'Keep-outs', 'Camera centre from tablet left edge'),
    ('camera_keepout_edge_y', '196 mm', 'Keep-outs', 'Camera centre from tablet bottom edge'),
    ('camera_keepout_center_x', '-device_width / 2 + camera_keepout_edge_x', 'Keep-outs', 'Centred camera relief X datum'),
    ('camera_keepout_center_y', '-device_height / 2 + camera_keepout_edge_y', 'Keep-outs', 'Centred camera relief Y datum'),
    ('camera_keepout_width', '18 mm', 'Keep-outs', 'Blind camera-island relief width'),
    ('camera_keepout_height', '18 mm', 'Keep-outs', 'Blind camera-island relief height'),
    ('camera_keepout_depth', '2 mm', 'Keep-outs', 'Blind camera-island relief depth'),
    ('button_relief_edge_y_min', '146 mm', 'Keep-outs', 'Button relief lower bound from tablet bottom'),
    ('button_relief_edge_y_max', '192 mm', 'Keep-outs', 'Button relief upper bound from tablet bottom'),
    ('button_relief_height', 'button_relief_edge_y_max - button_relief_edge_y_min', 'Keep-outs', 'Power/volume relief span'),
    ('button_relief_center_y', '-device_height / 2 + (button_relief_edge_y_min + button_relief_edge_y_max) / 2', 'Keep-outs', 'Centred button relief Y datum'),
    ('button_relief_depth', '1.5 mm', 'Keep-outs', 'Blind relief into the inner face of right guide'),
    ('button_relief_center_x', 'device_width / 2 + pocket_clearance_x + button_relief_depth / 2', 'Keep-outs', 'Relief centre measured outward from guide inner face'),
    ('button_remaining_wall', 'dock_side_wall - button_relief_depth', 'Keep-outs', 'Outer guide wall retained behind button relief'),
    ('speaker_slot_edge_x', '102 mm', 'Keep-outs', 'Speaker slot centre from tablet left edge'),
    ('speaker_slot_center_x', '-device_width / 2 + speaker_slot_edge_x', 'Keep-outs', 'Centred lower-speaker slot X datum'),
    ('speaker_slot_center_y', 'shelf_center_y', 'Keep-outs', 'Speaker slot contained in lower shelf'),
    ('speaker_slot_width', '20 mm', 'Keep-outs', 'Single lower-speaker opening width'),
    ('speaker_slot_height', '5 mm', 'Keep-outs', 'Acoustic opening height through shelf depth'),
    ('speaker_slot_center_z', 'speaker_slot_height / 2', 'Keep-outs', 'XZ slot centre opens from shelf rear datum'),
    ('speaker_slot_plane_offset', '-shelf_center_y - lower_support_thickness / 2', 'Keep-outs', 'Positive XZ-plane offset locates the shelf outer Y face'),
    ('coupon_speaker_slot_plane_offset', '-coupon_shelf_center_y - lower_support_thickness / 2', 'Coupons', 'Positive XZ-plane offset locates the coupon shelf outer Y face'),
    ('coupon_cable_center_y', '-coupon_guide_length / 2 - cable_pocket_run_depth / 2', 'Coupons', 'Open-air cable envelope below shortened guide coupon edge'),
    ('faceplate_cable_coupon_width', '52 mm', 'Coupons', 'Connected bottom-centre Faceplate cable test span'),
    ('faceplate_cable_coupon_band_height', 'bezel_width + inner_lip_overlap', 'Coupons', 'Real visible-lip bottom band height'),
    ('faceplate_cable_coupon_center_x', 'cable_pocket_center_x', 'Coupons', 'Coupon retains the controlled tablet-edge X datum'),
    ('faceplate_cable_coupon_center_y', '-device_height / 2 - faceplate_cable_coupon_band_height / 2', 'Coupons', 'Real bottom Faceplate band location'),
)


def _parameter(design, name):
    return design.userParameters.itemByName(name)


def _set_parameters(design):
    for name, expression, group, comment in PARAMETERS:
        existing = _parameter(design, name)
        if existing:
            # Never erase a physical measurement when the operator reruns the
            # generator to create the now-unblocked wall coupon.
            if name != 'dual_lock_measured_engaged_thickness':
                existing.expression = expression
            existing.comment = comment
        else:
            design.userParameters.add(
                name,
                adsk.core.ValueInput.createByString(expression),
                'mm',
                comment,
            )
        parameter = _parameter(design, name)
        parameter.groupName = group


def _mm(design, name):
    """Return a millimetre user parameter in Fusion's internal centimetres."""
    return _parameter(design, name).value


def _ensure_parameter(design, name, expression, comment, group='Coupons'):
    parameter = _parameter(design, name)
    if parameter:
        parameter.expression = expression
        parameter.comment = comment
    else:
        parameter = design.userParameters.add(
            name, adsk.core.ValueInput.createByString(expression), 'mm', comment)
    parameter.groupName = group
    return parameter


def _new_component(root, name):
    try:
        occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    except RuntimeError as error:
        if 'Part Design documents can only contain one component' in str(error):
            raise RuntimeError(
                'HALO Dock requires a Hybrid Design document because it creates '
                'multiple internal components. Open or convert to Hybrid Design, '
                'then rerun in a fresh empty document.'
            ) from error
        raise
    occurrence.component.name = name
    return occurrence.component


def _set_dimension_expression(dimension, expression):
    dimension.parameter.expression = expression


class _RoundedRectangleGeometry:
    """Entities created for one closed, parameter-driven rounded rectangle."""

    def __init__(self, sketch, lines, arcs):
        self.lines = lines
        self.arcs = arcs
        self.profile = sketch.profiles.item(sketch.profiles.count - 1)


def _rounded_rectangle(
    sketch,
    width,
    height,
    radius,
    width_expression,
    height_expression,
    radius_expression,
):
    """Draw a parameter-driven rounded rectangle centred on the origin."""
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    half_w, half_h = width / 2, height / 2
    r = min(radius, half_w, half_h)
    line_entities = (
        lines.addByTwoPoints(adsk.core.Point3D.create(-half_w + r, half_h, 0), adsk.core.Point3D.create(half_w - r, half_h, 0)),
        lines.addByTwoPoints(adsk.core.Point3D.create(half_w, half_h - r, 0), adsk.core.Point3D.create(half_w, -half_h + r, 0)),
        lines.addByTwoPoints(adsk.core.Point3D.create(half_w - r, -half_h, 0), adsk.core.Point3D.create(-half_w + r, -half_h, 0)),
        lines.addByTwoPoints(adsk.core.Point3D.create(-half_w, -half_h + r, 0), adsk.core.Point3D.create(-half_w, half_h - r, 0)),
    )
    arc_entities = (
        arcs.addByCenterStartSweep(adsk.core.Point3D.create(half_w - r, half_h - r, 0), adsk.core.Point3D.create(half_w - r, half_h, 0), -3.141592653589793 / 2),
        arcs.addByCenterStartSweep(adsk.core.Point3D.create(half_w - r, -half_h + r, 0), adsk.core.Point3D.create(half_w, -half_h + r, 0), -3.141592653589793 / 2),
        arcs.addByCenterStartSweep(adsk.core.Point3D.create(-half_w + r, -half_h + r, 0), adsk.core.Point3D.create(-half_w + r, -half_h, 0), -3.141592653589793 / 2),
        arcs.addByCenterStartSweep(adsk.core.Point3D.create(-half_w + r, half_h - r, 0), adsk.core.Point3D.create(-half_w, half_h - r, 0), -3.141592653589793 / 2),
    )

    # Centre this loop independently of every other loop. The construction
    # diagonal joins opposite arc centres, and constraining the sketch origin
    # to its midpoint removes translation without coupling unequal X/Y insets.
    center_diagonal = lines.addByTwoPoints(
        arc_entities[0].centerSketchPoint,
        arc_entities[2].centerSketchPoint,
    )
    center_diagonal.isConstruction = True
    sketch.geometricConstraints.addMidPoint(sketch.originPoint, center_diagonal)

    dimensions = sketch.sketchDimensions
    horizontal = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    vertical = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    for index in (0, 2):
        line = line_entities[index]
        dimension = dimensions.addDistanceDimension(
            line.startSketchPoint,
            line.endSketchPoint,
            horizontal,
            adsk.core.Point3D.create(0, line.startSketchPoint.geometry.y, 0),
        )
        _set_dimension_expression(dimension, f'{width_expression} - 2 * ({radius_expression})')
    for index in (1, 3):
        line = line_entities[index]
        dimension = dimensions.addDistanceDimension(
            line.startSketchPoint,
            line.endSketchPoint,
            vertical,
            adsk.core.Point3D.create(line.startSketchPoint.geometry.x, 0, 0),
        )
        _set_dimension_expression(dimension, f'{height_expression} - 2 * ({radius_expression})')
    for arc in arc_entities:
        center = arc.centerSketchPoint.geometry
        dimension = dimensions.addRadialDimension(
            arc, adsk.core.Point3D.create(center.x + (1.5 * r), center.y, 0)
        )
        _set_dimension_expression(dimension, radius_expression)

    return _RoundedRectangleGeometry(sketch, line_entities, arc_entities)


def _extrude(component, profile, distance_expression, operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation):
    extrudes = component.features.extrudeFeatures
    feature_input = extrudes.createInput(profile, operation)
    feature_input.setDistanceExtent(
        False, adsk.core.ValueInput.createByString(distance_expression)
    )
    return extrudes.add(feature_input)


def _centered_rectangle_profile(
    sketch,
    design,
    width_name,
    height_name,
    center_x,
    center_y,
):
    """Create a parameter-dimensioned rectangle, centred on expression datums."""
    width = _mm(design, width_name)
    height = _mm(design, height_name)
    # Centre datums must be named parameters too; failing loudly prevents a
    # typo from silently creating fixed, origin-centred geometry.
    cx = _mm(design, center_x)
    cy = _mm(design, center_y)
    lines = sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(cx - width / 2, cy - height / 2, 0),
        adsk.core.Point3D.create(cx + width / 2, cy + height / 2, 0),
    )
    dims = sketch.sketchDimensions
    horizontal = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    vertical = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    # addTwoPointRectangle returns a Python list in Fusion's Python API, not
    # an ObjectCollection. Indexing it directly is required during native use.
    bottom = lines[0]
    right = lines[1]
    _set_dimension_expression(
        dims.addDistanceDimension(
            bottom.startSketchPoint,
            bottom.endSketchPoint,
            horizontal,
            adsk.core.Point3D.create(cx, cy - height, 0),
        ),
        width_name,
    )
    _set_dimension_expression(
        dims.addDistanceDimension(
            right.startSketchPoint,
            right.endSketchPoint,
            vertical,
            adsk.core.Point3D.create(cx + width, cy, 0),
        ),
        height_name,
    )
    lower_left = bottom.startSketchPoint
    x_dim = dims.addDistanceDimension(
        sketch.originPoint,
        lower_left,
        horizontal,
        adsk.core.Point3D.create(cx / 2, cy - height, 0),
    )
    y_dim = dims.addDistanceDimension(
        sketch.originPoint,
        lower_left,
        vertical,
        adsk.core.Point3D.create(cx - width, cy / 2, 0),
    )
    # Distance dimensions are unsigned; the initial point quadrant preserves
    # direction while abs() keeps a legal expression on every side.
    _set_dimension_expression(x_dim, f'abs(({center_x}) - ({width_name}) / 2)')
    _set_dimension_expression(y_dim, f'abs(({center_y}) - ({height_name}) / 2)')
    return sketch.profiles.item(sketch.profiles.count - 1)


def _validate_iteration_2_geometry(design):
    device_thickness = _mm(design, 'device_thickness')
    screen_recess = _mm(design, 'screen_recess')
    front_thickness = _mm(design, 'front_thickness')
    clearance_x = _mm(design, 'pocket_clearance_x')
    clearance_y = _mm(design, 'pocket_clearance_y')
    clearance_z = _mm(design, 'pocket_clearance_z')
    pocket_depth = _mm(design, 'pocket_depth')

    if front_thickness <= screen_recess:
        raise RuntimeError('front_thickness must be greater than screen_recess to leave a rear perimeter skirt.')
    if clearance_x < 0 or clearance_y < 0 or clearance_z <= 0:
        raise RuntimeError('Pocket clearances must be non-negative so the Faceplate skirt stays outside TabletEnvelope.')

    expected_pocket_depth = device_thickness + 2 * clearance_z
    if abs(pocket_depth - expected_pocket_depth) > 1e-6:
        raise RuntimeError('pocket_depth must equal device_thickness + 2 * pocket_clearance_z.')
    selected_slot_width = _mm(design, 'selected_clearance_coupon_slot_width')
    if abs(pocket_depth - selected_slot_width) > 1e-6:
        raise RuntimeError('Selected full-model pocket depth must equal the corresponding clearance-coupon slot width.')

    skirt_rear_z = pocket_depth + screen_recess - front_thickness
    skirt_front_z = skirt_rear_z + (front_thickness - screen_recess)
    lip_rear_z = pocket_depth
    lip_front_z = lip_rear_z + screen_recess

    tolerance = 1e-6
    if skirt_front_z - pocket_depth > tolerance:
        raise RuntimeError('Faceplate perimeter skirt would extend forward into the TabletEnvelope depth.')
    if abs(lip_rear_z - pocket_depth) > tolerance:
        raise RuntimeError('Faceplate lip rear plane must start at the tablet display plane.')
    if abs(lip_front_z - (pocket_depth + screen_recess)) > tolerance:
        raise RuntimeError('Faceplate lip front plane must preserve screen_recess ahead of the display.')

    installed_projection = (
        _mm(design, 'wall_shadow_gap')
        + _mm(design, 'dock_back_thickness')
        + pocket_depth
        + screen_recess
    )
    if abs(installed_projection - _mm(design, 'total_projection_target')) > tolerance:
        raise RuntimeError('Installed layer stack does not meet total_projection_target.')
    if _mm(design, 'wall_shadow_gap') <= 0:
        raise RuntimeError('wall_shadow_gap must create a positive physical separation.')
    if abs(_mm(design, 'guide_depth') - pocket_depth) > tolerance:
        raise RuntimeError('guide_depth must equal pocket_depth.')
    if _mm(design, 'retention_concept_width') <= 0:
        raise RuntimeError('Retention concept width must be positive.')

    device_half_width = _mm(design, 'device_width') / 2
    device_half_height = _mm(design, 'device_height') / 2
    guide_inner_x = _mm(design, 'guide_center_x') - _mm(design, 'dock_side_wall') / 2
    shelf_top_y = _mm(design, 'shelf_center_y') + _mm(design, 'lower_support_thickness') / 2
    retention_inner_x = _mm(design, 'retention_center_x') - _mm(design, 'retention_concept_width') / 2
    guide_top_y = _mm(design, 'guide_center_y') + _mm(design, 'guide_height') / 2
    retention_top_y = _mm(design, 'retention_center_y') + _mm(design, 'retention_concept_height') / 2
    if guide_inner_x < device_half_width - tolerance:
        raise RuntimeError('Side guides would intersect TabletEnvelope.')
    if shelf_top_y > -device_half_height + tolerance:
        raise RuntimeError('Lower support shelf would intersect TabletEnvelope.')
    if retention_inner_x < device_half_width - tolerance:
        raise RuntimeError('Retention concept would intersect TabletEnvelope.')
    if guide_top_y >= device_half_height - tolerance or retention_top_y > device_half_height + tolerance:
        raise RuntimeError('Guide or retention geometry would obstruct the fully open top insertion path.')

    coupon_inner_width = _mm(design, 'coupon_guide_inner_width')
    expected_coupon_width = _mm(design, 'device_width') + 2 * _mm(design, 'coupon_guide_clearance')
    if abs(coupon_inner_width - expected_coupon_width) > tolerance:
        raise RuntimeError('Guide coupon pocket must equal device_width + 2 * coupon_guide_clearance.')
    if _mm(design, 'coupon_guide_clearance') < 0:
        raise RuntimeError('coupon_guide_clearance must be non-negative.')
    if _mm(design, 'coupon_corner_arm_length') <= _mm(design, 'bezel_width'):
        raise RuntimeError('Open corner coupon arms must extend beyond the bezel.')

    dock_half_width = device_half_width + clearance_x + _mm(design, 'dock_side_wall')
    dock_half_height = device_half_height + clearance_y + _mm(design, 'dock_side_wall')
    if (abs(_mm(design, 'camera_keepout_center_x')) + _mm(design, 'camera_keepout_width') / 2 > dock_half_width or
            abs(_mm(design, 'camera_keepout_center_y')) + _mm(design, 'camera_keepout_height') / 2 > dock_half_height or
            _mm(design, 'camera_keepout_depth') >= _mm(design, 'dock_back_thickness')):
        raise RuntimeError('Camera Keep-out must be contained within DockBody and remain blind.')
    if _mm(design, 'button_remaining_wall') <= 0 or _mm(design, 'button_remaining_wall') < 1.5 / 10:
        raise RuntimeError('Button Relief must leave at least approximately 1.5 mm of guide wall.')
    tablet_bottom = -device_half_height
    if _mm(design, 'cable_pocket_center_y') + _mm(design, 'cable_pocket_run_depth') / 2 > tablet_bottom + tolerance:
        raise RuntimeError('Cable Pocket must not intersect TabletEnvelope above the USB edge.')
    shelf_left = -_mm(design, 'shelf_width') / 2
    shelf_right = _mm(design, 'shelf_width') / 2
    slot_left = _mm(design, 'speaker_slot_center_x') - _mm(design, 'speaker_slot_width') / 2
    slot_right = _mm(design, 'speaker_slot_center_x') + _mm(design, 'speaker_slot_width') / 2
    if slot_left < shelf_left or slot_right > shelf_right:
        raise RuntimeError('Speaker slot must be contained within the lower shelf.')


def _dual_lock_measurement(design, required):
    """Validate the selected physical wall stack; zero explicitly means unknown."""
    measured = _mm(design, 'dual_lock_measured_engaged_thickness')
    shadow_gap = _mm(design, 'wall_shadow_gap')
    dock_back = _mm(design, 'dock_back_thickness')
    if measured <= 0:
        if required:
            raise RuntimeError(
                'BLOCKED — exact Dual Lock pair must be selected and measured before print release.'
            )
        return None
    recess = measured - shadow_gap
    if recess < 0:
        raise RuntimeError('dual_lock_recess_depth cannot be negative; measured thickness must be at least wall_shadow_gap.')
    if recess >= dock_back:
        raise RuntimeError('Dual Lock recess would pass through dock_back_thickness.')
    remaining = dock_back - recess
    if remaining <= 0:
        raise RuntimeError('Dual Lock recess must leave positive structural backing thickness.')
    if abs(_mm(design, 'dual_lock_center_x') + _mm(design, 'dual_lock_center_x_left')) > 1e-6:
        raise RuntimeError('Left and right Dual Lock fields must remain symmetric.')
    if shadow_gap <= 0:
        raise RuntimeError('An open visible shadow gap is required around the discrete pads.')
    return recess, remaining


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(
        component.xYConstructionPlane,
        adsk.core.ValueInput.createByString(expression),
    )
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _offset_xz_plane(component, expression, name):
    """Offset from XZ; its positive normal points toward negative model Y."""
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(
        component.xZConstructionPlane,
        adsk.core.ValueInput.createByString(expression),
    )
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _cut_speaker_slot(component, design, plane_offset, name):
    """Cut the controlled 20 x 5 mm XZ opening through the full shelf Y wall."""
    width = _mm(design, 'speaker_slot_width')
    height = _mm(design, 'speaker_slot_height')
    shelf_wall = _mm(design, 'lower_support_thickness')
    if abs(width - 2.0) > 1e-6 or abs(height - 0.5) > 1e-6:
        raise RuntimeError('Speaker slot XZ profile must remain exactly 20 x 5 mm.')
    if width <= 0 or height <= 0 or height > _mm(design, 'guide_depth'):
        raise RuntimeError('Speaker slot must be a positive XZ opening contained in shelf depth.')
    if shelf_wall <= 0:
        raise RuntimeError('Speaker slot through-cut requires positive lower_support_thickness.')
    plane = _offset_xz_plane(component, plane_offset, name + ' outer Y face')
    sketch = component.sketches.add(plane)
    sketch.name = name + ' 20 x 5 mm XZ profile'
    profile = _centered_rectangle_profile(
        sketch, design, 'speaker_slot_width', 'speaker_slot_height',
        'speaker_slot_center_x', 'speaker_slot_center_z')
    cut = _extrude(
        component, profile, 'lower_support_thickness',
        adsk.fusion.FeatureOperations.CutFeatureOperation)
    cut.name = name + ' through complete shelf Y thickness'
    if abs(cut.extentOne.distance.value - shelf_wall) > 1e-6:
        raise RuntimeError(
            'Speaker slot cut must traverse all of lower_support_thickness; '
            'residual shelf material would block the opening.')
    # A successful CutFeature over exactly the shelf-wall parameter leaves no
    # residual shelf thickness in this 20 x 5 mm XZ opening. Fusion raises if
    # the profile misses the shelf or the requested cut cannot be constructed.
    return cut


def _build_tablet_envelope(design, root):
    component = _new_component(root, 'TabletEnvelope')
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'Tablet outline (reference envelope)'
    geometry = _rounded_rectangle(
        sketch,
        _mm(design, 'device_width'),
        _mm(design, 'device_height'),
        _mm(design, 'device_corner_radius'),
        'device_width',
        'device_height',
        'device_corner_radius',
    )
    body = _extrude(component, geometry.profile, 'device_thickness').bodies.item(0)
    body.name = 'SM-X130 reference envelope - not for manufacture'
    return component


def _cut_cable_profile(component, design, plane, center_y, distance, name):
    """Cut the conservative controlled rectangular cable clearance."""
    sketch = component.sketches.add(plane)
    sketch.name = name + ' rectangular footprint'
    cut = _extrude(
        component,
        _centered_rectangle_profile(
            sketch, design, 'cable_pocket_width', 'cable_pocket_run_depth',
            'cable_pocket_center_x', center_y),
        distance, adsk.fusion.FeatureOperations.CutFeatureOperation)
    cut.name = name + ' - conservative rectangular clearance'
    return cut


def _validate_timeline_health(design):
    """Block export for every unhealthy sketch or feature after recomputation."""
    unhealthy = []
    components = [design.rootComponent]
    for index in range(design.rootComponent.allOccurrences.count):
        component = design.rootComponent.allOccurrences.item(index).component
        if component not in components:
            components.append(component)
    error_state = adsk.fusion.FeatureHealthStates.ErrorFeatureHealthState
    warning_state = adsk.fusion.FeatureHealthStates.WarningFeatureHealthState
    for component in components:
        for collection in (component.sketches, component.features):
            for index in range(collection.count):
                entity = collection.item(index)
                if entity.healthState in (error_state, warning_state):
                    unhealthy.append(
                        '{} / {}: healthState={} — {}'.format(
                            component.name, entity.name, entity.healthState,
                            entity.errorOrWarningMessage))
    if unhealthy:
        raise RuntimeError(
            'Export blocked by unhealthy Fusion timeline entities:\n' +
            '\n'.join(unhealthy))


def _create_temporary_cable_envelope(design):
    """Create and validate a non-timeline rectangular interference body."""
    width = _mm(design, 'cable_pocket_width')
    run_depth = _mm(design, 'cable_pocket_run_depth')
    height = _mm(design, 'cable_pocket_height')
    center_x = _mm(design, 'cable_pocket_center_x')
    center_y = _mm(design, 'cable_pocket_center_y')
    center = adsk.core.Point3D.create(center_x, center_y, height / 2)
    length_direction = adsk.core.Vector3D.create(1, 0, 0)
    width_direction = adsk.core.Vector3D.create(0, 1, 0)
    oriented_box = adsk.core.OrientedBoundingBox3D.create(
        center, length_direction, width_direction, width, run_depth, height)
    manager = adsk.fusion.TemporaryBRepManager.get()
    body = manager.createBox(oriented_box)
    expected_min = (center_x - width / 2, center_y - run_depth / 2, 0.0)
    expected_max = (center_x + width / 2, center_y + run_depth / 2, height)
    if (not body or not body.isTemporary or not body.isValid or
            not body.isSolid or body.volume <= 0):
        raise RuntimeError(
            'Temporary cable envelope must be a valid, solid, positive-volume '
            'TemporaryBRep body.')
    bounds = body.preciseBoundingBox
    actual = (
        bounds.minPoint.x, bounds.minPoint.y, bounds.minPoint.z,
        bounds.maxPoint.x, bounds.maxPoint.y, bounds.maxPoint.z)
    expected = expected_min + expected_max
    tolerance = 0.01  # Fusion internal centimetres: 0.1 mm; do not increase.
    if any(abs(value - target) > tolerance
           for value, target in zip(actual, expected)):
        raise RuntimeError(
            'Temporary cable envelope has incorrect world-space bounds. '
            'Expected min/max (mm): {}; actual min/max (mm): {}.'.format(
                tuple(value * 10 for value in expected),
                tuple(value * 10 for value in actual)))
    return body


def _validate_cable_clearance(design, printable_components):
    """Intersect printable body copies with a validated temporary envelope."""
    envelope_body = _create_temporary_cable_envelope(design)
    manager = adsk.fusion.TemporaryBRepManager.get()
    for component in printable_components:
        for index in range(component.bRepBodies.count):
            intersection = manager.copy(envelope_body)
            printable = manager.copy(component.bRepBodies.item(index))
            intersects = manager.booleanOperation(
                intersection, printable,
                adsk.fusion.BooleanTypes.IntersectionBooleanType)
            if intersects and intersection.physicalProperties.volume > 1e-9:
                raise RuntimeError(
                    'Temporary cable envelope intersects ' + component.name +
                    ' after controlled cuts; printable export is blocked.')
    envelope_body = None  # Drop the only temporary reference before export.


def _ring_profile(sketch):
    ring_profiles = []
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        if profile.profileLoops.count == 2:
            ring_profiles.append(profile)
    if len(ring_profiles) != 1:
        raise RuntimeError(
            'Expected exactly one closed two-loop Faceplate ring profile; found '
            + str(len(ring_profiles)) + '.'
        )
    return ring_profiles[0]


def _build_faceplate(design, root):
    # Split the Faceplate so the visible lip sits in front of the tablet while
    # the remaining structural depth is only a perimeter skirt outside the
    # TabletEnvelope. This preserves the 0.8 mm recess without body collision.
    component = _new_component(root, 'Faceplate')
    lip_rear_plane = _offset_plane(
        component,
        'pocket_depth',
        'Faceplate lip rear plane (tablet display datum)',
    )
    skirt_rear_plane = _offset_plane(
        component,
        'pocket_depth + screen_recess - front_thickness',
        'Faceplate skirt rear plane (parameter driven)',
    )

    device_width = _mm(design, 'device_width')
    device_height = _mm(design, 'device_height')
    device_radius = _mm(design, 'device_corner_radius')
    bezel = _mm(design, 'bezel_width')
    lip = _mm(design, 'inner_lip_overlap')
    clearance_x = _mm(design, 'pocket_clearance_x')
    clearance_y = _mm(design, 'pocket_clearance_y')

    lip_sketch = component.sketches.add(lip_rear_plane)
    lip_sketch.name = 'Faceplate visible lip and display opening'
    _rounded_rectangle(
        lip_sketch,
        device_width + (2 * bezel),
        device_height + (2 * bezel),
        device_radius + bezel,
        'device_width + 2 * bezel_width',
        'device_height + 2 * bezel_width',
        'device_corner_radius + bezel_width',
    )
    _rounded_rectangle(
        lip_sketch,
        device_width - (2 * lip),
        device_height - (2 * lip),
        max(device_radius - lip, 0),
        'device_width - 2 * inner_lip_overlap',
        'device_height - 2 * inner_lip_overlap',
        'device_corner_radius - inner_lip_overlap',
    )
    lip_feature = _extrude(component, _ring_profile(lip_sketch), 'screen_recess')
    lip_feature.name = 'Visible front lip - display recess'
    lip_feature.bodies.item(0).name = 'HALO Faceplate Rev A - front lip'

    skirt_sketch = component.sketches.add(skirt_rear_plane)
    skirt_sketch.name = 'Faceplate rear perimeter skirt outside TabletEnvelope'
    _rounded_rectangle(
        skirt_sketch,
        device_width + (2 * bezel),
        device_height + (2 * bezel),
        device_radius + bezel,
        'device_width + 2 * bezel_width',
        'device_height + 2 * bezel_width',
        'device_corner_radius + bezel_width',
    )
    _rounded_rectangle(
        skirt_sketch,
        device_width + (2 * clearance_x),
        device_height + (2 * clearance_y),
        device_radius + clearance_x,
        'device_width + 2 * pocket_clearance_x',
        'device_height + 2 * pocket_clearance_y',
        'device_corner_radius + pocket_clearance_x',
    )
    skirt_feature = _extrude(
        component,
        _ring_profile(skirt_sketch),
        'front_thickness - screen_recess',
    )
    skirt_feature.name = 'Rear perimeter skirt - outside tablet envelope'
    skirt_feature.bodies.item(0).name = 'HALO Faceplate Rev A - rear perimeter skirt'
    _cut_cable_profile(
        component, design, skirt_rear_plane, 'cable_pocket_center_y',
        'front_thickness - screen_recess',
        'Faceplate rear-skirt USB-C cable clearance')
    return component


def _build_dock_body(design, root):
    # The top remains entirely crossbar-free: insertion is constrained only by
    # side guides, a lower shelf, and explicitly non-final side detent studies.
    component = _new_component(root, 'DockBody')
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'Preliminary DockBody backing outline'
    clearance_x = _mm(design, 'pocket_clearance_x')
    clearance_y = _mm(design, 'pocket_clearance_y')
    wall = _mm(design, 'dock_side_wall')
    geometry = _rounded_rectangle(
        sketch,
        _mm(design, 'device_width') + (2 * clearance_x) + (2 * wall),
        _mm(design, 'device_height') + (2 * clearance_y) + (2 * wall),
        _mm(design, 'device_corner_radius') + clearance_x + wall,
        'device_width + 2 * pocket_clearance_x + 2 * dock_side_wall',
        'device_height + 2 * pocket_clearance_y + 2 * dock_side_wall',
        'device_corner_radius + pocket_clearance_x + dock_side_wall',
    )
    feature = _extrude(component, geometry.profile, '-dock_back_thickness')
    feature.name = 'Iteration 2 projection-controlled backing'
    feature.bodies.item(0).name = 'HALO DockBody Rev A - backing'

    # Blind camera-island relief: it starts at the tablet rear datum and cuts
    # only part-way into the backing. It is deliberately not an optical hole.
    camera_sketch = component.sketches.add(component.xYConstructionPlane)
    camera_sketch.name = 'Blind rear camera island keep-out'
    camera_relief = _extrude(
        component,
        _centered_rectangle_profile(
            camera_sketch, design, 'camera_keepout_width',
            'camera_keepout_height', 'camera_keepout_center_x',
            'camera_keepout_center_y'),
        '-camera_keepout_depth',
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    camera_relief.name = 'Camera island blind load relief - no optical opening'

    # The rear portion of the generic USB cable pocket opens at the bottom of
    # DockBody and joins the lower-shelf opening below. No connector model is
    # encoded in this deliberately generous envelope.
    _cut_cable_profile(
        component, design, component.xYConstructionPlane,
        'cable_pocket_center_y', '-dock_back_thickness',
        'DockBody backing USB-C cable clearance to rear management volume')

    # A measured stack thicker than the visible gap is received by two
    # discrete rear pockets.  The selected Dual Lock then ends on the pocket
    # floor, providing wall -> Dual Lock -> DockBody contact with no air gap.
    measurement = _dual_lock_measurement(design, required=False)
    if measurement and measurement[0] > 0:
        rear_plane = _offset_plane(component, '-dock_back_thickness', 'DockBody rear mounting plane')
        for side, center_x in (
            ('Right', 'dual_lock_center_x'),
            ('Left', 'dual_lock_center_x_left'),
        ):
            recess_sketch = component.sketches.add(rear_plane)
            recess_sketch.name = side + ' measured Dual Lock recess footprint'
            recess = _extrude(
                component,
                _centered_rectangle_profile(
                    recess_sketch, design, 'dual_lock_pad_width',
                    'dual_lock_pad_height', center_x, 'dual_lock_center_y'
                ),
                'dual_lock_recess_depth',
                adsk.fusion.FeatureOperations.CutFeatureOperation,
            )
            recess.name = side + ' Dual Lock recess - measured stack'

    for side, center_x in (
        ('Right', 'guide_center_x'),
        ('Left', 'guide_center_x_left'),
    ):
        guide_sketch = component.sketches.add(component.xYConstructionPlane)
        guide_sketch.name = side + ' side guide footprint'
        guide = _extrude(
            component,
            _centered_rectangle_profile(
                guide_sketch,
                design,
                'dock_side_wall',
                'guide_height',
                center_x,
                'guide_center_y',
            ),
            'guide_depth',
        )
        guide.name = side + ' side guide - open top'
        guide.bodies.item(0).name = side + ' side guide'

    button_sketch = component.sketches.add(component.xYConstructionPlane)
    button_sketch.name = 'Right guide blind internal power and volume relief'
    button_relief = _extrude(
        component,
        _centered_rectangle_profile(
            button_sketch, design, 'button_relief_depth',
            'button_relief_height', 'button_relief_center_x',
            'button_relief_center_y'),
        'guide_depth',
        adsk.fusion.FeatureOperations.CutFeatureOperation,
    )
    button_relief.name = 'Internal button relief - no finger access or through-hole'

    shelf_sketch = component.sketches.add(component.xYConstructionPlane)
    shelf_sketch.name = 'Lower support shelf footprint'
    shelf = _extrude(
        component,
        _centered_rectangle_profile(
            shelf_sketch,
            design,
            'shelf_width',
            'lower_support_thickness',
            'dock_center_x',
            'shelf_center_y',
        ),
        'guide_depth',
    )
    shelf.name = 'Lower support shelf'
    shelf.bodies.item(0).name = 'Lower tablet support shelf'

    _cut_speaker_slot(
        component, design, 'speaker_slot_plane_offset',
        'One simple lower-speaker opening - no grille')

    _cut_cable_profile(
        component, design, component.xYConstructionPlane,
        'cable_pocket_center_y', 'cable_pocket_height',
        'Lower-shelf USB-C connector housing clearance')

    for side, center_x in (
        ('Right', 'retention_center_x'),
        ('Left', 'retention_center_x_left'),
    ):
        retention_sketch = component.sketches.add(component.xYConstructionPlane)
        retention_sketch.name = side + ' non-final retention concept footprint'
        retention = _extrude(
            component,
            _centered_rectangle_profile(
                retention_sketch,
                design,
                'retention_concept_width',
                'retention_concept_height',
                center_x,
                'retention_center_y',
            ),
            'guide_depth',
        )
        retention.name = side + ' upper side detent concept - NOT FINAL'
        retention.bodies.item(0).name = side + ' retention concept - not released'
    return component


def _build_wall_interface(design, root):
    component = _new_component(root, 'WallInterface')
    component.description = 'Measured, discrete 3M Dual Lock pair envelopes; reference only, never printable spacer geometry.'
    wall_plane = _offset_plane(
        component,
        '-dock_back_thickness - wall_shadow_gap',
        'Wall datum - establishes actual shadow gap',
    )
    for side, center_x in (
        ('Right', 'dual_lock_center_x'),
        ('Left', 'dual_lock_center_x_left'),
    ):
        sketch = component.sketches.add(wall_plane)
        sketch.name = side + ' hidden Dual Lock field'
        field = _extrude(
            component,
            _centered_rectangle_profile(
                sketch,
                design,
                'dual_lock_pad_width',
                'dual_lock_pad_height',
                center_x,
                'dual_lock_center_y',
            ),
            'dual_lock_measured_engaged_thickness',
        )
        field.name = side + ' selected 3M Dual Lock engaged envelope'
        field.bodies.item(0).name = side + ' measured mounting stack - NOT PRINTABLE'
    return component


def _open_corner_l_profile(sketch, design, band_expression, radius_parameter):
    """Create one closed, origin-datumed L with equal parameter-driven arms."""
    radius = _mm(design, radius_parameter) + _mm(design, 'bezel_width')
    arm = _mm(design, 'coupon_corner_arm_length')
    # Both current band expressions are simple sums/differences of known
    # parameters; use their evaluated value only to seed the constrained sketch.
    if band_expression == 'bezel_width + inner_lip_overlap':
        band = _mm(design, 'bezel_width') + _mm(design, 'inner_lip_overlap')
    else:
        band = _mm(design, 'bezel_width') - _mm(design, 'pocket_clearance_x')
    if band <= 0 or band >= radius or arm <= radius:
        raise RuntimeError(
            'Open corner coupon requires 0 < band width < outer radius < arm length.')

    # Put the theoretical sharp outer corner on the sketch origin.  Dimension
    # each arm endpoint directly from that fixed datum: construction lines on
    # the arm axes would overlap the real edges and split Fusion's profile.
    center = (-radius, -radius)
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs
    outer_arc = arcs.addByCenterStartSweep(
        adsk.core.Point3D.create(-radius, -radius, 0),
        adsk.core.Point3D.create(0, -radius, 0),
        3.141592653589793 / 2,
    )
    outer_top = lines.addByTwoPoints(
        adsk.core.Point3D.create(-arm, 0, 0), outer_arc.endSketchPoint)
    outer_side = lines.addByTwoPoints(
        outer_arc.startSketchPoint, adsk.core.Point3D.create(0, -arm, 0))
    side_end = lines.addByTwoPoints(
        outer_side.endSketchPoint, adsk.core.Point3D.create(-band, -arm, 0))
    inner_arc = arcs.addByCenterStartSweep(
        adsk.core.Point3D.create(center[0], center[1], 0),
        adsk.core.Point3D.create(-band, -radius, 0),
        3.141592653589793 / 2,
    )
    inner_side = lines.addByTwoPoints(
        side_end.endSketchPoint, inner_arc.startSketchPoint)
    inner_top = lines.addByTwoPoints(
        inner_arc.endSketchPoint, adsk.core.Point3D.create(-arm, -band, 0))
    top_end = lines.addByTwoPoints(inner_top.endSketchPoint, outer_top.startSketchPoint)

    constraints = sketch.geometricConstraints
    constraints.addTangent(outer_top, outer_arc)
    constraints.addTangent(outer_arc, outer_side)
    constraints.addTangent(inner_side, inner_arc)
    constraints.addTangent(inner_arc, inner_top)
    constraints.addConcentric(outer_arc, inner_arc)
    constraints.addHorizontal(outer_top)
    constraints.addHorizontal(side_end)
    constraints.addHorizontal(inner_top)
    constraints.addVertical(top_end)

    dims = sketch.sketchDimensions
    horizontal = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
    vertical = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation
    horizontal_arm_dimension = dims.addDistanceDimension(
        sketch.originPoint, outer_top.startSketchPoint,
        horizontal, adsk.core.Point3D.create(-arm / 2, radius, 0))
    _set_dimension_expression(
        horizontal_arm_dimension, 'coupon_corner_arm_length')
    vertical_arm_dimension = dims.addDistanceDimension(
        sketch.originPoint, outer_side.endSketchPoint,
        vertical, adsk.core.Point3D.create(radius, -arm / 2, 0))
    _set_dimension_expression(vertical_arm_dimension, 'coupon_corner_arm_length')
    band_dimension = dims.addDistanceDimension(
        top_end.startSketchPoint, top_end.endSketchPoint, vertical,
        adsk.core.Point3D.create(-arm - band, -band / 2, 0))
    _set_dimension_expression(band_dimension, band_expression)
    outer_radial = dims.addRadialDimension(
        outer_arc, adsk.core.Point3D.create(-radius, radius / 2, 0))
    _set_dimension_expression(outer_radial, radius_parameter + ' + bezel_width')

    if sketch.profiles.count != 1:
        raise RuntimeError(
            'Open corner sketch must resolve to exactly one closed profile; found '
            + str(sketch.profiles.count) + '.')
    return sketch.profiles.item(0)


def _build_faceplate_corner_coupon(design, root, candidate_id, radius_parameter):
    component = _new_component(root, 'Coupon_Faceplate_Open_Corner_L_' + candidate_id)
    component.description = 'Open L coupon: explicit ' + radius_parameter + ' candidate, lip, recess, pocket clearance, and joined rear skirt.'
    lip_plane = _offset_plane(component, 'pocket_depth', 'Coupon lip display datum')
    lip_sketch = component.sketches.add(lip_plane)
    lip_sketch.name = 'OPEN L lip profile - static validation forbids ring loops'
    lip = _extrude(component, _open_corner_l_profile(
        lip_sketch, design, 'bezel_width + inner_lip_overlap', radius_parameter), 'screen_recess')
    lip.name = 'Open L visible lip and front surface'
    skirt_plane = _offset_plane(
        component, 'pocket_depth + screen_recess - front_thickness',
        'Coupon rear skirt datum')
    skirt_sketch = component.sketches.add(skirt_plane)
    skirt_sketch.name = 'OPEN L rear skirt profile - pocket side remains open'
    skirt = _extrude(component, _open_corner_l_profile(
        skirt_sketch, design, 'bezel_width - pocket_clearance_x', radius_parameter),
        'front_thickness - screen_recess',
        adsk.fusion.FeatureOperations.JoinFeatureOperation)
    skirt.name = 'Open L rear perimeter skirt and pocket clearance witness'
    return component


def _validate_open_corner_coupon(component, design):
    """Reject a disconnected or collapsed native coupon before any export."""
    if component.bRepBodies.count != 1:
        raise RuntimeError(
            'Open corner coupon export blocked: expected exactly one joined BRep '
            'body, found ' + str(component.bRepBodies.count) +
            '. Regenerate and verify the rear-skirt Join operation in Fusion.')
    bounds = component.bRepBodies.item(0).boundingBox
    width = bounds.maxPoint.x - bounds.minPoint.x
    height = bounds.maxPoint.y - bounds.minPoint.y
    expected = _mm(design, 'coupon_corner_arm_length')
    tolerance = 0.01  # Fusion internal centimetres: 0.1 mm.
    if abs(width - expected) > tolerance or abs(height - expected) > tolerance:
        raise RuntimeError(
            'Open corner coupon export blocked: expected XY extents of '
            'coupon_corner_arm_length ({:.3f} x {:.3f} mm), got {:.3f} x '
            '{:.3f} mm. Inspect the open-L profile constraints before export.'.format(
                expected * 10, expected * 10, width * 10, height * 10))


def _build_guide_shelf_coupon(design, root):
    component = _new_component(root, 'Coupon_Side_Guide_Lower_Shelf')
    component.description = 'Full-width guide coupon with the conservative rectangular cable pocket and single speaker slot.'
    shelf_sketch = component.sketches.add(component.xYConstructionPlane)
    shelf = _extrude(component, _centered_rectangle_profile(
        shelf_sketch, design, 'coupon_shelf_width', 'lower_support_thickness',
        'dock_center_x', 'coupon_shelf_center_y'), 'guide_depth')
    shelf.name = 'Full pocket-width lower seating shelf and rail connector'
    for side, center_x in (
        ('Right', 'coupon_guide_center_x'),
        ('Left', 'coupon_guide_center_x_left'),
    ):
        sketch = component.sketches.add(component.xYConstructionPlane)
        rail = _extrude(component, _centered_rectangle_profile(
            sketch, design, 'dock_side_wall', 'coupon_guide_length',
            center_x, 'coupon_guide_center_y'), 'guide_depth',
            adsk.fusion.FeatureOperations.JoinFeatureOperation)
        rail.name = side + ' shortened guide coupon rail'
    _cut_cable_profile(
        component, design, component.xYConstructionPlane,
        'coupon_cable_center_y', 'cable_pocket_height',
        'Guide coupon USB-C cable clearance')
    _cut_speaker_slot(
        component, design, 'coupon_speaker_slot_plane_offset',
        'Guide coupon single lower-speaker opening')
    return component


def _build_faceplate_cable_coupon(design, root):
    """Build one connected bottom-centre Faceplate/cable fit article."""
    component = _new_component(root, 'Coupon_Faceplate_USB_C_Cable_Pocket')
    component.description = (
        'Real Faceplate lip/skirt depths and controlled rectangular cable cut; '
        'verify tablet insertion, connector housing, bend freedom, and no skirt contact.')
    lip_plane = _offset_plane(component, 'pocket_depth', 'Cable coupon lip rear datum')
    lip_sketch = component.sketches.add(lip_plane)
    lip = _extrude(
        component, _centered_rectangle_profile(
            lip_sketch, design, 'faceplate_cable_coupon_width',
            'faceplate_cable_coupon_band_height',
            'faceplate_cable_coupon_center_x', 'faceplate_cable_coupon_center_y'),
        'screen_recess')
    lip.name = 'Real visible Faceplate bottom lip segment'
    skirt_plane = _offset_plane(
        component, 'pocket_depth + screen_recess - front_thickness',
        'Cable coupon rear-skirt datum')
    skirt_sketch = component.sketches.add(skirt_plane)
    skirt = _extrude(
        component, _centered_rectangle_profile(
            skirt_sketch, design, 'faceplate_cable_coupon_width',
            'faceplate_cable_coupon_band_height',
            'faceplate_cable_coupon_center_x', 'faceplate_cable_coupon_center_y'),
        'front_thickness - screen_recess',
        adsk.fusion.FeatureOperations.JoinFeatureOperation)
    skirt.name = 'Joined real Faceplate rear-skirt segment'
    _cut_cable_profile(
        component, design, skirt_plane, 'cable_pocket_center_y',
        'front_thickness - screen_recess',
        'Faceplate coupon rear-skirt USB-C clearance')
    if component.bRepBodies.count != 1:
        raise RuntimeError(
            'Faceplate cable coupon must remain one printable BRep after its cable cut.')
    return component


def _build_clearance_coupon(design, root, clearance_text):
    safe = clearance_text.replace('.', '_')
    component = _new_component(root, 'Coupon_Clearance_' + safe + 'mm')
    component.description = 'Short physical slot gauge; evaluate on the real tablet at 100% scale.'
    # A dedicated parameter preserves each candidate rather than mutating the
    # selected assembly clearance.
    parameter_name = 'coupon_fit_clearance_' + safe
    center_right = 'coupon_fit_center_x_' + safe
    center_left = center_right + '_left'
    base_width = 'coupon_fit_base_width_' + safe
    rail_center_y = 'coupon_fit_rail_center_y_' + safe
    base_center_y = 'coupon_fit_base_center_y_' + safe
    _ensure_parameter(design, parameter_name, clearance_text + ' mm',
                      'Per-side candidate clearance')
    _ensure_parameter(
        design, center_right,
        f'device_thickness / 2 + {parameter_name} + coupon_fit_rail_width / 2',
        'Right clearance-gauge rail centre magnitude')
    _ensure_parameter(design, center_left, '-' + center_right,
                      'Left clearance-gauge rail centre')
    _ensure_parameter(
        design, base_width,
        f'device_thickness + 2 * {parameter_name} + 2 * coupon_fit_rail_width',
        'Connected clearance-gauge outside width')
    _ensure_parameter(design, rail_center_y, '-coupon_fit_base_height / 2',
                      'Rail centre overlaps the connecting base')
    _ensure_parameter(
        design, base_center_y,
        '-coupon_fit_rail_length / 2 - coupon_fit_base_height / 2',
        'Connecting base centre below the insertion slot')

    base_sketch = component.sketches.add(component.xYConstructionPlane)
    base = _extrude(component, _centered_rectangle_profile(
        base_sketch, design, base_width, 'coupon_fit_base_height',
        'dock_center_x', base_center_y), 'lower_support_thickness')
    base.name = 'Connected fit-gauge base ' + clearance_text + ' mm'
    for side, center_x in (('Right', center_right), ('Left', center_left)):
        sketch = component.sketches.add(component.xYConstructionPlane)
        rail = _extrude(component, _centered_rectangle_profile(
            sketch, design, 'coupon_fit_rail_width', 'coupon_fit_rail_length',
            center_x, rail_center_y), 'lower_support_thickness',
            adsk.fusion.FeatureOperations.JoinFeatureOperation)
        rail.name = side + ' fit gauge rail ' + clearance_text + ' mm'
    return component


def _build_wall_coupon_field(design, root, side, center_x):
    """Build one controlled wall-stack test article with exactly one solid."""
    measurement = _dual_lock_measurement(design, required=True)
    component = _new_component(root, 'Coupon_Wall_Stack_Shadow_Gap_' + side)
    component.description = (
        side + ' single-field wall-stack article; separately exported so no '
        'loose bodies or uncontrolled relative spacing enter one vendor file.')
    sketch = component.sketches.add(component.xYConstructionPlane)
    backing = _extrude(component, _centered_rectangle_profile(
        sketch, design, 'wall_coupon_backing_width', 'wall_coupon_backing_height',
        center_x, 'dual_lock_center_y'), '-dock_back_thickness')
    backing.name = side + ' discrete wall coupon backing field'
    if measurement[0] > 0:
        rear_plane = _offset_plane(
            component, '-dock_back_thickness', side + ' coupon rear plane')
        pocket_sketch = component.sketches.add(rear_plane)
        pocket = _extrude(component, _centered_rectangle_profile(
            pocket_sketch, design, 'dual_lock_pad_width', 'dual_lock_pad_height',
            center_x, 'dual_lock_center_y'), 'dual_lock_recess_depth',
            adsk.fusion.FeatureOperations.CutFeatureOperation)
        pocket.name = side + ' measured recess; bond pad to floor'
    else:
        backing.name += ' - zero recess; pad bonds to rear face'
    return component


def _build_assembly_placeholder(root):
    assembly = _new_component(root, 'Assembly')
    assembly.description = 'Placeholder: assembly joints, final latch, and service motion are deferred.'


def _export_stl(export_manager, component, path):
    options = export_manager.createSTLExportOptions(component, path)
    options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    export_manager.execute(options)


def _export_step(export_manager, component, path):
    """Export one controlled printable component, never the design root."""
    options = export_manager.createSTEPExportOptions(path, component)
    export_manager.execute(options)


def _export_printable_part(export_manager, component, output_dir, part_id):
    """Keep vendor STEP/STL names and component scope in one fail-safe path."""
    _export_step(export_manager, component, os.path.join(output_dir, part_id + '.step'))
    _export_stl(export_manager, component, os.path.join(output_dir, part_id + '.stl'))


def _validate_full_size_release(design):
    _dual_lock_measurement(design, required=True)
    incomplete = [name for name, passed in FULL_SIZE_RELEASE_GATES.items() if not passed]
    if incomplete:
        raise RuntimeError(
            'FULL_SIZE_PRINT_CANDIDATE blocked; unmet evidence gates: ' + ', '.join(incomplete)
        )


def _export_outputs(design, coupons, faceplate, dock_body):
    if EXPORT_MODE not in (COUPONS_ONLY, FULL_SIZE_PRINT_CANDIDATE):
        raise RuntimeError('Unknown EXPORT_MODE: ' + str(EXPORT_MODE))
    root_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'HALO_Dock_Rev_A')
    output_dir = os.path.join(
        root_dir, 'coupons' if EXPORT_MODE == COUPONS_ONLY else 'print-candidate')
    os.makedirs(output_dir, exist_ok=True)
    export_manager = design.exportManager
    if not design.computeAll():
        raise RuntimeError('Export blocked because design.computeAll() returned False.')
    _validate_timeline_health(design)
    _validate_cable_clearance(design, (faceplate, dock_body))
    if EXPORT_MODE == COUPONS_ONLY:
        # Each tuple is one printable component and one controlled Part ID.
        # Full parts and root/reference geometry are absent from this list.
        for component, part_id in coupons:
            if part_id in (
                COUPON_PART_IDS['corner_R8_0'],
                COUPON_PART_IDS['corner_R8_5'],
                COUPON_PART_IDS['corner_R9_0'],
            ):
                _validate_open_corner_coupon(component, design)
            _export_printable_part(export_manager, component, output_dir, part_id)
    else:
        _validate_full_size_release(design)
        # There is intentionally no root-component STEP/F3D export. The design
        # root contains TabletEnvelope, coupons, WallInterface references, and
        # Assembly placeholder content that is prohibited in vendor output.
        authorized_parts = (
            (faceplate, FULL_SIZE_PART_IDS['faceplate']),
            (dock_body, FULL_SIZE_PART_IDS['dock_body']),
        )
        for component, part_id in authorized_parts:
            _export_printable_part(export_manager, component, output_dir, part_id)
    return output_dir


def run(context):
    try:
        design = adsk.fusion.Design.cast(APP.activeProduct)
        if not design:
            raise RuntimeError('Open or create a Fusion Design before running this script.')
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent
        _set_parameters(design)
        _validate_iteration_2_geometry(design)
        _build_tablet_envelope(design, root)
        faceplate = _build_faceplate(design, root)
        dock_body = _build_dock_body(design, root)
        if _dual_lock_measurement(design, required=False):
            _build_wall_interface(design, root)
        _build_assembly_placeholder(root)
        coupons = []
        for clearance in ('0.2', '0.3', '0.4'):
            coupons.append((_build_clearance_coupon(design, root, clearance),
                COUPON_PART_IDS[clearance]))
        for candidate_id, radius_parameter in (
            ('R8_0', 'coupon_corner_radius_R8_0'),
            ('R8_5', 'coupon_corner_radius_R8_5'),
            ('R9_0', 'coupon_corner_radius_R9_0'),
        ):
            coupons.append((
                _build_faceplate_corner_coupon(
                    design, root, candidate_id, radius_parameter),
                COUPON_PART_IDS['corner_' + candidate_id],
            ))
        coupons.append((_build_guide_shelf_coupon(design, root),
            COUPON_PART_IDS['guide']))
        coupons.append((_build_faceplate_cable_coupon(design, root),
            COUPON_PART_IDS['faceplate_cable']))
        if _dual_lock_measurement(design, required=False):
            coupons.extend((
                (_build_wall_coupon_field(
                    design, root, 'Right', 'wall_coupon_center_x'),
                 COUPON_PART_IDS['wall_right']),
                (_build_wall_coupon_field(
                    design, root, 'Left', 'wall_coupon_center_x_left'),
                 COUPON_PART_IDS['wall_left']),
            ))
        output_dir = _export_outputs(design, coupons, faceplate, dock_body)
        if UI:
            message = 'HALO Dock Rev A generated in ' + EXPORT_MODE + ' mode and exported to:\n' + output_dir
            if not _dual_lock_measurement(design, required=False):
                message += ('\n\nWall coupon omitted: BLOCKED — exact Dual Lock pair must be selected '
                            'and measured before print release.')
            UI.messageBox(message)
    except Exception:
        if UI:
            UI.messageBox('HALO Dock generation failed:\n{}'.format(traceback.format_exc()))
        raise
