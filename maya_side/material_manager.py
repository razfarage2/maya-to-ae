import maya.cmds as cmds
from typing import Dict, List, Any, Optional


class MaterialManager:
    """Extract material/shader information from scene"""

    def get_all_materials(self) -> List[Dict[str, Any]]:
        """Get all materials in the scene"""
        materials = []

        shading_engines = cmds.ls(type="shadingEngine") or []

        for sg in shading_engines:
            if sg in ["initialShadingGroup", "initialParticleSE"]:
                continue

            material_data = self._extract_material_data(sg)
            if material_data:
                materials.append(material_data)

        return materials

    def _extract_material_data(self, shading_engine: str) -> Optional[Dict[str, Any]]:
        """Extract data from a shading engine"""
        connections = cmds.listConnections(
            f"{shading_engine}.surfaceShader", source=True
        )
        if not connections:
            return None

        shader = connections[0]
        shader_type = cmds.nodeType(shader)

        assigned_objects = self._get_assigned_objects(shading_engine)

        material_data = {
            "name": shader,
            "shading_engine": shading_engine,
            "type": shader_type,
            "assigned_objects": assigned_objects,
            "properties": self._get_shader_properties(shader, shader_type),
        }

        return material_data

    def _get_assigned_objects(self, shading_engine: str) -> List[str]:
        """Get objects assigned to this material"""
        assigned = []

        members = cmds.sets(shading_engine, query=True) or []

        for member in members:
            if cmds.nodeType(member) == "mesh":
                transforms = cmds.listRelatives(member, parent=True, fullPath=True)
                if transforms:
                    assigned.append(transforms[0].split("|")[-1])
            else:
                assigned.append(member)

        return list(set(assigned))

    def _get_shader_properties(self, shader: str, shader_type: str) -> Dict[str, Any]:
        """Extract basic shader properties"""
        properties = {}

        common_attrs = {
            "color": "color",
            "diffuse": "diffuse",
            "specular": "specularColor",
            "roughness": "roughness",
            "metalness": "metalness",
            "opacity": "opacity",
            "emission": "emissionColor",
        }

        for prop_name, attr_name in common_attrs.items():
            value = self._safe_get_attr(shader, attr_name)
            if value is not None:
                properties[prop_name] = value

        properties["textures"] = self._get_connected_textures(shader)

        return properties

    def _get_connected_textures(self, shader: str) -> Dict[str, str]:
        """Get file texture nodes connected to shader"""
        textures = {}

        texture_attrs = ["color", "diffuse", "normalCamera", "specularColor"]

        for attr in texture_attrs:
            full_attr = f"{shader}.{attr}"
            if cmds.objExists(full_attr):
                connections = cmds.listConnections(full_attr, source=True, type="file")
                if connections:
                    file_node = connections[0]
                    file_path = cmds.getAttr(f"{file_node}.fileTextureName")
                    textures[attr] = file_path

        return textures

    def _safe_get_attr(self, node: str, attr: str, default=None):
        """Safely get attribute with fallback"""
        try:
            if cmds.objExists(f"{node}.{attr}"):
                value = cmds.getAttr(f"{node}.{attr}")
                if isinstance(value, list) and len(value) == 1:
                    return list(value[0])
                return value
        except:
            pass
        return default

    def get_material_for_object(self, obj_name: str) -> Optional[str]:
        """Get material assigned to specific object"""
        try:
            shapes = cmds.listRelatives(obj_name, shapes=True, fullPath=True)
            if not shapes:
                return None

            shape = shapes[0]

            shading_engines = cmds.listConnections(shape, type="shadingEngine")
            if shading_engines:
                connections = cmds.listConnections(
                    f"{shading_engines[0]}.surfaceShader"
                )
                if connections:
                    return connections[0]
        except:
            pass

        return None
