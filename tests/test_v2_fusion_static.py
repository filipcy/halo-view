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
        self.assertIn("def _add_usb_bridge", source)
        self.assertIn('"Back Bottom Left"', source)
        self.assertIn('"Back Bottom Right"', source)
        self.assertNotIn('"PROVISIONAL USB Routing Deck"', source)
        self.assertNotIn('"PROVISIONAL Wall Exit Cutter"', source)
        self.assertIn("USB_POCKET[1]", source)
        self.assertIn("USB_CHANNEL_W / 2", source)
        self.assertIn("WALL_EXIT_Y < DEVICE_H", source)

    def test_usb_route_has_one_transverse_bridge_and_no_dedicated_exit(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertEqual(source.count('"PROVISIONAL USB Cable Retaining Bridge Roof"'), 1)
        self.assertIn("USB_BRIDGE_W = 4.5", source)
        self.assertIn("USB_CABLE_CLEARANCE_Z", source)
        self.assertIn("USB_BRIDGE_CENTER_Y = 15.0", source)
        self.assertIn("USB_BRIDGE_OVERLAP = 0.5", source)
        self.assertIn("PROVISIONAL Single Transverse USB Cable Bridge", source)
        self.assertIn("adsk.fusion.FeatureOperations.JoinFeatureOperation", source)
        self.assertIn("combineFeatures.createInput(holder, tools)", source)
        self.assertIn("join_input.isKeepToolBodies = False", source)
        self.assertNotIn("Wall Exit Cutter", source)

    def test_usb_features_do_not_leave_helper_brep_bodies(self):
        source = FUSION.read_text(encoding="utf-8")
        route = source[source.index("def _add_usb_bridge"):source.index("def _chamfer_long_front_edges")]
        self.assertIn("JoinFeatureOperation", route)
        self.assertEqual(route.count("combineFeatures.createInput"), 1)
        self.assertIn("join_input.isKeepToolBodies = False", route)
        self.assertNotIn("PROVISIONAL USB Routing Deck", source)
        self.assertIn("holder_component.bRepBodies.count != 1", source)

    def test_central_opening_rejects_residual_geometry(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("def _validate_central_cable_opening", source)
        self.assertIn("holder.pointContainment", source)
        self.assertIn("Residual geometry crosses central cable opening", source)
        self.assertIn("USB bridge blocks the required cable clearance underneath", source)
        self.assertIn("Expected transverse USB bridge roof is absent", source)
        self.assertNotIn("def _cut_usb_route", source)

    def test_one_body_failure_reports_each_remaining_body(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("def _body_diagnostics", source)
        self.assertIn("body.volume", source)
        self.assertIn("body.getPhysicalProperties().volume", source)
        self.assertNotIn("MeasureManager.get", source)
        self.assertIn("body.isSolid", source)
        self.assertIn("bounds.minPoint.x", source)
        self.assertIn("bounds.maxPoint.z", source)
        self.assertIn("size XYZ mm", source)
        message_box = source.index("ui.messageBox(", source.index("def _validate_and_report"))
        body_error = source.index("raise RuntimeError(", message_box)
        self.assertLess(message_box, body_error)

    def test_generator_exports_required_inspection_views(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn('"HALO_Wall_Mount_V2_USB_bridge_closeup.png"', source)
        self.assertIn('"HALO_Wall_Mount_V2_front_edge_oblique.png"', source)
        self.assertIn("saveAsImageFile", source)

    def test_chamfer_targets_only_long_outer_front_edges(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("FRONT_EDGE_CHAMFER = 0.9", source)
        self.assertIn("def _chamfer_long_front_edges", source)
        self.assertIn("is_front and is_outer and is_long_y", source)
        self.assertIn("addEqualDistanceChamferEdgeSet", source)

    def test_tablet_envelope_uses_physical_corner_radius(self):
        source = FUSION.read_text(encoding="utf-8")
        self.assertIn("def _rounded_box", source)
        self.assertIn("DEVICE_H, DEVICE_R, TABLET_REAR_Z", source)


if __name__ == "__main__":
    unittest.main()
