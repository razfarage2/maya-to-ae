import sys
import argparse
from pathlib import Path
import traceback
import os


def main():
    parser = argparse.ArgumentParser(description="Maya-to-AE Bridge")
    parser.add_argument("scene_file", type=str, help="Path to .ma or .mb file")
    parser.add_argument("--render", action="store_true", help="Enable Render Mode")
    parser.add_argument(
        "--dry-run", action="store_true", help="Just check file validity"
    )
    parser.add_argument("--output", "-o", type=str, help="Output path template")
    parser.add_argument(
        "--aov", type=str, default="preview", help="AOV to render (default: preview)"
    )
    parser.add_argument(
        "--camera", type=str, default="persp", help="Camera to render from"
    )
    parser.add_argument("--frame", "-f", type=float, help="Single frame fallback")
    parser.add_argument("--start_frame", type=float, help="Start frame")
    parser.add_argument("--end_frame", type=float, help="End frame")
    parser.add_argument("--no-aovs", action="store_true")
    parser.add_argument("--no-materials", action="store_true")

    args = parser.parse_args()
    scene_path = Path(args.scene_file)
    try:
        import maya.standalone

        maya.standalone.initialize()
        import maya.cmds as cmds

        sys.stdout.write("[OK] Maya initialized\n")
    except Exception as e:
        print(f"CRITICAL ERROR: Maya Init Failed: {e}")
        sys.exit(1)

    try:
        if not scene_path.exists():
            raise FileNotFoundError(f"Scene file not found: {scene_path}")

        cmds.file(str(scene_path), open=True, force=True)
        if args.render:
            try:
                from renderer import SceneRenderer
            except ImportError:
                print("ERROR: Could not import 'renderer.py'.")
                sys.exit(1)

            if args.start_frame is not None and args.end_frame is not None:
                start_f = int(args.start_frame)
                end_f = int(args.end_frame)
            else:
                fallback = int(args.frame) if args.frame is not None else 1
                start_f = fallback
                end_f = fallback

            if args.output:
                out_template = Path(args.output)
            else:
                current_dir = Path(__file__).parent.absolute()
                temp_dir = current_dir.parent / "data" / "temp_render"
                out_template = temp_dir / f"{args.aov}"

            r = SceneRenderer()
            first_file_path = ""

            print(f"--- RENDER START: {args.aov} ({start_f}-{end_f}) ---")
            sys.stdout.flush()

            for f in range(start_f, end_f + 1):
                current_path = out_template.parent / f"{out_template.name}.{f:04d}.exr"

                result = r.render_pass(
                    aov_name=args.aov,
                    camera=args.camera,
                    frame=f,
                    output_path=str(current_path),
                )

                if f == start_f:
                    first_file_path = result

                sys.stdout.write(f"Rendering frame {f}...\n")
                sys.stdout.flush()

            print(f"RENDER_COMPLETE:{first_file_path}")
            sys.stdout.flush()

        else:
            from scene_reader import SceneReader
            from serializer import SceneSerializer

            if args.output:
                out_path = Path(args.output)
            else:
                out_dir = Path(__file__).parent.parent / "data" / "exports"
                out_dir.mkdir(parents=True, exist_ok=True)
                out_path = out_dir / "output.json"

            reader = SceneReader()
            scene_data = reader.extract_scene(
                include_aovs=not args.no_aovs, include_materials=not args.no_materials
            )

            serializer = SceneSerializer()
            serializer.write(scene_data, out_path)

            print(f"[OK] Metadata exported to {out_path}")

    except Exception as e:
        print(f"\nCRITICAL EXECUTION ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)

    finally:
        try:
            maya.standalone.uninitialize()
        except:
            pass


if __name__ == "__main__":
    main()
