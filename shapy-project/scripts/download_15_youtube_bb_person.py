from pathlib import Path
import gzip
import csv
import urllib.request
import subprocess
import json
from collections import OrderedDict

OUT_ROOT = Path("datasets_shapy_eval/youtube_bb")
VIDEO_DIR = OUT_ROOT / "videos"
META_DIR = OUT_ROOT / "metadata"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

CSV_URL = "https://research.google.com/youtube-bb/yt_bb_detection_validation.csv.gz"
CSV_GZ = META_DIR / "yt_bb_detection_validation.csv.gz"

print("[INFO] Downloading official YouTube-BB detection validation CSV...")
if not CSV_GZ.exists():
    urllib.request.urlretrieve(CSV_URL, CSV_GZ)

# YouTube-BB detection CSV columns:
# youtube_id,timestamp_ms,class_id,class_name,object_id,object_presence,xmin,xmax,ymin,ymax
segments = OrderedDict()

print("[INFO] Selecting 15 unique PERSON video segments...")
with gzip.open(CSV_GZ, "rt") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 10:
            continue

        youtube_id = row[0]
        timestamp_ms = int(row[1])
        class_name = row[3]
        object_id = row[4]
        presence = row[5]

        if class_name.lower() != "person":
            continue
        if presence.lower() != "present":
            continue

        key = (youtube_id, object_id)

        if key not in segments:
            start_s = max(0, timestamp_ms / 1000.0 - 2.0)
            end_s = start_s + 15.0

            segments[key] = {
                "youtube_id": youtube_id,
                "object_id": object_id,
                "start_s": round(start_s, 2),
                "end_s": round(end_s, 2),
                "class_name": class_name,
            }

        if len(segments) >= 15:
            break

selected = list(segments.values())

if len(selected) != 15:
    raise SystemExit(f"[ERROR] Expected 15 person segments, got {len(selected)}")

manifest = []

for idx, item in enumerate(selected):
    youtube_id = item["youtube_id"]
    start_s = item["start_s"]
    end_s = item["end_s"]

    out_path = VIDEO_DIR / f"{idx:02d}_{youtube_id}_person.mp4"
    url = f"https://www.youtube.com/watch?v={youtube_id}"

    cmd = [
        "yt-dlp",
        "-f", "mp4/bestvideo+bestaudio/best",
        "--download-sections", f"*{start_s}-{end_s}",
        "--force-keyframes-at-cuts",
        "--merge-output-format", "mp4",
        "-o", str(out_path),
        url,
    ]

    print(f"[DOWNLOAD] {idx:02d}: {url} [{start_s}, {end_s}]")

    result = subprocess.run(cmd, text=True)

    if result.returncode != 0 or not out_path.exists():
        print(f"[WARN] Failed to download {youtube_id}. This can happen if YouTube removed the video.")
        continue

    item["video_path"] = str(out_path)
    item["url"] = url
    manifest.append(item)

manifest_path = META_DIR / "manifest_15_youtube_bb_person.json"
manifest_path.write_text(json.dumps(manifest, indent=2))

print(f"[DONE] Downloaded {len(manifest)} videos")
print(f"[DONE] Manifest: {manifest_path}")

if len(manifest) != 15:
    raise SystemExit(
        f"[ERROR] Downloaded only {len(manifest)} videos. "
        "Some YouTube videos may be unavailable. Re-run the script or increase selection search."
    )
