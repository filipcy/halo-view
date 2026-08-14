"""Static parity checks; Autodesk Fusion itself is not available in CI."""
import ast
import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "cad/source/HALO_Wall_Mount_V2.py"
FUSION = ROOT / "cad/source/HALO_Wall_Mount_V2_Fusion.py"


def literal_constants(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values = {}
    def record(target, value):
        if isinstance(target, ast.Name):
            values[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            for child, item in zip(target.elts, value):
                record(child, item)

    for node in tree.body:
        if isinstance(node, ast.Assign):
            try:
                value = ast.literal_eval(node.value)
                for target in node.targets:
                    record(target, value)
            except (ValueError, TypeError):
                pass
    return values


class FusionGeneratorStaticTests(unittest.TestCase):
    def test_validated_literal_parameters_match_review_generator(self):
        fusion = literal_constants(FUSION)
        spec = importlib.util.spec_from_file_location("halo_v2_review_for_parity", REVIEW)
        review = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(review)
        names = ("DEVICE_W", "DEVICE_H", "DEVICE_T", "DEVICE_R", "WALL_CONTACT_Z",
                 "TABLET_REAR_Z", "REAR_CLEARANCE_Z", "REAR_SUPPORT_MAX_Z",
                 "TABLET_FRONT_Z", "SIDE_W", "SHELF_H", "LIP_OVERLAP", "LIP_T",
                 "RETAINER_MIN_Z", "RETAINER_MAX_Z", "EDGE_CHAMFER", "BUTTON_SHIFT")
        for name in names:
            self.assertEqual(fusion[name], getattr(review, name), name)

    def test_fusion_api_and_delivery_contract_are_present(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("import adsk.core", source)
        self.assertIn("import adsk.fusion", source)
        self.assertIn('COMPONENT_NAME = "HALO_Wall_Mount_V2"', source)
        self.assertIn('ENVELOPE_NAME = "TabletEnvelope"', source)
        self.assertIn('"HALO_Wall_Mount_V2.step"', source)
        self.assertIn('"HALO_Wall_Mount_V2.stl"', source)
        self.assertIn("combineFeatures", source)

    def test_provisional_usb_parameters_drive_real_cut_geometry(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("def _cut_usb_route", source)
        self.assertIn('"PROVISIONAL USB-C Plug Pocket Cutter"', source)
        self.assertIn('"PROVISIONAL Hidden Cable Channel Cutter"', source)
        self.assertNotIn('"PROVISIONAL Wall Exit Cutter"', source)
        self.assertIn("USB_POCKET[1]", source)
        self.assertIn("USB_CHANNEL_W / 2", source)
        self.assertIn("WALL_EXIT_Y + channel_half <= DEVICE_H", source)
        self.assertIn("CutFeatureOperation", source)

    def test_usb_route_has_one_transverse_bridge_and_no_dedicated_exit(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertEqual(source.count('"PROVISIONAL USB Cable Retaining Bridge"'), 1)
        self.assertIn("USB_BRIDGE_W = 4.5", source)
        self.assertIn("USB_CABLE_CLEARANCE_Z", source)
        self.assertIn("bridge_center_y = (USB_POCKET[1] + channel_end_y) / 2", source)
        self.assertIn("PROVISIONAL Single Transverse USB Cable Bridge", source)
        self.assertNotIn("Wall Exit Cutter", source)

    def test_generator_exports_rear_usb_detail_view(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("RearViewOrientation", source)
        self.assertIn('"HALO_Wall_Mount_V2_USB_rear_detail.png"', source)
        self.assertIn("saveAsImageFile", source)

    def test_tablet_envelope_uses_physical_corner_radius(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("def _rounded_box", source)
        self.assertIn("DEVICE_H, DEVICE_R, TABLET_REAR_Z", source)


if __name__ == "__main__":
    unittest.main()
