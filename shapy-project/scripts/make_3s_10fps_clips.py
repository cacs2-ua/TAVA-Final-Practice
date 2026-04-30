from pathlib import Path
import subprocess
import json
import traceback

ROOT = Path("datasets_shapy_eval")

DATASETS = [
    "compas3d",
    "aistpp",
    "kth",
]

TARGET_DURATION = 3.0
TARGET_FPS = 10
TARGET_FRAMES = 30

def run(cmd, check=True):
    print("[RUN]", " ".join(map(str, cmd)))
    result = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if check and result.returncode != 0:
        if result.stdout.strip():
            print(result.stdout)
        if result.stderr.strip():
            print(result.stderr)
        raise RuntimeError(f"Command failed with exit code {result.returncode}")

    return result

def get_duration(video_path):
    result = run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=True,
    )

    value = result.stdout.strip()

    if not value:
        raise RuntimeError("ffprobe returned empty duration")

    return float(value)

def get_frame_count(video_path):
    result = run(
        [
            "ffprobe",
            "-v", "error",
            "-count_frames",
            "-select_streams", "v:0",
            "-show_entries", "stream=nb_read_frames",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        check=False,
    )

    value = result.stdout.strip()

    if value.isdigit():
        return int(value)

    return None

def make_clip(video_path, out_path, start):
    cmd = [
        "ffmpeg",
        "-y",
        "-ss", f"{start:.3f}",
        "-i", str(video_path),
        "-t", str(TARGET_DURATION),
        "-vf", f"fps={TARGET_FPS},setpts=PTS-STARTPTS",
        "-frames:v", str(TARGET_FRAMES),
        "-an",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out_path),
    ]

    run(cmd, check=True)

    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError(f"Output clip was not created or is empty: {out_path}")

all_manifest = []
all_skipped = []

for dataset_name in DATASETS:
    video_dir = ROOT / dataset_name / "videos"
    clip_dir = ROOT / dataset_name / "clips_3s_10fps"
    metadata_dir = ROOT / dataset_name / "metadata"

    clip_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    videos = sorted(
        list(video_dir.glob("*.mp4")) +
        list(video_dir.glob("*.avi")) +
        list(video_dir.glob("*.mov")) +
        list(video_dir.glob("*.mkv"))
    )

    print()
    print("=" * 80)
    print(f"[DATASET] {dataset_name}")
    print(f"[INFO] Input videos found: {len(videos)}")
    print(f"[INFO] Output folder: {clip_dir}")
    print("=" * 80)

    if not videos:
        print(f"[WARN] No videos found in {video_dir}")
        continue

    dataset_manifest = []
    dataset_skipped = []
    ok_count = 0

    for input_idx, video_path in enumerate(videos):
        print()
        print("-" * 80)
        print(f"[VIDEO] dataset={dataset_name} input_idx={input_idx} file={video_path.name}")

        out_path = clip_dir / f"{input_idx:02d}_{video_path.stem}_3s_10fps.mp4"

        try:
            duration = get_duration(video_path)

            if duration <= 0:
                raise RuntimeError(f"Invalid duration: {duration}")

            if duration >= TARGET_DURATION:
                start = max(0.0, (duration - TARGET_DURATION) / 2.0)
            else:
                start = 0.0

            print(f"[INFO] duration={duration:.3f}s start={start:.3f}s")

            make_clip(video_path, out_path, start)

            frame_count = get_frame_count(out_path)

            item = {
                "dataset": dataset_name,
                "status": "ok",
                "input_index": input_idx,
                "output_index": ok_count,
                "source_video": str(video_path),
                "source_duration_seconds": duration,
                "clip_start_seconds": start,
                "target_duration_seconds": TARGET_DURATION,
                "target_fps": TARGET_FPS,
                "target_frames": TARGET_FRAMES,
                "output_clip": str(out_path),
                "output_frame_count": frame_count,
            }

            dataset_manifest.append(item)
            all_manifest.append(item)

            ok_count += 1

            print(f"[OK] Saved: {out_path}")
            print(f"[OK] Frame count: {frame_count}")

        except Exception as exc:
            print(f"[SKIP] Corrupt/unreadable/problematic video ignored: {video_path}")
            print(f"[SKIP] Reason: {repr(exc)}")

            if out_path.exists() and out_path.stat().st_size == 0:
                out_path.unlink()

            skipped_item = {
                "dataset": dataset_name,
                "status": "skipped_corrupt_or_unreadable",
                "input_index": input_idx,
                "source_video": str(video_path),
                "error": repr(exc),
                "traceback": traceback.format_exc(),
            }

            dataset_skipped.append(skipped_item)
            all_skipped.append(skipped_item)

            continue

    manifest_path = metadata_dir / "clips_3s_10fps_manifest.json"
    skipped_path = metadata_dir / "clips_3s_10fps_skipped.json"

    manifest_path.write_text(json.dumps(dataset_manifest, indent=2))
    skipped_path.write_text(json.dumps(dataset_skipped, indent=2))

    print()
    print(f"[DONE] Dataset: {dataset_name}")
    print(f"[DONE] OK clips: {len(dataset_manifest)}")
    print(f"[DONE] Skipped videos: {len(dataset_skipped)}")
    print(f"[DONE] Dataset manifest: {manifest_path}")
    print(f"[DONE] Skipped manifest: {skipped_path}")

global_manifest_path = ROOT / "all_clips_3s_10fps_manifest.json"
global_skipped_path = ROOT / "all_clips_3s_10fps_skipped.json"

global_manifest_path.write_text(json.dumps(all_manifest, indent=2))
global_skipped_path.write_text(json.dumps(all_skipped, indent=2))

print()
print("=" * 80)
print("[DONE] All clip generation finished.")
print(f"[DONE] Total OK clips: {len(all_manifest)}")
print(f"[DONE] Total skipped videos: {len(all_skipped)}")
print("[DONE] Global manifest:", global_manifest_path)
print("[DONE] Global skipped manifest:", global_skipped_path)
print("=" * 80)
