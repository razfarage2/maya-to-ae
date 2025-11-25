import maya.cmds as cmds
from typing import Dict, List, Any


class AOVManager:
    STANDARD_AOVS = [
        "N",
        "Z",
        "P",
        "ID",
        "motionvector",
        "diffuse",
        "specular",
        "coat",
        "sheen",
        "transmission",
        "sss",
        "emission",
        "background",
        "shadow_matte",
        "albedo",
    ]

    def __init__(self):
        self.renderer = self._detect_renderer()

    def _detect_renderer(self) -> str:
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
        aovs = []
        existing_names = set()

        try:
            if cmds.pluginInfo("mtoa", query=True, loaded=True):
                aov_nodes = cmds.ls(type="aiAOV") or []
                for aov_node in aov_nodes:
                    raw_name = cmds.getAttr(f"{aov_node}.name")
                    existing_names.add(raw_name)

                    aovs.append(
                        {
                            "name": raw_name,
                            "node": aov_node,
                            "type": "Custom",
                            "enabled": cmds.getAttr(f"{aov_node}.enabled"),
                            "status": "In Scene",
                        }
                    )
        except Exception as e:
            print(f"Error extracting Arnold AOVs: {e}")

        for std_name in self.STANDARD_AOVS:
            if std_name not in existing_names:
                aovs.append(
                    {
                        "name": std_name,
                        "node": None,
                        "type": "Standard",
                        "enabled": False,
                        "status": "Available",
                    }
                )

        if "beauty" not in existing_names:
            aovs.insert(
                0,
                {
                    "name": "beauty",
                    "node": None,
                    "type": "RGBA",
                    "enabled": True,
                    "status": "Default",
                },
            )

        return aovs

    def _get_redshift_aovs(self) -> List[Dict[str, Any]]:
        aovs = []
        try:
            if cmds.pluginInfo("redshift4maya", query=True, loaded=True):
                aov_nodes = cmds.ls(type="RedshiftAOV") or []
                for aov_node in aov_nodes:
                    aovs.append(
                        {
                            "name": aov_node,
                            "type": "Custom",
                            "enabled": self._safe_get_attr(aov_node, "enabled", True),
                            "status": "In Scene",
                        }
                    )
        except:
            pass
        return aovs

    def _get_default_aovs(self) -> List[Dict[str, Any]]:
        return [
            {"name": "beauty", "type": "RGBA", "enabled": True, "status": "Default"}
        ]

    def _get_render_settings(self) -> Dict[str, Any]:
        return {
            "resolution": {
                "width": self._safe_get_attr("defaultResolution", "width", 1920),
                "height": self._safe_get_attr("defaultResolution", "height", 1080),
            },
            "output_path": self._get_default_output_path(),
        }

    def _get_default_output_path(self) -> str:
        try:
            workspace = cmds.workspace(query=True, rootDirectory=True)
            project_path = cmds.workspace(fileRuleEntry="images")
            return f"{workspace}{project_path}"
        except:
            return ""

    def _safe_get_attr(self, node: str, attr: str, default=None):
        try:
            return cmds.getAttr(f"{node}.{attr}")
        except:
            return default
