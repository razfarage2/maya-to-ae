# Maya To AE

A Python-based Maya standalone exporter that extracts detailed scene data, including meshes, cameras, lights, materials, and AOVs (render passes), and serializes it into a structured JSON format. Designed for Passing AOVs into After effects with ease.
---

## Features

- **Scene Data Extraction**
  - Meshes: geometry, transforms, visibility, and assigned materials
  - Cameras: focal length, film aperture, clipping planes, and world transform
  - Lights: type, color, intensity, and transform
  - Scene metadata: frame range, FPS, up-axis, units

- **Material Extraction**
  - Shaders, shading engines, assigned objects
  - Shader properties: color, diffuse, specular, roughness, metalness, opacity, emission
  - Connected textures

- **AOV / Render Pass Extraction**
  - Arnold and Redshift supported
  - Detects enabled passes, types, and output paths
  - Includes default beauty pass for all renderers

- **Flexible Command-Line Interface**
  - Supports dry-run validation
  - Custom output paths
  - Frame-specific extraction
  - Optional skipping of materials or AOVs

- **JSON Serialization**
  - Pretty-printed JSON with schema versioning
  - Schema validation for consistent data structure

- **Automated Tests**
  - Tests for scene extraction, materials, AOVs, and JSON serialization
  - Compatible with Maya standalone Python (`mayapy`)

---

## Installation

1. **Maya Requirements**
   - Autodesk Maya 2023, 2024, or 2025
   - Plugins: Arnold (`mtoa`) or Redshift (`redshift4maya`) if using their AOVs

2. **Project Setup**
   ```bash
   git clone https://github.com/razfarage2/maya-to-ae.git
   cd maya-to-ae/maya_side
````

3. **Run Tests**
   On Windows PowerShell:

   ```powershell
   .\run_tests.ps1
   ```

   This script will detect installed `mayapy` versions and run the included test suite.

---

## Usage

### CLI Runner

```bash
mayapy runner.py <scene_file> [options]
```

#### Options

| Flag             | Description                                                   |
| ---------------- | ------------------------------------------------------------- |
| `-o, --output`   | Output JSON file path (default: `./data/exports/output.json`) |
| `-f, --frame`    | Frame to extract (default: current timeline frame)            |
| `--dry-run`      | Validate scene without exporting                              |
| `--no-aovs`      | Skip extraction of AOVs/render passes                         |
| `--no-materials` | Skip material extraction                                      |

### Example

```bash
mayapy runner.py myScene.mb --output data/exports/myScene.json --frame 10
```

---

## Project Structure

```
maya_side/
│
├─ aov_manager.py         # Extracts render passes / AOVs
├─ material_manager.py    # Extracts materials, shaders, and textures
├─ scene_reader.py        # Reads scene objects, cameras, lights, and geometry
├─ serializer.py          # Writes/reads JSON data and validates schema
├─ runner.py              # CLI entry point
├─ utils.py               # Helper functions for Maya operations
│
tests/
├─ test_aov_manager.py
├─ test_scene_reader.py
├─ test_serializer.py
│
scripts/
├─ run_tests.ps1          # PowerShell script to run all tests with mayapy
```

---

## Development Notes

* **Standalone Maya Mode**
  All extraction scripts are designed to run in Maya standalone mode (`maya.standalone.initialize()`), so no GUI is required.

* **Schema Versioning**
  Current schema version: `0.2.0`. Always check compatibility if updating the exporter.

* **Material & AOV Fallbacks**

  * If no AOVs are detected, a default beauty pass is inserted.
  * If no materials are assigned, meshes will reference `lambert1` as default.

* **Error Handling**

  * Safe attribute access via `_safe_get_attr`
  * Missing plugins are logged as warnings instead of failing

---

## Testing

* Run individual test files with `mayapy`, or use the PowerShell script `run_tests.ps1`.
* Tests cover:

  * SceneReader: meshes,  ameras, lights, materials
  * AOVManager: default, Arnold, Redshift passes
  * SceneSerializer: JSON write, read, and validation

---

## Contributions

Contributions are welcome! But please Reach out first

---

## License

MIT
---

## Contact

For support or questions, open an issue in this repository or contact the maintainer directly.
