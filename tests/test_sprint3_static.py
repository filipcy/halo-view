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
        self.assertIn('PROVISIONAL AND UNVERIFIED', SOURCE)
        self.assertFalse(assignment('FULL_SIZE_RELEASE_GATES')['corner_radius_selected'])
        run = ast.unparse(function('run'))
        self.assertIn("('R8_0', 'coupon_corner_radius_R8_0')", run)
        self.assertIn("('R8_5', 'coupon_corner_radius_R8_5')", run)
        self.assertIn("('R9_0', 'coupon_corner_radius_R9_0')", run)
        self.assertNotIn('device_corner_radius).expression', run)

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

    def test_cable_radius_is_real_positive_sweep_geometry(self):
        rounded = ast.unparse(function('_centered_rounded_rectangle_profile'))
        self.assertIn("_mm(design, radius_name)", rounded)
        self.assertIn('addByCenterStartSweep', rounded)
        self.assertIn('_set_dimension_expression(radial, radius_name)', rounded)
        self.assertNotIn('-quarter_turn', rounded)
        cutter = ast.unparse(function('_cut_cable_profile'))
        self.assertIn("'cable_pocket_corner_radius'", cutter)
        self.assertIn('_centered_rounded_rectangle_profile', cutter)

    def test_cable_envelope_is_reference_only_and_export_guarded(self):
        envelope = ast.unparse(function('_build_cable_envelope'))
        self.assertIn("_new_component(root, 'CableEnvelope')", envelope)
        self.assertIn('NON-PRINTABLE', envelope)
        self.assertIn('intentional open-air cable clearance', envelope)
        self.assertIn("'cable_pocket_width'", envelope)
        self.assertIn("'cable_pocket_run_depth'", envelope)
        self.assertIn("'cable_pocket_height'", envelope)
        export = ast.unparse(function('_export_outputs'))
        self.assertIn('_validate_cable_envelope_clear', export)
        self.assertNotIn('_export_printable_part(export_manager, cable_envelope', export)

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
        self.assertIn('JoinFeatureOperation', fit)
        self.assertIn('measurement[0] > 0', wall)

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
        # Fit-gauge left centres are expressions derived from right centres,
        # and both rails are generated through the same loop.
        fit = ast.unparse(function('_build_clearance_coupon'))
        self.assertIn("center_left, '-' + center_right", fit)
        self.assertIn("('Right', center_right), ('Left', center_left)", fit)

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
