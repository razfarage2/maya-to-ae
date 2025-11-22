# Maya → AE JSON Schema Documentation

**Schema Version**: 0.2.0

This document describes the JSON format exported by the Maya-to-AE bridge.

## Top-Level Structure

```json
{
  "export_info": { ... },
  "scene_data": { ... }
}
```

## Export Info

Metadata about the export itself:

```json
{
  "export_info": {
    "timestamp": "2025-01-15T10:30:00",
    "exporter_version": "0.2.0"
  }
}
```

## Scene Data

### Schema Version
```json
{
  "schema_version": "0.2.0"
}
```

### Scene Info
```json
{
  "scene_info": {
    "current_frame": 24.0,
    "frame_range": [1.0, 120.0],
    "fps": 24,
    "scene_file": "path/to/scene.ma",
    "up_axis": "y",
    "linear_unit": "cm",
    "angular_unit": "deg"
  }
}
```

### Cameras
Array of camera objects:

```json
{
  "cameras": [
    {
      "name": "persp",
      "shape_name": "perspShape",
      "transform": [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
      "focal_length": 35.0,
      "horizontal_film_aperture": 1.417,
      "vertical_film_aperture": 0.945,
      "near_clip": 0.1,
      "far_clip": 10000.0,
      "is_renderable": true
    }
  ]
}
```

**Transform Matrix**: 4x4 matrix as flat array (16 floats) in row-major order:
```
[m00, m01, m02, m03,
 m10, m11, m12, m13,
 m20, m21, m22, m23,
 m30, m31, m32, m33]
```
Where m30, m31, m32 are the translation (X, Y, Z).

### Meshes
Array of mesh objects:

```json
{
  "meshes": [
    {
      "name": "pCube1",
      "full_path": "|pCube1",
      "shape_name": "pCubeShape1",
      "transform": [1, 0, 0, 0, ...],
      "geometry": {
        "vertex_count": 8,
        "face_count": 6,
        "triangle_count": 12,
        "uv_sets": ["map1"],
        "has_uvs": true
      },
      "material": "lambert1",
      "visible": true
    }
  ]
}
```

### Lights
Array of light objects:

```json
{
  "lights": [
    {
      "name": "pointLight1",
      "type": "pointLight",
      "transform": [1, 0, 0, 0, ...],
      "color": [1.0, 1.0, 1.0],
      "intensity": 1.0,
      "enabled": true
    }
  ]
}
```

**Light Types**: `pointLight`, `directionalLight`, `spotLight`, `areaLight`, `ambientLight`

### Render Passes (NEW in v0.2.0)
AOV/render pass information:

```json
{
  "render_passes": {
    "renderer": "Arnold",
    "aovs": [
      {
        "name": "aiAOV_beauty",
        "type": "RGBA",
        "enabled": true,
        "data_type": "RGBA",
        "filter": "gaussian",
        "output_path": "path/to/renders/"
      },
      {
        "name": "aiAOV_diffuse",
        "type": "diffuse",
        "enabled": true,
        "data_type": "RGB",
        "filter": "gaussian",
        "output_path": "path/to/renders/"
      }
    ],
    "render_settings": {
      "resolution": {
        "width": 1920,
        "height": 1080,
        "aspect_ratio": 1.778
      },
      "frame_padding": 4,
      "image_format": "exr",
      "output_path": "path/to/renders/",
      "animation": true,
      "start_frame": 1.0,
      "end_frame": 120.0,
      "by_frame": 1.0
    }
  }
}
```

**Supported Renderers**: Arnold, Redshift, V-Ray, Maya Software, Maya Hardware 2.0

**Common AOV Types**:
- `RGBA` / `beauty` - Final composite
- `diffuse` - Diffuse lighting
- `specular` - Specular highlights
- `emission` - Emissive surfaces
- `N` - Surface normals
- `Z` - Depth/Z-depth

### Materials (NEW in v0.2.0)
Material/shader assignments:

```json
{
  "materials": [
    {
      "name": "redMaterial",
      "shading_engine": "redMaterialSG",
      "type": "lambert",
      "assigned_objects": ["pCube1", "pCube2"],
      "properties": {
        "color": [1.0, 0.0, 0.0],
        "diffuse": 0.8,
        "textures": {
          "color": "path/to/texture.png"
        }
      }
    }
  ]
}
```

**Common Shader Types**: `lambert`, `blinn`, `phong`, `aiStandardSurface`, `RedshiftMaterial`

## Version History

### 0.2.0 (Current)
- Added `render_passes` with AOV support
- Added `materials` with shader assignments
- Added `material` field to meshes
- Added render settings (resolution, format, frame range)

### 0.1.0
- Initial schema
- Basic scene info, cameras, meshes, lights
- Transform matrices, geometry stats

## Usage Notes

### Transform Matrices
All transforms are in world space as 4x4 matrices (16 floats). To extract position:
```javascript
const x = transform[12];
const y = transform[13];
const z = transform[14];
```

### Material Matching
Match meshes to materials using the `material` field in mesh data and `name` field in materials array.

### AOV Naming
AOV names may vary by renderer. Use the `type` field for standardized pass identification.

### File Paths
All file paths (textures, output paths) are absolute paths from the Maya scene.