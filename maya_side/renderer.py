import maya.cmds as cmds
import maya.mel as mel
from pathlib import Path
import os


class SceneRenderer:
    def __init__(self):
        self.valid_renderers = ["arnold", "redshift"]

    def render_pass(self, aov_name: str, camera: str, frame: int, output_path: str):
        renderer = self._get_renderer()
        self._set_preview_quality(renderer)

        self._isolate_aov(aov_name, renderer)

        cmds.currentTime(frame)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        prefix = output_path.with_suffix("").as_posix()
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", prefix, type="string")

        print(f"Rendering {aov_name} at frame {frame} to {output_path}...")

        if renderer == "arnold":
            try:
                cmds.arnoldRender(width=1920, height=1080, camera=camera)
            except Exception as e:
                print(f"Arnold render warning (usually safe to ignore): {e}")
        else:
            cmds.render(camera, x=1920, y=1080)

        return str(output_path)

    def _get_renderer(self):
        return cmds.getAttr("defaultRenderGlobals.currentRenderer")

    def _set_preview_quality(self, renderer):
        if renderer == "arnold":
            cmds.setAttr("defaultArnoldRenderOptions.AASamples", 1)
            cmds.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", 1)
            cmds.setAttr("defaultArnoldRenderOptions.GISpecularSamples", 1)
            cmds.setAttr("defaultArnoldRenderOptions.GITransmissionSamples", 1)

    def _isolate_aov(self, target_aov: str, renderer):
        if renderer != "arnold":
            return

        aovs = cmds.ls(type="aiAOV") or []
        found = False

        for aov in aovs:
            aov_attr_name = cmds.getAttr(f"{aov}.name")
            if aov_attr_name == target_aov or aov == target_aov:
                cmds.setAttr(f"{aov}.enabled", 1)
                found = True
            else:
                cmds.setAttr(f"{aov}.enabled", 0)

        if not found:
            print(f"AOV '{target_aov}' not found. Injecting temporary AOV...")
            import mtoa.aovs as aovs

            aovs.AOVInterface().addAOV(target_aov)
