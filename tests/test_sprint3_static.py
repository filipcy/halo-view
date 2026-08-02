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
        self.assertNotIn('createSTEPExportOptions', coupon_branch)
        self.assertNotIn('createFusionArchiveExportOptions', coupon_branch)

    def test_guide_coupon_is_device_width_derived_and_symmetric(self):
        self.assertIn("('coupon_guide_inner_width', 'device_width + 2 * coupon_guide_clearance'", SOURCE)
        self.assertIn("('coupon_shelf_width', 'coupon_guide_inner_width'", SOURCE)
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

    def test_dual_lock_is_measurement_gated(self):
        self.assertNotIn('dual_lock_engaged_thickness', SOURCE)
        self.assertIn("('dual_lock_measured_engaged_thickness', '0 mm'", SOURCE)
        self.assertIn("'dual_lock_measured_engaged_thickness - wall_shadow_gap'", SOURCE)
        validation = ast.unparse(function('_dual_lock_measurement'))
        for guard in ('measured <= 0', 'recess < 0', 'recess >= dock_back', 'remaining <= 0'):
            self.assertIn(guard, validation)

    def test_all_required_pairs_use_signed_centres(self):
        for right, left in (
            ('guide_center_x', 'guide_center_x_left'),
            ('retention_center_x', 'retention_center_x_left'),
            ('coupon_guide_center_x', 'coupon_guide_center_x_left'),
            ('dual_lock_center_x', 'dual_lock_center_x_left'),
            ('wall_coupon_center_x', 'wall_coupon_center_x_left'),
        ):
            self.assertIn(f"('{left}', '-{right}'", SOURCE)
        # Fit gauge rails are generated in one signed loop, not independent offsets.
        fit = ast.unparse(function('_build_clearance_coupon'))
        self.assertIn("('Right', 1), ('Left', -1)", fit)

    def test_manifest_matches_every_generated_stl_name(self):
        manifest = (ROOT / 'manufacturing/HALO_Dock_Rev_A_External_Print_Candidate/PART_MANIFEST.md').read_text()
        expected = {
            'HALO_Dock_Rev_A_Clearance_0_2mm.stl',
            'HALO_Dock_Rev_A_Clearance_0_3mm.stl',
            'HALO_Dock_Rev_A_Clearance_0_4mm.stl',
            'HALO_Dock_Rev_A_Faceplate_Open_Corner_L.stl',
            'HALO_Dock_Rev_A_Side_Guide_Lower_Shelf.stl',
            'HALO_Dock_Rev_A_Wall_Stack_Shadow_Gap.stl',
            'HALO_Dock_Rev_A_Faceplate_PRINT_CANDIDATE_ONLY.stl',
            'HALO_Dock_Rev_A_DockBody_PRINT_CANDIDATE_ONLY.stl',
        }
        for name in expected:
            self.assertIn(name, SOURCE)
            self.assertIn(name, manifest)


if __name__ == '__main__':
    unittest.main()
