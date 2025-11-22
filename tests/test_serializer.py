import sys
import os
import json
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent / "maya_side"))

from serializer import SceneSerializer


def test_serializer_write():
    """Test writing JSON to file"""
    print("\n=== Test: Serializer Write ===")

    serializer = SceneSerializer()

    test_data = {
        "schema_version": "0.2.0",
        "scene_info": {"fps": 24, "frame_range": [1, 100]},
        "meshes": [{"name": "testCube", "vertex_count": 8}],
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)

    try:
        serializer.write(test_data, temp_path)

        assert temp_path.exists(), "File should be created"

        with open(temp_path, "r") as f:
            saved_data = json.load(f)

        assert "export_info" in saved_data, "Should have export_info"
        assert "scene_data" in saved_data, "Should have scene_data"
        assert (
            saved_data["scene_data"]["schema_version"] == "0.2.0"
        ), "Schema version should match"

        print(f"✓ Successfully wrote JSON to {temp_path}")
        print(f"✓ File size: {temp_path.stat().st_size} bytes")

    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_serializer_read():
    """Test reading JSON from file"""
    print("\n=== Test: Serializer Read ===")

    serializer = SceneSerializer()

    test_data = {
        "export_info": {
            "timestamp": "2025-01-15T10:00:00",
            "exporter_version": "0.2.0",
        },
        "scene_data": {"schema_version": "0.2.0", "meshes": []},
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)
        json.dump(test_data, f)

    try:
        loaded_data = serializer.read(temp_path)

        assert "export_info" in loaded_data, "Should have export_info"
        assert "scene_data" in loaded_data, "Should have scene_data"
        assert (
            loaded_data["export_info"]["exporter_version"] == "0.2.0"
        ), "Version should match"

        print(f"✓ Successfully read JSON from {temp_path}")

    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_serializer_validation():
    """Test schema validation"""
    print("\n=== Test: Schema Validation ===")

    serializer = SceneSerializer()

    valid_data = {
        "export_info": {},
        "scene_data": {
            "schema_version": "0.2.0",
            "scene_info": {},
            "cameras": [],
            "meshes": [],
        },
    }

    assert serializer.validate_schema(valid_data) == True, "Valid data should pass"
    print("✓ Valid schema passed validation")

    invalid_data = {"export_info": {}, "scene_data": {"schema_version": "0.2.0"}}

    assert serializer.validate_schema(invalid_data) == False, "Invalid data should fail"
    print("✓ Invalid schema failed validation (as expected)")


def test_json_format():
    """Test JSON formatting and readability"""
    print("\n=== Test: JSON Format ===")

    serializer = SceneSerializer()

    test_data = {
        "schema_version": "0.2.0",
        "meshes": [{"name": "cube1", "vertices": 8}, {"name": "cube2", "vertices": 8}],
    }

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)

    try:
        serializer.write(test_data, temp_path)

        with open(temp_path, "r") as f:
            content = f.read()

        assert "\n" in content, "Should have newlines (pretty print)"
        assert "  " in content, "Should have indentation"

        print("✓ JSON is properly formatted with indentation")

    finally:
        if temp_path.exists():
            temp_path.unlink()


def run_all_tests():
    """Run all serializer tests"""
    print("\n" + "=" * 60)
    print("Running Serializer Tests")
    print("=" * 60)

    tests = [
        test_serializer_write,
        test_serializer_read,
        test_serializer_validation,
        test_json_format,
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
    success = run_all_tests()
    sys.exit(0 if success else 1)
