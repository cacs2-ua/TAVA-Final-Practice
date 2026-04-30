from pathlib import Path
import shutil
import json
import subprocess
from datasets import load_dataset, Video

OUT_ROOT = Path("datasets_shapy_eval/compas3d")
VIDEO_DIR = OUT_ROOT / "videos"
META_DIR = OUT_ROOT / "metadata"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

print("[INFO] Loading CoMPAS3D from local Hugging Face cache...")
ds = load_dataset("Rosie-Lab/compas3d", split="train")

# IMPORTANT:
# Do not decode videos. Otherwise datasets requires decord.
ds = ds.cast_column("video", Video(decode=False))

manifest = []

for i, row in enumerate(ds):
    if len(manifest) >= 15:
        break

    video = row.get("video")
    label = str(row.get("label", f"compas3d_{i:02d}"))

    if not isinstance(video, dict):
        print(f"[WARN] Row {i}: unsupported video object: {type(video)}")
        continue

    src_path = video.get("path")
    video_bytes = video.get("bytes")

    safe_label = label.replace("/", "_").replace(" ", "_").replace(":", "_")
    out_path = VIDEO_DIR / f"{len(manifest):02d}_{safe_label}.mp4"

    try:
        if video_bytes is not None:
            tmp_path = VIDEO_DIR / f"tmp_{len(manifest):02d}_{safe_label}"
            tmp_path.write_bytes(video_bytes)

            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(tmp_path),
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-crf", "23",
                    "-an",
                    "-movflags", "+faststart",
                    str(out_path),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            tmp_path.unlink(missing_ok=True)

        elif src_path is not None:
            src_path = Path(src_path)

            if not src_path.exists():
                print(f"[WARN] Row {i}: source path does not exist: {src_path}")
                continue

            if src_path.suffix.lower() == ".mp4":
                shutil.copy2(src_path, out_path)
            else:
                subprocess.run(
                    [
                        "ffmpeg", "-y",
                        "-i", str(src_path),
                        "-c:v", "libx264",
                        "-preset", "veryfast",
                        "-crf", "23",
                        "-an",
                        "-movflags", "+faststart",
                        str(out_path),
                    ],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        else:
            print(f"[WARN] Row {i}: video has neither path nor bytes")
            continue

        if not out_path.exists() or out_path.stat().st_size == 0:
            print(f"[WARN] Row {i}: output was not created correctly")
            continue

        manifest.append({
            "index": len(manifest),
            "row_index": i,
            "label": label,
            "source_path": str(src_path) if src_path is not None else None,
            "video_path": str(out_path),
        })

        print(f"[OK] {len(manifest):02d}/15 -> {out_path}")

    except Exception as exc:
        print(f"[WARN] Row {i} failed: {exc}")
        if out_path.exists() and out_path.stat().st_size == 0:
            out_path.unlink()

manifest_path = META_DIR / "manifest_15_compas3d.json"
manifest_path.write_text(json.dumps(manifest, indent=2))

print(f"[DONE] Saved {len(manifest)} videos")
print(f"[DONE] Manifest: {manifest_path}")

if len(manifest) != 15:
    raise SystemExit(f"[ERROR] Expected 15 videos, got {len(manifest)}")
