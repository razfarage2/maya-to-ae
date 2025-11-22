# Maya-AE Bridge Tests

Automated tests for the Maya to After Effects bridge.

## Running Tests

### Run All Tests (Recommended)
```powershell
.\run_tests.ps1
```

### Run Individual Test Files
```powershell
& "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" tests\test_serializer.py

& "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" tests\test_scene_reader.py

& "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" tests\test_aov_manager.py
```

## Test Coverage

### test_serializer.py
Tests JSON serialization and deserialization:
- ✓ Writing JSON to file
- ✓ Reading JSON from file
- ✓ Schema validation
- ✓ JSON formatting (indentation, readability)

### test_scene_reader.py
Tests Maya scene data extraction:
- ✓ Basic scene reader initialization
- ✓ Scene info extraction (FPS, frame range, units)
- ✓ Camera extraction (default + custom cameras)
- ✓ Mesh extraction (geometry, vertex counts)
- ✓ Material extraction and assignments
- ✓ Transform matrix extraction
- ✓ Schema version verification

### test_aov_manager.py
Tests AOV/render pass extraction:
- ✓ AOV manager initialization
- ✓ Renderer detection (Arnold, Maya Software, etc.)
- ✓ Render settings extraction (resolution, frame range)
- ✓ Default AOVs (beauty pass)
- ✓ Arnold AOVs (diffuse, specular, etc.)

## Test Structure

Each test file:
1. Initializes Maya standalone environment
2. Creates test scenes programmatically
3. Runs assertions on extracted data
4. Cleans up after itself
5. Reports pass/fail status

## Expected Output

Successful test run:
```
============================================================
Running Maya Scene Reader Tests
============================================================

=== Test: Basic Scene Reader ===
✓ SceneReader initialized

=== Test: Scene Info Extraction ===
✓ Scene info: Frame 50, Range [1.0, 100.0]

...

============================================================
Results: 7 passed, 0 failed
============================================================
```

## Adding New Tests

1. Create new test file in `tests/` directory
2. Import necessary modules
3. Write test functions (prefix with `test_`)
4. Add to `run_tests.ps1` test list
5. Run tests to verify

Example test function:
```python
def test_my_feature():
    print("\n=== Test: My Feature ===")
    
    import maya.cmds as cmds
    cmds.file(new=True, force=True)
    
    result = my_function()
    
    assert result is not None, "Result should not be None"
    assert result['value'] == 42, "Value should be 42"
    
    print("✓ Test passed")
```

## Troubleshooting

### "Maya standalone failed to initialize"
- Make sure mayapy path is correct
- Check Maya installation is complete
- Try running Maya normally first

### "Module not found"
- Check sys.path in test file
- Verify maya_side directory exists
- Ensure __init__.py exists in maya_side

### Tests hang or don't complete
- Maya standalone might not be shutting down
- Check for infinite loops
- Add timeouts if needed

## CI/CD Integration

These tests can be run in CI/CD pipelines:
```yaml
- name: Run Tests
  run: |
    & "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" -c "
    import sys
    sys.exit(0 if all_tests_pass() else 1)
    "
```