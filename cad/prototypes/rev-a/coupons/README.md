# Rev A coupon artifacts

This directory is a controlled landing area, **not a release**. The source of the geometry is `cad/source/HALO_Dock_Rev_A.py`. Do not add hand-made or renamed CAD/mesh/image files.

Artifact states are sequential:

1. **source generator** — committed Python only;
2. **generated, unverified** — produced by a native Fusion run but not accepted;
3. **native-verified** — rebuild, symmetry, section, and interference checks recorded;
4. **slicer-verified** — opened at 100%, dimensions/orientation/walls/supports/manifold/build volume checked;
5. **released coupon** — written approval links the evidence and exact file checksum.

Only verified native exports may be placed here. No artifact is currently committed or released.
