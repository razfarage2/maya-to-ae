import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "maya_side"))


def test_scene_reader_basic():
    """Test basic scene reading functionality"""
    print("\n=== Test: Basic Scene Reader ===")

    from scene_reader import SceneReader

    reader = SceneReader()

    assert reader is not None, "SceneReader should initialize"
    assert hasattr(
        reader, "extract_scene"
    ), "SceneReader should have extract_scene method"

    print("✓ SceneReader initialized")


def test_scene_info_extraction():
    """Test scene info extraction"""
    print("\n=== Test: Scene Info Extraction ===")

    import maya.cmds as cmds
    from scene_reader import SceneReader

    cmds.file(new=True, force=True)

    cmds.playbackOptions(minTime=1, maxTime=100)
    cmds.currentTime(50)

    reader = SceneReader()
    scene_data = reader.extract_scene(include_aovs=False, include_materials=False)

    assert "scene_info" in scene_data, "Should have scene_info"
    scene_info = scene_data["scene_info"]

    assert scene_info["current_frame"] == 50.0, "Current frame should be 50"
    assert scene_info["frame_range"] == [1.0, 100.0], "Frame range should be [1, 100]"
    assert scene_info["fps"] == 24, "FPS should be 24"
    assert scene_info["up_axis"] == "y", "Up axis should be y"

    print(
        f"✓ Scene info: Frame {scene_info['current_frame']}, Range {scene_info['frame_range']}"
    )


def test_camera_extraction():
    """Test camera extraction"""
    print("\n=== Test: Camera Extraction ===")

    import maya.cmds as cmds
    from scene_reader import SceneReader

    cmds.file(new=True, force=True)

    cam = cmds.camera(name="testCamera")[0]
    cmds.setAttr(f"{cam}Shape.focalLength", 50)

    reader = SceneReader()
    scene_data = reader.extract_scene(include_aovs=False, include_materials=False)

    assert "cameras" in scene_data, "Should have cameras"
    cameras = scene_data["cameras"]

    assert len(cameras) >= 4, "Should have at least 4 cameras (default + custom)"

    test_cam = next((c for c in cameras if c["name"] == "testCamera"), None)
    assert test_cam is not None, "Should find testCamera"
    assert test_cam["focal_length"] == 50.0, "Focal length should be 50"

    print(f"✓ Extracted {len(cameras)} cameras")
    print(f"✓ Custom camera focal length: {test_cam['focal_length']}")


def test_mesh_extraction():
    """Test mesh extraction"""
    print("\n=== Test: Mesh Extraction ===")

    import maya.cmds as cmds
    from scene_reader import SceneReader

    cmds.file(new=True, force=True)

    cube = cmds.polyCube(name="testCube")[0]
    sphere = cmds.polySphere(name="testSphere")[0]

    reader = SceneReader()
    scene_data = reader.extract_scene(include_aovs=False, include_materials=False)

    assert "meshes" in scene_data, "Should have meshes"
    meshes = scene_data["meshes"]

    assert len(meshes) == 2, "Should have 2 meshes"

    cube_data = next((m for m in meshes if m["name"] == "testCube"), None)
    assert cube_data is not None, "Should find testCube"
    assert cube_data["geometry"]["vertex_count"] == 8, "Cube should have 8 vertices"
    assert cube_data["geometry"]["face_count"] == 6, "Cube should have 6 faces"

    print(f"✓ Extracted {len(meshes)} meshes")
    print(
        f"✓ Cube: {cube_data['geometry']['vertex_count']} verts, {cube_data['geometry']['face_count']} faces"
    )


def test_material_extraction():
    """Test material extraction"""
    print("\n=== Test: Material Extraction ===")

    import maya.cmds as cmds
    from scene_reader import SceneReader

    cmds.file(new=True, force=True)

    cube = cmds.polyCube(name="materialTestCube")[0]

    shader = cmds.shadingNode("lambert", asShader=True, name="testMaterial")
    cmds.setAttr(f"{shader}.color", 1, 0, 0, type="double3")
    sg = cmds.sets(
        renderable=True, noSurfaceShader=True, empty=True, name="testMaterialSG"
    )
    cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")

    cmds.select(cube)
    cmds.hyperShade(assign=shader)

    reader = SceneReader()
    scene_data = reader.extract_scene(include_aovs=False, include_materials=True)

    assert "materials" in scene_data, "Should have materials"
    materials = scene_data["materials"]

    test_mat = next((m for m in materials if m["name"] == "testMaterial"), None)
    assert test_mat is not None, "Should find testMaterial"
    assert test_mat["type"] == "lambert", "Material should be lambert"
    assert (
        "materialTestCube" in test_mat["assigned_objects"]
    ), "Material should be assigned to cube"

    color = test_mat["properties"]["color"]
    assert color == [1.0, 0.0, 0.0], "Color should be red [1, 0, 0]"

    print(f"✓ Extracted {len(materials)} materials")
    print(
        f"✓ Material '{test_mat['name']}' assigned to: {test_mat['assigned_objects']}"
    )
    print(f"✓ Material color: {color}")


def test_transform_matrix():
    """Test transform matrix extraction"""
    print("\n=== Test: Transform Matrix ===")

    import maya.cmds as cmds
    from scene_reader import SceneReader

    cmds.file(new=True, force=True)

    cube = cmds.polyCube(name="transformTestCube")[0]
    cmds.move(5, 10, 15, cube)

    reader = SceneReader()
    scene_data = reader.extract_scene(include_aovs=False, include_materials=False)

    cube_data = next(
        (m for m in scene_data["meshes"] if m["name"] == "transformTestCube"), None
    )
    assert cube_data is not None, "Should find cube"

    matrix = cube_data["transform"]
    x, y, z = matrix[12], matrix[13], matrix[14]

    assert abs(x - 5) < 0.001, f"X should be 5, got {x}"
    assert abs(y - 10) < 0.001, f"Y should be 10, got {y}"
    assert abs(z - 15) < 0.001, f"Z should be 15, got {z}"

    print(f"✓ Transform matrix extracted correctly")
    print(f"✓ Position: [{x}, {y}, {z}]")


def test_schema_version():
    """Test schema version is correct"""
    print("\n=== Test: Schema Version ===")

    import maya.cmds as cmds
    from scene_reader import SceneReader

    cmds.file(new=True, force=True)

    reader = SceneReader()
    scene_data = reader.extract_scene(include_aovs=False, include_materials=False)

    assert "schema_version" in scene_data, "Should have schema_version"
    assert scene_data["schema_version"] == "0.2.0", "Schema version should be 0.2.0"

    print(f"✓ Schema version: {scene_data['schema_version']}")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Maya Scene Reader Tests")
    print("=" * 60)

    tests = [
        test_scene_reader_basic,
        test_scene_info_extraction,
        test_camera_extraction,
        test_mesh_extraction,
        test_material_extraction,
        test_transform_matrix,
        test_schema_version,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    import maya.standalone

    maya.standalone.initialize()

    try:
        success = run_all_tests()
        exit_code = 0 if success else 1
    finally:
        maya.standalone.uninitialize()

    sys.exit(exit_code)
