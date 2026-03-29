import maya.cmds as cmds
import maya.mel as mel
from pathlib import Path
import os
import glob


class SceneRenderer:
    def __init__(self):
        pass

    def render_pass(self, aov_name: str, camera: str, frame: int, output_path: str):
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        prefix = target_path.with_suffix("").as_posix()

        cmds.currentTime(frame)

        use_preview = aov_name.lower() in ["preview", "beauty", "viewport"]

        if use_preview:
            return self._render_preview(camera, prefix, frame)
        else:
            return self._render_arnold(aov_name, camera, prefix, frame)

    def _render_preview(self, camera, prefix, frame):
        print(f"Preview Rendering frame {frame}...")

        cmds.setAttr(
            "defaultRenderGlobals.currentRenderer", "mayaSoftware", type="string"
        )
        cmds.setAttr("defaultRenderGlobals.imageFormat", 8)  # JPG
        cmds.setAttr("defaultRenderGlobals.imfPluginKey", "jpg", type="string")

        cmds.setAttr("defaultRenderGlobals.animation", 0)
        cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 0)
        cmds.setAttr("defaultRenderGlobals.extensionPadding", 0)
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", prefix, type="string")

        try:
            cmds.setAttr("defaultRenderQuality.edgeAntiAliasing", 0)
            cmds.setAttr("defaultRenderQuality.shadingSamples", 1)
        except:
            pass

        garbage = glob.glob(f"{prefix}*")
        for g in garbage:
            try:
                os.remove(g)
            except:
                pass

        try:
            cmds.render(camera, x=1920, y=1080)
        except Exception as e:
            print(f"Render Error: {e}")

        candidates = glob.glob(f"{prefix}*")
        if candidates:
            return str(candidates[0]).replace("\\", "/")

        return f"{prefix}.jpg"

    def _render_arnold(self, aov_name, camera, prefix, frame):
        print(f"Arnold Rendering {aov_name} frame {frame}...")

        self._enable_aov(aov_name)

        cmds.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")
        cmds.setAttr("defaultRenderGlobals.imageFormat", 32)  # EXR
        cmds.setAttr("defaultRenderGlobals.imfPluginKey", "exr", type="string")

        cmds.setAttr("defaultRenderGlobals.animation", 1)
        cmds.setAttr("defaultRenderGlobals.putFrameBeforeExt", 1)
        cmds.setAttr("defaultRenderGlobals.extensionPadding", 4)

        file_prefix = f"{prefix}_<RenderPass>"
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", file_prefix, type="string")

        try:
            cmds.setAttr("defaultArnoldRenderOptions.AASamples", 1)
            cmds.setAttr("defaultArnoldRenderOptions.GIDiffuseSamples", 1)
            cmds.setAttr("defaultArnoldRenderOptions.motion_blur_enable", 0)
        except:
            pass

        search_pattern = f"{prefix}*.{frame:04d}.exr"
        for old in glob.glob(search_pattern):
            try:
                os.remove(old)
            except:
                pass

        try:
            cmds.arnoldRender(width=1920, height=1080, camera=camera)
        except:
            cmds.render(camera, x=1920, y=1080)

        candidates = glob.glob(search_pattern)

        if not candidates:
            print("Warning: No Arnold output found.")
            return f"{prefix}.exr"
        best_match = None
        clean_name = aov_name.replace("aiAOV_", "")

        for c in candidates:
            c_name = Path(c).name.lower()
            if f"_{aov_name.lower()}." in c_name or f"_{clean_name.lower()}." in c_name:
                best_match = c
                break

        if best_match:
            return str(best_match).replace("\\", "/")

        return str(candidates[0]).replace("\\", "/")

    def _enable_aov(self, target_aov):
        all_aovs = cmds.ls(type="aiAOV") or []
        for aov in all_aovs:
            try:
                cmds.setAttr(f"{aov}.enabled", 0)
            except:
                pass

        found = False
        for aov in all_aovs:
            try:
                name_attr = cmds.getAttr(f"{aov}.name")
            except:
                name_attr = ""

            if name_attr == target_aov or aov == target_aov:
                cmds.setAttr(f"{aov}.enabled", 1)
                found = True

        if not found:
            try:
                import mtoa.aovs as aovs

                aovs.AOVInterface().addAOV(target_aov)
                for n in cmds.ls(type="aiAOV"):
                    if cmds.getAttr(f"{n}.name") == target_aov:
                        cmds.setAttr(f"{n}.enabled", 1)
            except:
                pass
