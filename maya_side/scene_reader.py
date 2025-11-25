import maya.cmds as cmds
from typing import Dict, List, Any


class SceneReader:
    def __init__(self):
        self.scene_data = {}

    def extract_scene(
        self, include_aovs: bool = True, include_materials: bool = True
    ) -> Dict[str, Any]:
        start = int(cmds.playbackOptions(query=True, minTime=True))
        end = int(cmds.playbackOptions(query=True, maxTime=True))

        self.scene_data = {
            "schema_version": "0.6.0",
            "scene_info": {
                "frame_range": [start, end],
                "fps": self._get_fps(),
                "scene_file": cmds.file(query=True, sceneName=True),
            },
            "cameras": self._get_cameras(start, end),
            "locators": self._get_locators(start, end),
            "meshes": self._get_meshes(start, end),
        }
        return self.scene_data

    def _get_fps(self) -> float:
        time_unit = cmds.currentUnit(query=True, time=True)
        fps_map = {
            "film": 24.0,
            "pal": 25.0,
            "ntsc": 30.0,
            "show": 48.0,
            "palf": 50.0,
            "ntscf": 60.0,
        }
        return fps_map.get(time_unit, 24.0)

    def _bake_transform(self, node: str, start: int, end: int) -> List[Dict[str, Any]]:
        data = []
        original_time = cmds.currentTime(query=True)

        for f in range(start, end + 1):
            cmds.currentTime(f)
            cmds.dgdirty(node)
            trans = cmds.xform(node, query=True, worldSpace=True, translation=True)
            rot = cmds.xform(node, query=True, worldSpace=True, rotation=True)

            data.append({"f": f, "t": trans, "r": rot})

        cmds.currentTime(original_time)
        return data

    def _get_cameras(self, start, end) -> List[Dict[str, Any]]:
        cameras = []
        for cam_shape in cmds.ls(type="camera") or []:
            if cmds.getAttr(f"{cam_shape}.orthographic"):
                continue
            if not cmds.getAttr(f"{cam_shape}.renderable"):
                continue

            transform = cmds.listRelatives(cam_shape, parent=True)[0]
            cameras.append(
                {
                    "name": transform,
                    "type": "camera",
                    "focal_length": cmds.getAttr(f"{cam_shape}.focalLength"),
                    "film_back": cmds.getAttr(f"{cam_shape}.horizontalFilmAperture")
                    * 25.4,
                    "animation": self._bake_transform(transform, start, end),
                }
            )
        return cameras

    def _get_locators(self, start, end) -> List[Dict[str, Any]]:
        selection = cmds.ls(selection=True, long=True) or []
        target_nodes = []

        if selection:
            target_nodes = selection
        else:
            shapes = cmds.ls(type="locator", long=True) or []
            if shapes:
                target_nodes = list(
                    set(cmds.listRelatives(shapes, parent=True, fullPath=True))
                )

        locators = []
        for node in target_nodes:
            shapes = cmds.listRelatives(node, shapes=True) or []
            if shapes:
                if cmds.nodeType(shapes[0]) != "locator":
                    continue

            short_name = node.split("|")[-1]
            locators.append(
                {
                    "name": short_name,
                    "type": "locator",
                    "animation": self._bake_transform(node, start, end),
                }
            )
        return locators

    def _get_meshes(self, start, end) -> List[Dict[str, Any]]:
        selection = cmds.ls(selection=True, long=True) or []
        meshes = []
        for node in selection:
            shapes = cmds.listRelatives(node, shapes=True) or []
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                short_name = node.split("|")[-1]
                meshes.append(
                    {
                        "name": short_name,
                        "type": "mesh",
                        "animation": self._bake_transform(node, start, end),
                    }
                )
        return meshes
