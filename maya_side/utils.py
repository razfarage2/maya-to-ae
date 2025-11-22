import maya.cmds as cmds
from typing import List, Optional


def get_selected_objects() -> List[str]:
    """Get currently selected objects in Maya"""
    return cmds.ls(selection=True, long=True) or []


def print_scene_stats():
    """Print quick scene statistics for debugging"""
    meshes = cmds.ls(type="mesh", long=True) or []
    cameras = cmds.ls(type="camera") or []
    lights = cmds.ls(type="light") or []

    print(f"Scene Statistics:")
    print(f"  Meshes: {len(meshes)}")
    print(f"  Cameras: {len(cameras)}")
    print(f"  Lights: {len(lights)}")
    print(f"  Current Frame: {cmds.currentTime(query=True)}")


def safe_get_attr(node: str, attr: str, default=None):
    """Safely get Maya attribute with fallback"""
    try:
        return cmds.getAttr(f"{node}.{attr}")
    except:
        return default


def is_valid_maya_scene(file_path: str) -> bool:
    """Check if file is a valid Maya scene"""
    from pathlib import Path

    path = Path(file_path)
    return path.exists() and path.suffix in [".ma", ".mb"]
