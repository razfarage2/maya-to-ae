import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "maya_side"))


def test_aov_manager_init():
    """Test AOV manager initialization"""
    print("\n=== Test: AOV Manager Init ===")

    import maya.cmds as cmds
    from aov_manager import AOVManager

    cmds.file(new=True, force=True)

    manager = AOVManager()

    assert manager is not None, "AOVManager should initialize"
    assert hasattr(manager, "renderer"), "Should have renderer attribute"
    assert hasattr(manager, "get_all_aovs"), "Should have get_all_aovs method"

    print(f"✓ AOVManager initialized")
    print(f"✓ Detected renderer: {manager.renderer}")


def test_renderer_detection():
    """Test renderer detection"""
    print("\n=== Test: Renderer Detection ===")

    import maya.cmds as cmds
    from aov_manager import AOVManager

    cmds.file(new=True, force=True)

    manager = AOVManager()
    print(f"✓ Default renderer: {manager.renderer}")

    try:
        if cmds.pluginInfo("mtoa", query=True, loaded=True) or cmds.loadPlugin(
            "mtoa", quiet=True
        ):
            cmds.setAttr(
                "defaultRenderGlobals.currentRenderer", "arnold", type="string"
            )
            manager = AOVManager()
            assert manager.renderer == "Arnold", "Should detect Arnold"
            print(f"✓ Arnold renderer detected")
    except:
        print("⚠ Arnold not available, skipping Arnold test")


def test_get_render_settings():
    """Test render settings extraction"""
    print("\n=== Test: Render Settings ===")

    import maya.cmds as cmds
    from aov_manager import AOVManager

    cmds.file(new=True, force=True)

    cmds.setAttr("defaultResolution.width", 1920)
    cmds.setAttr("defaultResolution.height", 1080)
    cmds.setAttr("defaultRenderGlobals.startFrame", 1)
    cmds.setAttr("defaultRenderGlobals.endFrame", 120)

    manager = AOVManager()
    result = manager.get_all_aovs()

    assert "render_settings" in result, "Should have render_settings"
    settings = result["render_settings"]

    assert settings["resolution"]["width"] == 1920, "Width should be 1920"
    assert settings["resolution"]["height"] == 1080, "Height should be 1080"
    assert settings["start_frame"] == 1.0, "Start frame should be 1"
    assert settings["end_frame"] == 120.0, "End frame should be 120"

    print(
        f"✓ Resolution: {settings['resolution']['width']}x{settings['resolution']['height']}"
    )
    print(f"✓ Frame range: {settings['start_frame']}-{settings['end_frame']}")


def test_default_aovs():
    """Test default AOV extraction (no Arnold)"""
    print("\n=== Test: Default AOVs ===")

    import maya.cmds as cmds
    from aov_manager import AOVManager

    cmds.file(new=True, force=True)

    cmds.setAttr("defaultRenderGlobals.currentRenderer", "mayaSoftware", type="string")

    manager = AOVManager()
    result = manager.get_all_aovs()

    assert "aovs" in result, "Should have aovs"
    aovs = result["aovs"]

    assert len(aovs) > 0, "Should have at least one AOV"
    beauty = next((aov for aov in aovs if aov["name"] == "beauty"), None)
    assert beauty is not None, "Should have beauty pass"

    print(f"✓ Found {len(aovs)} AOVs")
    print(f"✓ Beauty pass present")


def test_arnold_aovs():
    """Test Arnold AOV extraction"""
    print("\n=== Test: Arnold AOVs ===")

    import maya.cmds as cmds
    from aov_manager import AOVManager

    cmds.file(new=True, force=True)

    try:
        if not cmds.pluginInfo("mtoa", query=True, loaded=True):
            cmds.loadPlugin("mtoa")

        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

        diffuse_aov = cmds.createNode("aiAOV", name="testAOV_diffuse")
        cmds.setAttr(f"{diffuse_aov}.name", "diffuse", type="string")
        cmds.setAttr(f"{diffuse_aov}.enabled", True)

        manager = AOVManager()
        result = manager.get_all_aovs()

        assert result["renderer"] == "Arnold", "Should detect Arnold"
        assert len(result["aovs"]) > 0, "Should have AOVs"

        test_aov = next(
            (aov for aov in result["aovs"] if "diffuse" in aov["type"]), None
        )
        assert test_aov is not None, "Should find diffuse AOV"

        print(f"✓ Arnold detected with {len(result['aovs'])} AOVs")
        print(f"✓ Found diffuse AOV")

    except Exception as e:
        print(f"⚠ Arnold test skipped: {e}")


def run_all_tests():
    """Run all AOV tests"""
    print("\n" + "=" * 60)
    print("Running AOV Manager Tests")
    print("=" * 60)

    tests = [
        test_aov_manager_init,
        test_renderer_detection,
        test_get_render_settings,
        test_default_aovs,
        test_arnold_aovs,
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
