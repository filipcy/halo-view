"""HALO Dock Rev A, Iteration 2 parametric generator for Autodesk Fusion 360.

Iteration 2 adds the first fit, support, retention-concept, and wall-mount geometry.
Run this script from Fusion 360's Scripts and Add-Ins dialog.
"""

import adsk.core
import adsk.fusion
import adsk.cam
import os
import traceback

APP = adsk.core.Application.get()
UI = APP.userInterface if APP else None
PARAMETERS = (
    # Captured device envelope.
    ('device_width', '125 mm', 'Device', 'Bare tablet width; validate by caliper'),
    ('device_height', '211 mm', 'Device', 'Bare tablet height; validate by caliper'),
    ('device_thickness', '8 mm', 'Device', 'Maximum bare tablet thickness; validate by caliper'),
    ('device_corner_radius', '18 mm', 'Device', 'Approximate traced corner radius'),
    # Accepted Rev A interface values.
    ('bezel_width', '6 mm', 'Faceplate', 'Visible bezel around tablet'),
    ('inner_lip_overlap', '0.5 mm', 'Faceplate', 'Target overlap; verify against active display'),
    ('screen_recess', '0.8 mm', 'Faceplate', 'Display recess from Faceplate plane'),
    ('pocket_clearance_x', '0.3 mm', 'Fit', 'Clearance per tablet side'),
    ('pocket_clearance_y', '0.3 mm', 'Fit', 'Clearance per tablet end'),
    ('pocket_clearance_z', '0.3 mm', 'Fit', 'Clearance behind tablet'),
    # Open engineering parameters selected for the Iteration 2 model.
    ('front_thickness', '2.4 mm', 'Faceplate', 'Prototype Faceplate structural thickness'),
    ('wall_shadow_gap', '1.5 mm', 'Dock', 'Gap between tile and DockBody'),
    ('total_projection_target', '18 mm', 'Dock', 'Packaging target from tile to front face'),
    ('dock_back_thickness', 'total_projection_target - wall_shadow_gap - device_thickness - screen_recess', 'Dock', 'Derived rear depth that closes the installed projection stack'),
    ('dock_side_wall', '3 mm', 'Dock', 'Prototype perimeter wall width'),
    ('lower_support_thickness', '3 mm', 'Dock', 'Reserved lower tablet support thickness'),
    ('retention_clearance', '0.3 mm', 'Fit', 'Reserved retention feature clearance'),
    ('guide_depth', 'device_thickness', 'Dock', 'Side-guide and shelf depth from tablet rear datum'),
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
    # Iteration 2 mounting interface; adhesive thickness remains a prototype assumption.
    ('dual_lock_pad_width', '25 mm', 'Wall interface', 'Flat hidden mounting field width'),
    ('dual_lock_pad_height', '50 mm', 'Wall interface', 'Flat hidden mounting field height'),
    ('dual_lock_pad_edge_offset', '12 mm', 'Wall interface', 'Field offset from DockBody side edge'),
    ('dual_lock_center_x', 'device_width / 2 + pocket_clearance_x + dock_side_wall - dual_lock_pad_edge_offset - dual_lock_pad_width / 2', 'Wall interface', 'Hidden mounting field centre magnitude'),
    ('dual_lock_center_x_left', '-dual_lock_center_x', 'Wall interface', 'Left hidden mounting field centre'),
    ('dual_lock_center_y', '0 mm', 'Wall interface', 'Hidden mounting field vertical centre'),
    ('usb_port_datum_x', '59 mm', 'Reserved', 'Confirmed horizontal datum from the left device edge'),
    ('usb_port_datum_y', '1 mm', 'Reserved', 'Approximate lower-edge offset; requires confirmation'),
    ('usb_opening_width', '8 mm', 'Reserved', 'Approximate port opening width'),
    ('usb_opening_height', '2 mm', 'Reserved', 'Approximate port opening height'),
    ('usb_connector_width', '12 mm', 'Reserved', 'Placeholder cable envelope; not modeled'),
    ('usb_connector_height', '7 mm', 'Reserved', 'Placeholder cable envelope; not modeled'),
    ('usb_connector_depth', '20 mm', 'Reserved', 'Placeholder cable envelope; not modeled'),
    ('camera_keepout_width', '18 mm', 'Keep-outs', 'Placeholder; requires measurement'),
    ('camera_keepout_height', '18 mm', 'Keep-outs', 'Placeholder; requires measurement'),
    ('camera_keepout_depth', '2 mm', 'Keep-outs', 'Placeholder; requires measurement'),
    ('speaker_keepout_length', '35 mm', 'Keep-outs', 'Placeholder; not modeled'),
    ('microphone_keepout_diameter', '3 mm', 'Keep-outs', 'Placeholder; not modeled'),
    ('button_keepout_length', '45 mm', 'Keep-outs', 'Placeholder; not modeled'),
)


def _parameter(design, name):
    return design.userParameters.itemByName(name)


def _set_parameters(design):
    for name, expression, group, comment in PARAMETERS:
        existing = _parameter(design, name)
        if existing:
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


def _new_component(root, name):
    occurrence = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occurrence.component.name = name
    return occurrence.component


def _set_dimension_expression(dimension, expression):
    dimension.parameter.expression = expression


def _rounded_rectangle(
    sketch,
    width,
    height,
    radius,
    width_expression,
    height_expression,
    radius_expression,
):
    """Draw a rounded rectangle dimensioned from Fusion user parameters."""
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

    # Anchor the upper-right corner centre to the sketch origin. Together with
    # the inferred coincidence/tangency constraints, this keeps both nested
    # rounded rectangles concentric when their user parameters change.
    corner_center = arc_entities[0].centerSketchPoint
    x_dimension = dimensions.addDistanceDimension(
        sketch.originPoint,
        corner_center,
        horizontal,
        adsk.core.Point3D.create(half_w / 2, 0, 0),
    )
    _set_dimension_expression(
        x_dimension, f'({width_expression}) / 2 - ({radius_expression})'
    )
    y_dimension = dimensions.addDistanceDimension(
        sketch.originPoint,
        corner_center,
        vertical,
        adsk.core.Point3D.create(0, half_h / 2, 0),
    )
    _set_dimension_expression(
        y_dimension, f'({height_expression}) / 2 - ({radius_expression})'
    )
    return sketch.profiles.item(0)


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

    if front_thickness <= screen_recess:
        raise RuntimeError('front_thickness must be greater than screen_recess to leave a rear perimeter skirt.')
    if clearance_x < 0 or clearance_y < 0:
        raise RuntimeError('Pocket clearances must be non-negative so the Faceplate skirt stays outside TabletEnvelope.')

    skirt_rear_z = device_thickness + screen_recess - front_thickness
    skirt_front_z = skirt_rear_z + (front_thickness - screen_recess)
    lip_rear_z = device_thickness
    lip_front_z = lip_rear_z + screen_recess

    tolerance = 1e-6
    if skirt_front_z - device_thickness > tolerance:
        raise RuntimeError('Faceplate perimeter skirt would extend forward into the TabletEnvelope depth.')
    if abs(lip_rear_z - device_thickness) > tolerance:
        raise RuntimeError('Faceplate lip rear plane must start at the tablet display plane.')
    if abs(lip_front_z - (device_thickness + screen_recess)) > tolerance:
        raise RuntimeError('Faceplate lip front plane must preserve screen_recess ahead of the display.')

    installed_projection = (
        _mm(design, 'wall_shadow_gap')
        + _mm(design, 'dock_back_thickness')
        + device_thickness
        + screen_recess
    )
    if abs(installed_projection - _mm(design, 'total_projection_target')) > tolerance:
        raise RuntimeError('Installed layer stack does not meet total_projection_target.')
    if _mm(design, 'wall_shadow_gap') <= 0:
        raise RuntimeError('wall_shadow_gap must create a positive physical separation.')
    if _mm(design, 'guide_depth') > device_thickness + tolerance:
        raise RuntimeError('Guide depth must not project in front of the tablet display plane.')
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


def _offset_plane(component, expression, name):
    plane_input = component.constructionPlanes.createInput()
    plane_input.setByOffset(
        component.xYConstructionPlane,
        adsk.core.ValueInput.createByString(expression),
    )
    plane = component.constructionPlanes.add(plane_input)
    plane.name = name
    return plane


def _build_tablet_envelope(design, root):
    component = _new_component(root, 'TabletEnvelope')
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = 'Tablet outline (reference envelope)'
    profile = _rounded_rectangle(
        sketch,
        _mm(design, 'device_width'),
        _mm(design, 'device_height'),
        _mm(design, 'device_corner_radius'),
        'device_width',
        'device_height',
        'device_corner_radius',
    )
    body = _extrude(component, profile, 'device_thickness').bodies.item(0)
    body.name = 'SM-X130 reference envelope - not for manufacture'
    return component


def _ring_profile(sketch):
    for index in range(sketch.profiles.count):
        profile = sketch.profiles.item(index)
        if profile.profileLoops.count == 2:
            return profile
    raise RuntimeError('Expected a closed Faceplate ring profile.')


def _build_faceplate(design, root):
    # Split the Faceplate so the visible lip sits in front of the tablet while
    # the remaining structural depth is only a perimeter skirt outside the
    # TabletEnvelope. This preserves the 0.8 mm recess without body collision.
    component = _new_component(root, 'Faceplate')
    lip_rear_plane = _offset_plane(
        component,
        'device_thickness',
        'Faceplate lip rear plane (tablet display datum)',
    )
    skirt_rear_plane = _offset_plane(
        component,
        'device_thickness + screen_recess - front_thickness',
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
    profile = _rounded_rectangle(
        sketch,
        _mm(design, 'device_width') + (2 * clearance_x) + (2 * wall),
        _mm(design, 'device_height') + (2 * clearance_y) + (2 * wall),
        _mm(design, 'device_corner_radius') + clearance_x + wall,
        'device_width + 2 * pocket_clearance_x + 2 * dock_side_wall',
        'device_height + 2 * pocket_clearance_y + 2 * dock_side_wall',
        'device_corner_radius + pocket_clearance_x + dock_side_wall',
    )
    feature = _extrude(component, profile, '-dock_back_thickness')
    feature.name = 'Iteration 2 projection-controlled backing'
    feature.bodies.item(0).name = 'HALO DockBody Rev A - backing'

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
    component.description = 'Hidden flat 3M Dual Lock mounting fields; adhesive specification is not final.'
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
            'wall_shadow_gap',
        )
        field.name = side + ' 3M Dual Lock field - prototype'
        field.bodies.item(0).name = side + ' hidden flat mounting field'
    return component


def _build_assembly_placeholder(root):
    assembly = _new_component(root, 'Assembly')
    assembly.description = 'Placeholder: assembly joints, final latch, and service motion are deferred.'


def _export_outputs(design, faceplate, dock_body):
    output_dir = os.path.join(
        os.path.expanduser('~'), 'Documents', 'HALO_Dock_Rev_A_Iteration_2'
    )
    os.makedirs(output_dir, exist_ok=True)
    basename = 'HALO_Dock_Rev_A_Iteration_2'
    export_manager = design.exportManager

    archive_options = export_manager.createFusionArchiveExportOptions(
        os.path.join(output_dir, basename + '.f3d')
    )
    export_manager.execute(archive_options)

    step_options = export_manager.createSTEPExportOptions(
        os.path.join(output_dir, basename + '.step'), design.rootComponent
    )
    export_manager.execute(step_options)

    for component, suffix in ((faceplate, 'Faceplate'), (dock_body, 'DockBody')):
        stl_options = export_manager.createSTLExportOptions(
            component, os.path.join(output_dir, basename + '_' + suffix + '.stl')
        )
        stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        export_manager.execute(stl_options)

    viewport = APP.activeViewport
    viewport.fit()
    viewport.refresh()
    viewport.saveAsImageFile(os.path.join(output_dir, basename + '.png'), 1920, 1080)
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
        _build_wall_interface(design, root)
        _build_assembly_placeholder(root)
        output_dir = _export_outputs(design, faceplate, dock_body)
        if UI:
            UI.messageBox('HALO Dock Rev A Iteration 2 generated and exported to:\n' + output_dir)
    except Exception:
        if UI:
            UI.messageBox('HALO Dock generation failed:\n{}'.format(traceback.format_exc()))
        raise
