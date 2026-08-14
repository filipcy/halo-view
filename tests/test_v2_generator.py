"""Dependency-free guards for the V2 design-review generator."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cad/source/HALO_Wall_Mount_V2.py"
SPEC = importlib.util.spec_from_file_location("halo_v2", SOURCE)
V2 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V2)


class V2GeneratorGuards(unittest.TestCase):
    def test_validated_fit_is_unchanged(self):
        self.assertEqual((V2.DEVICE_W, V2.DEVICE_H, V2.DEVICE_T, V2.DEVICE_R),
                         (125.0, 211.0, 8.0, 8.5))
        self.assertEqual((V2.CLEARANCE_X, V2.CLEARANCE_Y), (0.20, 0.20))
        self.assertEqual(V2.VALIDATED_POCKET_DEPTH, 8.6)
        self.assertEqual(V2.GUIDE_DEPTH, 8.6)
        self.assertEqual(V2.PRINTABLE_FORWARD_DEPTH, 8.0)
        self.assertEqual(V2.TABLET_REAR_Z, 3.0)
        self.assertEqual(V2.REAR_CLEARANCE_Z, 0.30)
        self.assertEqual(V2.REAR_SUPPORT_MAX_Z, 2.7)
        self.assertAlmostEqual(
            V2.TABLET_REAR_Z - V2.REAR_SUPPORT_MAX_Z, 0.30, places=9)

    def test_projection_and_retention_targets(self):
        self.assertEqual(V2.WALL_CONTACT_Z, 0.0)
        self.assertEqual(V2.TABLET_REAR_Z, 3.0)
        self.assertEqual(V2.TABLET_FRONT_Z, 11.0)
        self.assertEqual(V2.TABLET_FRONT_Z - V2.WALL_CONTACT_Z, 11.0)
        self.assertEqual(V2.RETAINER_MAX_Z, V2.TABLET_FRONT_Z)
        self.assertEqual(V2.RETAINER_MIN_Z, V2.TABLET_FRONT_Z - V2.LIP_T)
        self.assertGreaterEqual(V2.LIP_OVERLAP, 1.0)
        self.assertLessEqual(V2.LIP_OVERLAP, 1.5)

    def test_retainer_solids_stay_within_useful_tablet_thickness(self):
        retainers = [part for part in V2.solids()
                     if part[0].startswith("lip-")]
        self.assertEqual(len(retainers), 3)
        for _, minimum, maximum in retainers:
            self.assertLessEqual(maximum[2], V2.TABLET_FRONT_Z)
            self.assertGreater(minimum[2], V2.TABLET_REAR_Z)
            self.assertLess(minimum[2], V2.TABLET_FRONT_Z)
            self.assertEqual(minimum[2], V2.RETAINER_MIN_Z)
            self.assertEqual(maximum[2], V2.RETAINER_MAX_Z)

    def test_retainer_xy_overlap_remains_exactly_1_25_mm(self):
        parts = {part[0]: part for part in V2.solids()}
        left = parts["lip-left"]
        right_low = parts["lip-right-low"]
        self.assertEqual(left[2][0], V2.LIP_OVERLAP)
        self.assertEqual(V2.DEVICE_W - right_low[1][0], V2.LIP_OVERLAP)
        self.assertEqual(V2.LIP_OVERLAP, 1.25)

    def test_every_printable_solid_stays_at_or_behind_tablet_front(self):
        parts = V2.solids()
        self.assertTrue(any(len(part) == 3 for part in parts), "boxes covered")
        self.assertTrue(any(len(part) == 4 for part in parts), "prisms covered")
        maximum_z = max(V2.solid_max_z(part) for part in parts)
        for part in parts:
            self.assertLessEqual(
                V2.solid_max_z(part), V2.TABLET_FRONT_Z, part[0])
        self.assertEqual(maximum_z, 11.0)

    def test_actual_rear_support_geometry_preserves_clearance(self):
        rear_supports = [part for part in V2.solids()
                         if part[0].startswith(("back-", "camera-relief-"))]
        self.assertTrue(rear_supports)
        for part in rear_supports:
            self.assertLessEqual(
                V2.solid_max_z(part), V2.REAR_SUPPORT_MAX_Z, part[0])
        self.assertEqual(max(V2.solid_max_z(part) for part in rear_supports), 2.7)

    def test_camera_is_rear_view_left_not_mirrored_rev_a_side(self):
        self.assertEqual(V2.CAMERA_CENTER_X,
                         V2.DEVICE_W - V2.CAMERA_FROM_REAR_LEFT)
        self.assertGreater(V2.CAMERA_CENTER_X, V2.DEVICE_W / 2)
        names = {part[0] for part in V2.solids()}
        self.assertIn("camera-relief-floor", names)
        self.assertIn("camera-relief-outer-rail", names)

    def test_exterior_chamfer_does_not_change_fit_or_projection(self):
        self.assertEqual(V2.EDGE_CHAMFER, 2.0)
        names = {part[0] for part in V2.solids()}
        self.assertIn("back-top-chamfered", names)
        self.assertIn("shelf-left-chamfered", names)
        self.assertEqual((V2.CLEARANCE_X, V2.CLEARANCE_Y), (0.20, 0.20))
        self.assertEqual(V2.TABLET_FRONT_Z, 11.0)

    def test_usb_envelope_remains_explicitly_provisional(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(V2.USB_POCKET, (22.0, 30.0))
        self.assertIn("PROVISIONAL", source)
        self.assertIn("never production-approved", source)

    def test_button_cutout_moves_exactly_22_mm_down(self):
        self.assertEqual(V2.BUTTON_V2,
                         tuple(value - 22.0 for value in V2.BUTTON_OLD))
        self.assertEqual(V2.BUTTON_V2[1] - V2.BUTTON_V2[0],
                         V2.BUTTON_OLD[1] - V2.BUTTON_OLD[0])

    def test_outputs_include_stl_and_all_eight_views(self):
        old_out = V2.OUT
        try:
            with tempfile.TemporaryDirectory() as directory:
                V2.OUT = Path(directory)
                V2.main()
                self.assertTrue((V2.OUT / "HALO_Wall_Mount_V2_review.stl").is_file())
                self.assertEqual(len(list(V2.OUT.glob("*.svg"))), 8)
        finally:
            V2.OUT = old_out


if __name__ == "__main__":
    unittest.main()
