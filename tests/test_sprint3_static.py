"""Static release guards that run without Autodesk Fusion 360."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / 'cad/source/HALO_Dock_Rev_A.py'
SOURCE = SOURCE_PATH.read_text(encoding='utf-8')
TREE = ast.parse(SOURCE)


def assignment(name):
    for node in TREE.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError(f'missing assignment {name}')


def function(name):
    return next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == name)


class Sprint3StaticGuards(unittest.TestCase):
    def test_every_rounded_rectangle_is_independently_origin_centred(self):
        rounded = ast.unparse(function('_rounded_rectangle'))
        self.assertNotIn('concentric_with', rounded)
        self.assertNotIn('addConcentric', rounded)
        self.assertIn('center_diagonal.isConstruction = True', rounded)
        self.assertIn(
            'addMidPoint(sketch.originPoint, center_diagonal)', rounded
        )

    def test_width_height_and_radius_remain_parameter_driven(self):
        rounded = ast.unparse(function('_rounded_rectangle'))
        self.assertIn("f'{width_expression} - 2 * ({radius_expression})'", rounded)
        self.assertIn("f'{height_expression} - 2 * ({radius_expression})'", rounded)
        self.assertIn('_set_dimension_expression(dimension, radius_expression)', rounded)

    def test_both_faceplate_nested_profiles_use_generic_safe_api(self):
        faceplate = ast.unparse(function('_build_faceplate'))
        self.assertEqual(faceplate.count('_rounded_rectangle('), 4)
        self.assertNotIn('concentric_with', faceplate)

    def test_rear_skirt_supports_unequal_clearances_without_recentering(self):
        faceplate = ast.unparse(function('_build_faceplate'))
        self.assertIn("'device_width + 2 * pocket_clearance_x'", faceplate)
        self.assertIn("'device_height + 2 * pocket_clearance_y'", faceplate)
        self.assertIn("'device_corner_radius + pocket_clearance_x'", faceplate)
        self.assertNotIn('addConcentric', faceplate)

    def test_part_design_component_failure_explains_hybrid_design(self):
        new_component = ast.unparse(function('_new_component'))
        self.assertIn('Part Design documents can only contain one component', new_component)
        self.assertIn('requires a Hybrid Design document', new_component)
        self.assertIn('Open or convert to Hybrid Design', new_component)

    def test_ring_profile_requires_exactly_one_closed_two_loop_region(self):
        ring = ast.unparse(function('_ring_profile'))
        self.assertIn('profile.profileLoops.count == 2', ring)
        self.assertIn('len(ring_profiles) != 1', ring)

    def test_export_modes_and_safe_default(self):
        self.assertEqual(assignment('COUPONS_ONLY'), 'COUPONS_ONLY')
        self.assertEqual(assignment('FULL_SIZE_PRINT_CANDIDATE'), 'FULL_SIZE_PRINT_CANDIDATE')
        export = next(n for n in TREE.body if isinstance(n, ast.Assign) and
                      any(isinstance(t, ast.Name) and t.id == 'EXPORT_MODE' for t in n.targets))
        self.assertIsInstance(export.value, ast.Name)
        self.assertEqual(export.value.id, 'COUPONS_ONLY')

    def test_coupon_only_branch_never_names_full_parts(self):
        export = function('_export_outputs')
        mode_if = next(n for n in ast.walk(export) if isinstance(n, ast.If) and
                       'EXPORT_MODE == COUPONS_ONLY' in ast.unparse(n.test))
        coupon_branch = '\n'.join(ast.unparse(n) for n in mode_if.body)
        self.assertNotIn('faceplate', coupon_branch.lower())
        self.assertNotIn('dockbody', coupon_branch.lower())
        self.assertNotIn('dock_body', coupon_branch.lower())
        self.assertNotIn('createFusionArchiveExportOptions', coupon_branch)
        self.assertIn('_export_printable_part', coupon_branch)

    def test_guide_coupon_is_device_width_derived_and_symmetric(self):
        self.assertIn("('coupon_guide_inner_width', 'device_width + 2 * coupon_guide_clearance'", SOURCE)
        self.assertIn("('coupon_shelf_width', 'coupon_guide_inner_width + 2 * dock_side_wall'", SOURCE)
        self.assertIn("('coupon_guide_center_x_left', '-coupon_guide_center_x'", SOURCE)
        self.assertNotIn('coupon_guide_section_width', SOURCE)

    def test_open_corner_cannot_regress_to_ring(self):
        corner = ast.unparse(function('_build_faceplate_corner_coupon'))
        profile = ast.unparse(function('_open_corner_l_profile'))
        self.assertNotIn('_ring_profile', corner)
        self.assertNotIn('_rounded_rectangle', corner)
        self.assertNotIn('profileLoops.count == 2', profile)
        self.assertIn('coupon_corner_arm_length', profile)
        self.assertIn('addByCenterStartSweep', profile)
        self.assertEqual(profile.count('addByCenterStartSweep'), 2)
        self.assertNotIn('top_arm_datum', profile)
        self.assertNotIn('side_arm_datum', profile)
        self.assertNotIn('isConstruction', profile)
        self.assertIn(
            'sketch.originPoint, outer_top.startSketchPoint', profile)
        self.assertIn(
            'sketch.originPoint, outer_side.endSketchPoint', profile)
        self.assertEqual(profile.count("'coupon_corner_arm_length'"), 3)
        self.assertNotIn('-3.141592653589793 / 2', profile)
        self.assertIn(
            "Point3D.create(-arm, 0, 0), outer_arc.endSketchPoint", profile)
        self.assertIn(
            'outer_arc.startSketchPoint, adsk.core.Point3D.create(0, -arm, 0)',
            profile)
        self.assertIn(
            'side_end.endSketchPoint, inner_arc.startSketchPoint', profile)
        self.assertIn(
            'inner_arc.endSketchPoint, adsk.core.Point3D.create(-arm, -band, 0)',
            profile)
        self.assertNotIn('constraints.addCoincident', profile)
        self.assertNotIn('addVertical(outer_side)', profile)
        self.assertNotIn('addVertical(inner_side)', profile)
        self.assertNotIn('coupon_corner_outer_width', profile)
        self.assertNotIn('coupon_corner_outer_height', profile)

    def test_open_corner_skirt_joins_and_native_export_is_guarded(self):
        corner = ast.unparse(function('_build_faceplate_corner_coupon'))
        guard = ast.unparse(function('_validate_open_corner_coupon'))
        export = ast.unparse(function('_export_outputs'))
        self.assertIn('JoinFeatureOperation', corner)
        self.assertIn('component.bRepBodies.count != 1', guard)
        self.assertIn("_mm(design, 'coupon_corner_arm_length')", guard)
        self.assertIn('bounds.maxPoint.x - bounds.minPoint.x', guard)
        self.assertIn('bounds.maxPoint.y - bounds.minPoint.y', guard)
        self.assertIn('_validate_open_corner_coupon(component, design)', export)

    def test_three_explicit_corner_radius_candidates_are_unique_and_gated(self):
        part_ids = assignment('COUPON_PART_IDS')
        corner_ids = [part_ids['corner_R8_0'], part_ids['corner_R8_5'], part_ids['corner_R9_0']]
        self.assertEqual(len(corner_ids), len(set(corner_ids)))
        for token in ('R8_0', 'R8_5', 'R9_0'):
            self.assertIn(token, part_ids['corner_' + token])
            self.assertIn("('coupon_corner_radius_" + token, SOURCE)
        self.assertIn("('device_corner_radius', '8.5 mm'", SOURCE)
        self.assertIn('Selected from physical R8/R8.5/R9 coupon validation', SOURCE)
        self.assertFalse(assignment('FULL_SIZE_RELEASE_GATES')['corner_radius_selected'])
        run = ast.unparse(function('run'))
        self.assertIn("('R8_0', 'coupon_corner_radius_R8_0')", run)
        self.assertIn("('R8_5', 'coupon_corner_radius_R8_5')", run)
        self.assertIn("('R9_0', 'coupon_corner_radius_R9_0')", run)
        self.assertNotIn('device_corner_radius).expression', run)

    def test_physical_fit_selections_and_coupon_sets_are_preserved(self):
        self.assertIn("('pocket_clearance_x', '0.20 mm'", SOURCE)
        self.assertIn("('pocket_clearance_y', '0.20 mm'", SOURCE)
        self.assertIn("('device_corner_radius', '8.5 mm'", SOURCE)
        run = ast.unparse(function('run'))
        for clearance in ('0.2', '0.3', '0.4'):
            self.assertIn(clearance, run)
        for radius in ('R8_0', 'R8_5', 'R9_0'):
            self.assertIn(radius, run)

    def test_shelf_strength_and_usb_relief_are_guarded(self):
        self.assertIn("('lower_support_thickness', '3 mm'", SOURCE)
        self.assertIn("('shelf_hidden_structural_thickness', '3 mm'", SOURCE)
        self.assertIn("('shelf_root_fillet_radius', '3 mm'", SOURCE)
        self.assertIn("('usb_downward_relief', '0.30 mm'", SOURCE)
        self.assertIn("('usb_rear_relief', '0.20 mm'", SOURCE)
        reinforcement = ast.unparse(function('_add_shelf_root_reinforcement'))
        self.assertIn('shelf_root_fillet_radius', reinforcement)
        self.assertIn("'guide_depth'", reinforcement)
        self.assertIn('JoinFeatureOperation', reinforcement)
        dock = ast.unparse(function('_build_dock_body'))
        self.assertIn("'cable_pocket_cut_depth'", dock)
        self.assertIn('_add_shelf_root_reinforcement', dock)
        self.assertIn("('cable_pocket_width', '18 mm'", SOURCE)
        self.assertIn("-device_width / 2 + cable_pocket_edge_x", SOURCE)

    def test_pocket_depth_drives_full_stack_and_coupon_parity_guard(self):
        self.assertIn("('pocket_depth', 'device_thickness + 2 * pocket_clearance_z'", SOURCE)
        self.assertIn("('guide_depth', 'pocket_depth'", SOURCE)
        self.assertIn('total_projection_target - wall_shadow_gap - pocket_depth - screen_recess', SOURCE)
        validate = ast.unparse(function('_validate_iteration_2_geometry'))
        self.assertIn('clearance_z <= 0', validate)
        self.assertIn('pocket_depth - expected_pocket_depth', validate)
        self.assertIn('pocket_depth - selected_slot_width', validate)
        faceplate = ast.unparse(function('_build_faceplate'))
        corner = ast.unparse(function('_build_faceplate_corner_coupon'))
        for geometry in (faceplate, corner):
            self.assertIn("'pocket_depth'", geometry)
            self.assertIn('pocket_depth + screen_recess - front_thickness', geometry)

    def test_dashboard_keepouts_are_edge_based_and_physically_guarded(self):
        for expression in (
            "-device_width / 2 + cable_pocket_edge_x",
            "-device_width / 2 + camera_keepout_edge_x",
            "-device_height / 2 + camera_keepout_edge_y",
            "-device_width / 2 + speaker_slot_edge_x",
        ):
            self.assertIn(expression, SOURCE)
        dock = ast.unparse(function('_build_dock_body'))
        for feature in ('camera_keepout_depth', 'button_relief_depth',
                        'cable_pocket_center_y', '_cut_speaker_slot'):
            self.assertIn(feature, dock)
        validate = ast.unparse(function('_validate_iteration_2_geometry'))
        for message in ('Camera Keep-out', 'Button Relief', 'Cable Pocket', 'Speaker slot'):
            self.assertIn(message, validate)
        for prohibited in ('jack_opening', 'microsd', 'microphone_opening'):
            self.assertNotIn(prohibited, SOURCE.lower())

    def test_cable_cuts_use_proven_rectangular_profile(self):
        cutter = ast.unparse(function('_cut_cable_profile'))
        self.assertIn('_centered_rectangle_profile', cutter)
        self.assertNotIn('_centered_rounded_rectangle_profile', SOURCE)
        self.assertNotIn('cable_pocket_corner_radius', SOURCE)
        for builder in ('_build_faceplate', '_build_dock_body',
                        '_build_guide_shelf_coupon',
                        '_build_faceplate_cable_coupon'):
            self.assertIn('_cut_cable_profile', ast.unparse(function(builder)))

    def test_no_cable_reference_body_or_temporary_box_remains(self):
        self.assertNotIn('OrientedBoundingBox3D', SOURCE)
        self.assertNotIn('createBox', SOURCE)
        self.assertNotIn('TemporaryBRepManager', SOURCE)
        self.assertNotIn("_new_component(root, 'CableEnvelope')", SOURCE)
        self.assertNotIn('def _build_cable_envelope', SOURCE)

    def test_timeline_health_blocks_errors_and_warnings(self):
        health = ast.unparse(function('_validate_timeline_health'))
        self.assertIn('ErrorFeatureHealthState', health)
        self.assertIn('WarningFeatureHealthState', health)
        self.assertIn('entity.errorOrWarningMessage', health)
        self.assertIn('component.name', health)
        self.assertIn('entity.name', health)
        export = ast.unparse(function('_export_outputs'))
        self.assertIn('design.computeAll()', export)
        self.assertIn('_validate_timeline_health(design)', export)
        self.assertNotIn('_validate_cable_clearance', export)

    def test_cable_reference_cannot_enter_export_lists(self):
        export = ast.unparse(function('_export_outputs'))
        run = ast.unparse(function('run'))
        self.assertNotIn('cable_envelope', export)
        self.assertNotIn('CableEnvelope', run)
        self.assertNotIn('_export_printable_part(export_manager, envelope_body', SOURCE)

    def test_every_coupon_is_solid_validated_before_export(self):
        validator = ast.unparse(function('_validate_printable_coupon'))
        export = ast.unparse(function('_export_outputs'))
        self.assertIn('_validate_printable_coupon(component, part_id)', export)
        for guard in ('body_count != 1', 'not is_valid', 'not is_solid',
                      'volume <= 0', 'faces <= 0', 'edges <= 0',
                      'vertices <= 0', 'extent <= 0'):
            self.assertIn(guard, validator)
        self.assertIn('body.preciseBoundingBox', validator)
        self.assertIn("COUPON_PART_IDS['faceplate_cable']", validator)
        self.assertIn("'faceplate_cable_coupon_width'", validator)
        self.assertIn("COUPON_PART_IDS['guide']", validator)
        self.assertIn("'coupon_shelf_width'", validator)
        self.assertIn("'coupon_fit_outer_width_' + safe", validator)
        self.assertIn("'lower_support_thickness'", validator)
        self.assertIn('existing_bodies.append', validator)
        self.assertIn('existing.name', validator)
        self.assertIn('existing.volume', validator)
        coupon_branch = next(
            n for n in ast.walk(function('_export_outputs'))
            if isinstance(n, ast.If) and
            'EXPORT_MODE == COUPONS_ONLY' in ast.unparse(n.test))
        branch = '\n'.join(ast.unparse(node) for node in coupon_branch.body)
        self.assertNotIn("FULL_SIZE_PART_IDS['faceplate']", branch)
        self.assertNotIn("FULL_SIZE_PART_IDS['dock_body']", branch)

    def test_clearance_validation_uses_x_vertices_and_functional_y_range(self):
        validator = ast.unparse(function('_validate_printable_coupon'))
        self.assertNotIn("expected_y = _mm(design, 'coupon_fit_outer_height')", validator)
        self.assertIn("_mm(design, 'coupon_fit_outer_width_' + safe)", validator)
        self.assertIn("_mm(design, 'coupon_fit_slot_width_' + safe)", validator)
        self.assertIn('body.vertices.item(index).geometry.x', validator)
        self.assertIn('x_clusters', validator)
        self.assertIn('cluster_centers', validator)
        self.assertIn('-outer_width / 2', validator)
        self.assertIn('-slot_width / 2', validator)
        self.assertIn('slot_width / 2', validator)
        self.assertIn('outer_width / 2', validator)
        self.assertIn("minimum_y = _mm(design, 'coupon_fit_rail_length')", validator)
        self.assertIn("maximum_y = minimum_y + _mm(design, 'coupon_fit_base_height')", validator)
        self.assertIn('extents[1] < minimum_y - tolerance', validator)
        self.assertIn('extents[1] > maximum_y + tolerance', validator)
        self.assertIn('(extents[0], expected_x)', validator)
        self.assertIn('(extents[2], expected_z)', validator)

    def test_full_size_cable_review_gate_defaults_false(self):
        gates = assignment('FULL_SIZE_RELEASE_GATES')
        self.assertIn('cable_clearance_native_review', gates)
        self.assertFalse(gates['cable_clearance_native_review'])
        self.assertIn('physical USB-C coupon test', SOURCE)
        self.assertIn('native visual/interference review', SOURCE)
        self.assertIn('written confirmation', SOURCE)

    def test_every_intersecting_printable_and_coupons_receive_cable_cut(self):
        faceplate = ast.unparse(function('_build_faceplate'))
        dock = ast.unparse(function('_build_dock_body'))
        guide = ast.unparse(function('_build_guide_shelf_coupon'))
        cable_coupon = ast.unparse(function('_build_faceplate_cable_coupon'))
        self.assertIn('_cut_cable_profile', faceplate)
        self.assertGreaterEqual(dock.count('_cut_cable_profile'), 2)
        self.assertIn('_cut_cable_profile', guide)
        self.assertIn('_cut_speaker_slot', guide)
        self.assertIn('_cut_cable_profile', cable_coupon)
        self.assertIn('component.bRepBodies.count != 1', cable_coupon)
        self.assertIn(
            'HALO_Dock_Rev_A_Faceplate_USB_C_Cable_Pocket',
            assignment('COUPON_PART_IDS').values())

    def test_speaker_slot_is_shared_xz_through_cut(self):
        speaker = ast.unparse(function('_cut_speaker_slot'))
        self.assertIn('component.xZConstructionPlane', ast.unparse(function('_offset_xz_plane')))
        self.assertIn("'speaker_slot_width', 'speaker_slot_height'", speaker)
        self.assertIn("'speaker_slot_center_x', 'speaker_slot_center_z'", speaker)
        self.assertIn("profile, 'lower_support_thickness'", speaker)
        self.assertNotIn("profile, 'speaker_slot_height'", speaker)
        self.assertIn('height > _mm(design, \'guide_depth\')', speaker)
        self.assertIn('shelf_wall <= 0', speaker)
        self.assertIn('abs(width - 2.0)', speaker)
        self.assertIn('abs(height - 0.5)', speaker)
        self.assertIn('cut.extentOne.distance.value - shelf_wall', speaker)
        self.assertIn('residual shelf material would block', speaker)
        dock = ast.unparse(function('_build_dock_body'))
        guide = ast.unparse(function('_build_guide_shelf_coupon'))
        self.assertEqual(dock.count('_cut_speaker_slot'), 1)
        self.assertEqual(guide.count('_cut_speaker_slot'), 1)
        self.assertIn("'speaker_slot_plane_offset'", dock)
        self.assertIn("'coupon_speaker_slot_plane_offset'", guide)

    def test_dual_lock_is_measurement_gated(self):
        self.assertNotIn('dual_lock_engaged_thickness', SOURCE)
        self.assertIn("('dual_lock_measured_engaged_thickness', '0 mm'", SOURCE)
        self.assertIn("'dual_lock_measured_engaged_thickness - wall_shadow_gap'", SOURCE)
        validation = ast.unparse(function('_dual_lock_measurement'))
        for guard in ('measured <= 0', 'recess < 0', 'recess >= dock_back', 'remaining <= 0'):
            self.assertIn(guard, validation)

    def test_physical_measurement_survives_generator_rerun(self):
        setter = ast.unparse(function('_set_parameters'))
        self.assertIn("name != 'dual_lock_measured_engaged_thickness'", setter)

    def test_coupon_bodies_are_connected_and_zero_recess_is_safe(self):
        guide = ast.unparse(function('_build_guide_shelf_coupon'))
        fit = ast.unparse(function('_build_clearance_coupon'))
        wall = ast.unparse(function('_build_wall_coupon_field'))
        self.assertIn('JoinFeatureOperation', guide)
        self.assertNotIn('JoinFeatureOperation', fit)
        self.assertNotIn('CutFeatureOperation', fit)
        self.assertIn('measurement[0] > 0', wall)

    def test_clearance_coupons_are_single_explicit_u_profiles(self):
        fit = ast.unparse(function('_build_clearance_coupon'))
        self.assertNotIn('JoinFeatureOperation', fit)
        self.assertNotIn('CutFeatureOperation', fit)
        self.assertEqual(fit.count('component.sketches.add('), 1)
        self.assertEqual(fit.count('_extrude('), 1)
        self.assertEqual(fit.count('NewBodyFeatureOperation'), 1)
        self.assertIn("f'device_thickness + 2 * {parameter_name}'", fit)
        self.assertIn("f'{slot_width} + 2 * coupon_fit_rail_width'", fit)
        self.assertIn("_mm(design, 'coupon_fit_outer_height')", fit)
        self.assertIn("_mm(design, 'coupon_fit_base_height')", fit)
        self.assertIn('_mm(design, slot_width)', fit)
        self.assertIn('_mm(design, outer_width)', fit)
        self.assertIn('previous.endSketchPoint', fit)
        self.assertIn('first.startSketchPoint', fit)
        self.assertIn('sketch.profiles.count != 1', fit)
        self.assertNotIn('sketch.geometricConstraints', fit)
        self.assertNotIn('sketch.sketchDimensions', fit)
        self.assertIn("'lower_support_thickness'", fit)
        self.assertIn(
            "('coupon_fit_outer_height', 'coupon_fit_rail_length + coupon_fit_base_height / 2'",
            SOURCE)
        self.assertEqual([8 + 2 * c for c in (0.2, 0.3, 0.4)], [8.4, 8.6, 8.8])
        self.assertEqual([8 + 2 * c + 6 for c in (0.2, 0.3, 0.4)], [14.4, 14.6, 14.8])
        self.assertEqual(30 + 3 / 2, 31.5)
        self.assertIn("('lower_support_thickness', '3 mm'", SOURCE)

    def test_wall_fields_are_separate_controlled_parts(self):
        run = ast.unparse(function('run'))
        wall = ast.unparse(function('_build_wall_coupon_field'))
        self.assertIn("COUPON_PART_IDS['wall_right']", run)
        self.assertIn("COUPON_PART_IDS['wall_left']", run)
        self.assertNotIn("for side, center_x", wall)

    def test_step_stl_parity_and_no_contaminated_root_export(self):
        pair = ast.unparse(function('_export_printable_part'))
        export = ast.unparse(function('_export_outputs'))
        self.assertIn("part_id + '.step'", pair)
        self.assertIn("part_id + '.stl'", pair)
        self.assertNotIn('design.rootComponent', export)
        self.assertNotIn('createFusionArchiveExportOptions', export)
        self.assertIn("FULL_SIZE_PART_IDS['faceplate']", export)
        self.assertIn("FULL_SIZE_PART_IDS['dock_body']", export)

    def test_all_required_pairs_use_signed_centres(self):
        for right, left in (
            ('guide_center_x', 'guide_center_x_left'),
            ('retention_center_x', 'retention_center_x_left'),
            ('coupon_guide_center_x', 'coupon_guide_center_x_left'),
            ('dual_lock_center_x', 'dual_lock_center_x_left'),
            ('wall_coupon_center_x', 'wall_coupon_center_x_left'),
        ):
            self.assertIn(f"('{left}', '-{right}'", SOURCE)

    def test_manifest_matches_every_generated_stl_name(self):
        manifest = (ROOT / 'manufacturing/HALO_Dock_Rev_A_External_Print_Candidate/PART_MANIFEST.md').read_text()
        expected = {
            'HALO_Dock_Rev_A_Clearance_0_2mm',
            'HALO_Dock_Rev_A_Clearance_0_3mm',
            'HALO_Dock_Rev_A_Clearance_0_4mm',
            'HALO_Dock_Rev_A_Faceplate_Open_Corner_L_R8_0',
            'HALO_Dock_Rev_A_Faceplate_Open_Corner_L_R8_5',
            'HALO_Dock_Rev_A_Faceplate_Open_Corner_L_R9_0',
            'HALO_Dock_Rev_A_Side_Guide_Lower_Shelf',
            'HALO_Dock_Rev_A_Faceplate_USB_C_Cable_Pocket',
            'HALO_Dock_Rev_A_Wall_Stack_Shadow_Gap_Right',
            'HALO_Dock_Rev_A_Wall_Stack_Shadow_Gap_Left',
            'HALO_Dock_Rev_A_Faceplate_PRINT_CANDIDATE_ONLY',
            'HALO_Dock_Rev_A_DockBody_PRINT_CANDIDATE_ONLY',
        }
        for name in expected:
            self.assertIn(name, SOURCE)
            self.assertIn(name + '.step', manifest)
            self.assertIn(name + '.stl', manifest)


if __name__ == '__main__':
    unittest.main()
