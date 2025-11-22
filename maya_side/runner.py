import sys
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Extract Maya scene data to JSON")
    parser.add_argument("scene_file", type=str, help="Path to .ma or .mb file")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output JSON path (default: ./data/exports/output.json)",
    )
    parser.add_argument(
        "--frame",
        "-f",
        type=int,
        help="Frame to extract (default: current timeline frame)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Validate scene without exporting"
    )
    parser.add_argument(
        "--no-aovs", action="store_true", help="Skip AOV/render pass extraction"
    )
    parser.add_argument(
        "--no-materials", action="store_true", help="Skip material extraction"
    )

    args = parser.parse_args()

    scene_path = Path(args.scene_file)
    if not scene_path.exists():
        print(f"ERROR: Scene file not found: {scene_path}")
        sys.exit(1)

    if scene_path.suffix not in [".ma", ".mb"]:
        print(f"ERROR: File must be .ma or .mb, got: {scene_path.suffix}")
        sys.exit(1)

    output_path = args.output
    if not output_path:
        output_dir = Path(__file__).parent.parent / "data" / "exports"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "output.json"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Maya Scene Exporter")
    print(f"Scene: {scene_path}")
    print(f"Output: {output_path}")
    if args.frame:
        print(f"Frame: {args.frame}")
    if args.dry_run:
        print("Mode: DRY RUN (validation only)")
    print("-" * 50)

    try:
        import maya.standalone

        maya.standalone.initialize()
        print("✓ Maya standalone initialized")
    except Exception as e:
        print(f"ERROR: Failed to initialize Maya standalone: {e}")
        sys.exit(1)

    import maya.cmds as cmds
    from scene_reader import SceneReader
    from serializer import SceneSerializer

    try:
        print(f"Opening scene: {scene_path}")
        cmds.file(str(scene_path), open=True, force=True)
        print("✓ Scene opened")

        if args.frame:
            cmds.currentTime(args.frame)
            print(f"✓ Set to frame {args.frame}")

        print("Extracting scene data...")
        reader = SceneReader()
        scene_data = reader.extract_scene(
            include_aovs=not args.no_aovs, include_materials=not args.no_materials
        )

        print(
            f"✓ Extracted: {len(scene_data.get('meshes', []))} meshes, "
            f"{len(scene_data.get('cameras', []))} cameras"
        )

        if not args.no_aovs and "render_passes" in scene_data:
            aov_count = len(scene_data["render_passes"].get("aovs", []))
            renderer = scene_data["render_passes"].get("renderer", "Unknown")
            print(f"✓ Render passes: {aov_count} AOVs ({renderer})")

        if not args.no_materials and "materials" in scene_data:
            material_count = len(scene_data.get("materials", []))
            print(f"✓ Materials: {material_count}")

        if args.dry_run:
            print("\n✓ Dry run complete - scene is valid")
            print(f"Would export to: {output_path}")
        else:
            print(f"Writing JSON to: {output_path}")
            serializer = SceneSerializer()
            serializer.write(scene_data, output_path)
            print(f"✓ Export complete: {output_path}")

            size_kb = output_path.stat().st_size / 1024
            print(f"File size: {size_kb:.2f} KB")

    except Exception as e:
        print(f"\nERROR during extraction: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        maya.standalone.uninitialize()
        print("\n✓ Maya standalone shut down")


if __name__ == "__main__":
    main()
