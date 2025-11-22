import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class SceneSerializer:
    """Serialize Maya scene data to JSON format"""

    def __init__(self):
        self.indent = 2  # Pretty print by default

    def write(self, scene_data: Dict[str, Any], output_path: Path) -> None:
        """Write scene data to JSON file"""
        output_path = Path(output_path)

        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "exporter_version": "0.1.0",
            },
            "scene_data": scene_data,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=self.indent, ensure_ascii=False)

    def read(self, input_path: Path) -> Dict[str, Any]:
        """Read JSON file back into dict (for validation/testing)"""
        input_path = Path(input_path)

        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def validate_schema(self, data: Dict[str, Any]) -> bool:
        """Basic validation of scene data structure"""
        required_keys = ["schema_version", "scene_info", "cameras", "meshes"]

        scene_data = data.get("scene_data", {})

        for key in required_keys:
            if key not in scene_data:
                print(f"Validation error: Missing required key '{key}'")
                return False

        version = scene_data.get("schema_version")
        if not version or not isinstance(version, str):
            print("Validation error: Invalid schema_version")
            return False

        return True
