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
    def test_nested_rounded_rectangles_are_explicitly_concentric(self):
        rounded = ast.unparse(function('_rounded_rectangle'))
        self.assertIn('concentric_with=None', rounded)
        self.assertIn('constraints.addConcentric(outer_arc, inner_arc)', rounded)
        self.assertIn('zip(concentric_with.arcs, arc_entities)', rounded)

    def test_only_outer_or_standalone_rectangle_has_origin_anchors(self):
        rounded_node = function('_rounded_rectangle')
        anchor_if = next(
            node for node in ast.walk(rounded_node)
            if isinstance(node, ast.If)
            and ast.unparse(node.test) == 'concentric_with is None'
            and 'sketch.originPoint' in ast.unparse(node)
        )
        self.assertEqual(ast.unparse(anchor_if).count('sketch.originPoint'), 2)
        self.assertNotIn('sketch.originPoint', '\n'.join(
            ast.unparse(node) for node in anchor_if.orelse
        ))

    def test_both_faceplate_inner_loops_use_outer_geometry(self):
        faceplate = ast.unparse(function('_build_faceplate'))
        self.assertIn('lip_outer = _rounded_rectangle', faceplate)
        self.assertIn('concentric_with=lip_outer', faceplate)
        self.assertIn('skirt_outer = _rounded_rectangle', faceplate)
        self.assertIn('concentric_with=skirt_outer', faceplate)
        self.assertEqual(faceplate.count('concentric_with='), 2)

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
        self.assertNotIn('lines.addByTwoPoints(outer_arc.endSketchPoint', profile)

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
            'HALO_Dock_Rev_A_Faceplate_Open_Corner_L',
            'HALO_Dock_Rev_A_Side_Guide_Lower_Shelf',
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
