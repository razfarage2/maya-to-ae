import maya.cmds as cmds
from typing import Dict, List, Any


class AOVManager:
    """Extract AOV/render pass information from Maya scene"""

    def __init__(self):
        self.renderer = self._detect_renderer()
        self.aovs = []

    def _detect_renderer(self) -> str:
        """Detect which renderer is being used"""
        current_renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")

        renderer_map = {
            "arnold": "Arnold",
            "redshift": "Redshift",
            "vray": "V-Ray",
            "mentalRay": "Mental Ray",
            "mayaSoftware": "Maya Software",
            "mayaHardware2": "Maya Hardware 2.0",
        }

        return renderer_map.get(current_renderer, current_renderer)

    def get_all_aovs(self) -> Dict[str, Any]:
        """Get all AOVs based on current renderer"""
        result = {
            "renderer": self.renderer,
            "aovs": [],
            "render_settings": self._get_render_settings(),
        }

        if self.renderer == "Arnold":
            result["aovs"] = self._get_arnold_aovs()
        elif self.renderer == "Redshift":
            result["aovs"] = self._get_redshift_aovs()
        else:
            result["aovs"] = self._get_default_aovs()

        return result

    def _get_arnold_aovs(self) -> List[Dict[str, Any]]:
        """Extract Arnold AOVs"""
        aovs = []

        try:
            if not cmds.pluginInfo("mtoa", query=True, loaded=True):
                print("Warning: Arnold plugin not loaded")
                return []

            aov_nodes = cmds.ls(type="aiAOV") or []

            for aov_node in aov_nodes:
                enabled = cmds.getAttr(f"{aov_node}.enabled")
                if not enabled:
                    continue

                aov_data = {
                    "name": aov_node,
                    "type": cmds.getAttr(f"{aov_node}.name"),
                    "enabled": enabled,
                    "data_type": self._get_arnold_aov_type(aov_node),
                    "filter": self._safe_get_attr(aov_node, "filter", "gaussian"),
                    "output_path": self._get_aov_output_path(aov_node),
                }
                aovs.append(aov_data)

            if not any(aov["type"] == "RGBA" for aov in aovs):
                aovs.insert(
                    0,
                    {
                        "name": "beauty",
                        "type": "RGBA",
                        "enabled": True,
                        "data_type": "RGBA",
                        "filter": "gaussian",
                        "output_path": self._get_default_output_path(),
                    },
                )

        except Exception as e:
            print(f"Error extracting Arnold AOVs: {e}")

        return aovs

    def _get_redshift_aovs(self) -> List[Dict[str, Any]]:
        """Extract Redshift AOVs"""
        aovs = []

        try:
            if not cmds.pluginInfo("redshift4maya", query=True, loaded=True):
                print("Warning: Redshift plugin not loaded")
                return []

            aov_nodes = cmds.ls(type="RedshiftAOV") or []

            for aov_node in aov_nodes:
                enabled = self._safe_get_attr(aov_node, "enabled", True)
                if not enabled:
                    continue

                aov_data = {
                    "name": aov_node,
                    "type": self._safe_get_attr(aov_node, "aovType", "unknown"),
                    "enabled": enabled,
                    "output_path": self._get_aov_output_path(aov_node),
                }
                aovs.append(aov_data)

        except Exception as e:
            print(f"Error extracting Redshift AOVs: {e}")

        return aovs

    def _get_default_aovs(self) -> List[Dict[str, Any]]:
        """Get basic render layers for default renderers"""
        aovs = []

        layers = cmds.ls(type="renderLayer") or []

        for layer in layers:
            if layer == "defaultRenderLayer":
                continue

            renderable = cmds.getAttr(f"{layer}.renderable")
            if renderable:
                aovs.append(
                    {
                        "name": layer,
                        "type": "render_layer",
                        "enabled": True,
                        "output_path": self._get_default_output_path(),
                    }
                )

        aovs.insert(
            0,
            {
                "name": "beauty",
                "type": "RGBA",
                "enabled": True,
                "output_path": self._get_default_output_path(),
            },
        )

        return aovs

    def _get_arnold_aov_type(self, aov_node: str) -> str:
        """Get Arnold AOV data type"""
        type_map = {0: "RGBA", 1: "RGB", 2: "VECTOR", 3: "FLOAT", 4: "INT"}
        type_value = self._safe_get_attr(aov_node, "type", 0)
        return type_map.get(type_value, "RGBA")

    def _get_render_settings(self) -> Dict[str, Any]:
        """Extract render settings"""
        settings = {
            "resolution": self._get_resolution(),
            "frame_padding": cmds.getAttr("defaultRenderGlobals.extensionPadding"),
            "image_format": self._get_image_format(),
            "output_path": self._get_default_output_path(),
            "animation": cmds.getAttr("defaultRenderGlobals.animation"),
            "start_frame": cmds.getAttr("defaultRenderGlobals.startFrame"),
            "end_frame": cmds.getAttr("defaultRenderGlobals.endFrame"),
            "by_frame": cmds.getAttr("defaultRenderGlobals.byFrameStep"),
        }
        return settings

    def _get_resolution(self) -> Dict[str, int]:
        """Get render resolution"""
        return {
            "width": cmds.getAttr("defaultResolution.width"),
            "height": cmds.getAttr("defaultResolution.height"),
            "aspect_ratio": cmds.getAttr("defaultResolution.deviceAspectRatio"),
        }

    def _get_image_format(self) -> str:
        """Get output image format"""
        format_map = {
            0: "iff",
            1: "tiff",
            2: "sgi",
            3: "als",
            4: "rla",
            5: "jpg",
            6: "tga",
            7: "bmp",
            8: "png",
            19: "tif",
            32: "exr",
        }
        format_value = cmds.getAttr("defaultRenderGlobals.imageFormat")
        return format_map.get(format_value, "exr")

    def _get_default_output_path(self) -> str:
        """Get default render output path"""
        workspace = cmds.workspace(query=True, rootDirectory=True)
        project_path = cmds.workspace(fileRuleEntry="images")
        return f"{workspace}{project_path}"

    def _get_aov_output_path(self, aov_node: str) -> str:
        """Get specific AOV output path"""
        return self._get_default_output_path()

    def _safe_get_attr(self, node: str, attr: str, default=None):
        """Safely get attribute with fallback"""
        try:
            return cmds.getAttr(f"{node}.{attr}")
        except:
            return default
