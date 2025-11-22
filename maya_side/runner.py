import sys
import argparse
from pathlib import Path
import traceback


def main():
    parser = argparse.ArgumentParser(description="Maya-to-AE Bridge")

    parser.add_argument("scene_file", type=str, help="Path to .ma or .mb file")
    parser.add_argument("--output", "-o", type=str, help="Output path (JSON or Image)")
    parser.add_argument(
        "--frame", "-f", type=float, help="Frame number (default: current)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate without exporting"
    )

    parser.add_argument("--no-aovs", action="store_true", help="Skip AOV extraction")
    parser.add_argument(
        "--no-materials", action="store_true", help="Skip material extraction"
    )

    parser.add_argument("--render", action="store_true", help="Enable Render Mode")
    parser.add_argument(
        "--aov", type=str, help="Specific AOV to render (required for --render)"
    )
    parser.add_argument(
        "--camera", type=str, default="persp", help="Camera to render from"
    )

    args = parser.parse_args()

    scene_path = Path(args.scene_file)
    if not scene_path.exists():
        print(f"ERROR: Scene file not found: {scene_path}")
        sys.exit(1)

    try:
        import maya.standalone

        maya.standalone.initialize()
        import maya.cmds as cmds
        import maya.mel as mel

        print("Maya standalone initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize Maya standalone: {e}")
        sys.exit(1)

    try:
        print(f"Opening scene: {scene_path}")
        cmds.file(str(scene_path), open=True, force=True)

        if args.frame is not None:
            cmds.currentTime(args.frame)
            print(f"Set to frame {args.frame}")
        else:
            args.frame = cmds.currentTime(query=True)

        if args.render:
            if not args.aov:
                print("ERROR: --aov argument is required when using --render")
                sys.exit(1)

            print(f"--- STARTING SILENT RENDER [{args.aov}] ---")

            try:
                from renderer import SceneRenderer
            except ImportError:
                print(
                    "ERROR: Could not import 'renderer.py'. Ensure it is in the maya_side folder."
                )
                sys.exit(1)

            if args.output:
                output_path = args.output
            else:
                temp_dir = Path(__file__).parent.parent / "data" / "temp_render"
                output_path = temp_dir / f"{args.aov}.{int(args.frame):04d}.exr"

            r = SceneRenderer()
            final_path = r.render_pass(
                aov_name=args.aov,
                camera=args.camera,
                frame=args.frame,
                output_path=str(output_path),
            )

            print(f"RENDER_COMPLETE:{final_path}")
            sys.stdout.flush()

        else:
            print("--- STARTING METADATA EXTRACTION ---")

            from scene_reader import SceneReader
            from serializer import SceneSerializer

            if args.output:
                output_path = Path(args.output)
            else:
                output_dir = Path(__file__).parent.parent / "data" / "exports"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / "output.json"

            reader = SceneReader()
            scene_data = reader.extract_scene(
                include_aovs=not args.no_aovs, include_materials=not args.no_materials
            )

            print(f"Extracted: {len(scene_data.get('meshes', []))} meshes")

            if args.dry_run:
                print("\nDry run complete - scene is valid")
            else:
                serializer = SceneSerializer()
                serializer.write(scene_data, output_path)
                print(f"Export complete: {output_path}")

                size_kb = output_path.stat().st_size / 1024
                print(f"File size: {size_kb:.2f} KB")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

    finally:
        maya.standalone.uninitialize()
        print("\nMaya standalone shut down")


if __name__ == "__main__":
    main()
