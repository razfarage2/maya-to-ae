import maya.cmds as cmds
from typing import Dict, List, Any


class SceneReader:
    """Extract scene data from the current Maya scene"""

    def __init__(self):
        self.scene_data = {}

    def extract_scene(
        self, include_aovs: bool = True, include_materials: bool = True
    ) -> Dict[str, Any]:
        """Extract all relevant scene data"""
        self.scene_data = {
            "schema_version": "0.2.0",  # Updated version
            "scene_info": self._get_scene_info(),
            "cameras": self._get_cameras(),
            "meshes": self._get_meshes(),
            "lights": self._get_lights(),
        }

        if include_aovs:
            from aov_manager import AOVManager

            aov_manager = AOVManager()
            self.scene_data["render_passes"] = aov_manager.get_all_aovs()

        if include_materials:
            from material_manager import MaterialManager

            material_manager = MaterialManager()
            self.scene_data["materials"] = material_manager.get_all_materials()

        return self.scene_data

    def _get_scene_info(self) -> Dict[str, Any]:
        """Get basic scene metadata"""
        current_frame = cmds.currentTime(query=True)
        start_frame = cmds.playbackOptions(query=True, minTime=True)
        end_frame = cmds.playbackOptions(query=True, maxTime=True)
        fps = self._get_fps()

        return {
            "current_frame": current_frame,
            "frame_range": [start_frame, end_frame],
            "fps": fps,
            "scene_file": cmds.file(query=True, sceneName=True),
            "up_axis": cmds.upAxis(query=True, axis=True),
            "linear_unit": cmds.currentUnit(query=True, linear=True),
            "angular_unit": cmds.currentUnit(query=True, angle=True),
        }

    def _get_fps(self) -> float:
        """Get frames per second from time unit"""
        time_unit = cmds.currentUnit(query=True, time=True)
        fps_map = {
            "film": 24,
            "pal": 25,
            "ntsc": 30,
            "show": 48,
            "palf": 50,
            "ntscf": 60,
        }
        return fps_map.get(time_unit, 24)

    def _get_cameras(self) -> List[Dict[str, Any]]:
        """Extract camera data"""
        cameras = []

        cam_shapes = cmds.ls(type="camera") or []

        for cam_shape in cam_shapes:
            cam_transform = cmds.listRelatives(cam_shape, parent=True)[0]

            cam_data = {
                "name": cam_transform,
                "shape_name": cam_shape,
                "transform": self._get_transform_matrix(cam_transform),
                "focal_length": cmds.getAttr(f"{cam_shape}.focalLength"),
                "horizontal_film_aperture": cmds.getAttr(
                    f"{cam_shape}.horizontalFilmAperture"
                ),
                "vertical_film_aperture": cmds.getAttr(
                    f"{cam_shape}.verticalFilmAperture"
                ),
                "near_clip": cmds.getAttr(f"{cam_shape}.nearClipPlane"),
                "far_clip": cmds.getAttr(f"{cam_shape}.farClipPlane"),
                "is_renderable": cmds.getAttr(f"{cam_shape}.renderable"),
            }
            cameras.append(cam_data)

        return cameras

    def _get_meshes(self) -> List[Dict[str, Any]]:
        """Extract mesh geometry and transforms"""
        meshes = []

        mesh_shapes = cmds.ls(type="mesh", long=True) or []

        for mesh_shape in mesh_shapes:
            if cmds.getAttr(f"{mesh_shape}.intermediateObject"):
                continue

            mesh_transform = cmds.listRelatives(mesh_shape, parent=True, fullPath=True)[
                0
            ]

            material = self._get_mesh_material(mesh_shape)

            mesh_data = {
                "name": mesh_transform.split("|")[-1],
                "full_path": mesh_transform,
                "shape_name": mesh_shape.split("|")[-1],
                "transform": self._get_transform_matrix(mesh_transform),
                "geometry": self._get_mesh_geometry(mesh_shape),
                "material": material,
                "visible": cmds.getAttr(f"{mesh_transform}.visibility"),
            }
            meshes.append(mesh_data)

        return meshes

    def _get_mesh_material(self, mesh_shape: str) -> str:
        """Get material name assigned to mesh"""
        try:
            shading_engines = cmds.listConnections(mesh_shape, type="shadingEngine")
            if shading_engines:
                connections = cmds.listConnections(
                    f"{shading_engines[0]}.surfaceShader"
                )
                if connections:
                    return connections[0]
        except:
            pass
        return "lambert1"

    def _get_mesh_geometry(self, mesh_shape: str) -> Dict[str, Any]:
        """Extract mesh geometry data (vertices, UVs, etc.)"""
        vertices = cmds.xform(
            f"{mesh_shape}.vtx[*]", query=True, translation=True, worldSpace=False
        )
        num_vertices = len(vertices) // 3

        num_faces = cmds.polyEvaluate(mesh_shape, face=True)
        num_triangles = cmds.polyEvaluate(mesh_shape, triangle=True)

        uv_sets = cmds.polyUVSet(mesh_shape, query=True, allUVSets=True) or []

        geometry = {
            "vertex_count": num_vertices,
            "face_count": num_faces,
            "triangle_count": num_triangles,
            "uv_sets": uv_sets,
            "has_uvs": len(uv_sets) > 0,
        }

        return geometry

    def _get_lights(self) -> List[Dict[str, Any]]:
        """Extract light data"""
        lights = []

        light_types = [
            "pointLight",
            "directionalLight",
            "spotLight",
            "areaLight",
            "ambientLight",
        ]

        for light_type in light_types:
            light_shapes = cmds.ls(type=light_type) or []

            for light_shape in light_shapes:
                light_transform = cmds.listRelatives(light_shape, parent=True)[0]

                light_data = {
                    "name": light_transform,
                    "type": light_type,
                    "transform": self._get_transform_matrix(light_transform),
                    "color": list(cmds.getAttr(f"{light_shape}.color")[0]),
                    "intensity": cmds.getAttr(f"{light_shape}.intensity"),
                    "enabled": not cmds.getAttr(f"{light_transform}.visibility") == 0,
                }
                lights.append(light_data)

        return lights

    def _get_transform_matrix(self, node: str) -> List[float]:
        """Get world space transform matrix as flat list of 16 floats"""
        matrix = cmds.xform(node, query=True, worldSpace=True, matrix=True)
        return matrix
