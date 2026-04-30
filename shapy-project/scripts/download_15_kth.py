from pathlib import Path
import urllib.request
import json
import subprocess
import time

OUT_ROOT = Path("datasets_shapy_eval/kth")
VIDEO_DIR = OUT_ROOT / "videos"
META_DIR = OUT_ROOT / "metadata"
TMP_DIR = OUT_ROOT / "tmp"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR.mkdir(parents=True, exist_ok=True)

# KTH official dataset naming pattern:
# person01_walking_d1_uncomp.avi, person02_walking_d1_uncomp.avi, ...
# We download exactly 15 individual videos.
ACTION = "walking"
SCENARIO = "d1"

BASE_URLS = [
    "https://www.csc.kth.se/cvap/actions",
    "http://www.csc.kth.se/cvap/actions",
    "https://www.nada.kth.se/cvap/actions",
    "http://www.nada.kth.se/cvap/actions",
]

selected = [
    f"person{person_id:02d}_{ACTION}_{SCENARIO}_uncomp.avi"
    for person_id in range(1, 16)
]

def download_one(filename, tmp_path):
    last_error = None

    for base in BASE_URLS:
        url = f"{base}/{ACTION}/{filename}"
        try:
            print(f"[TRY] {url}")
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()

            if len(data) < 1024:
                raise RuntimeError(f"Downloaded file too small: {len(data)} bytes")

            tmp_path.write_bytes(data)
            print(f"[OK] Downloaded: {url}")
            return url

        except Exception as exc:
            last_error = exc
            print(f"[WARN] Failed: {url} -> {exc}")
            time.sleep(0.5)

    raise RuntimeError(f"Could not download {filename}. Last error: {last_error}")

manifest = []

print("[1/3] Downloading exactly 15 individual KTH videos...")

for idx, filename in enumerate(selected):
    tmp_avi = TMP_DIR / filename
    out_mp4 = VIDEO_DIR / f"{idx:02d}_{filename.replace('.avi', '.mp4')}"

    if out_mp4.exists() and out_mp4.stat().st_size > 0:
        print(f"[OK] Already exists: {out_mp4}")
        manifest.append({
            "index": idx,
            "dataset": "KTH",
            "action": ACTION,
            "scenario": SCENARIO,
            "source_filename": filename,
            "video_path": str(out_mp4),
            "status": "already_exists",
        })
        continue

    source_url = download_one(filename, tmp_avi)

    print(f"[CONVERT] {tmp_avi.name} -> {out_mp4.name}")

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(tmp_avi),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-an",
        "-movflags", "+faststart",
        str(out_mp4),
    ]

    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not out_mp4.exists() or out_mp4.stat().st_size == 0:
        raise RuntimeError(f"Failed to create MP4: {out_mp4}")

    manifest.append({
        "index": idx,
        "dataset": "KTH",
        "action": ACTION,
        "scenario": SCENARIO,
        "source_filename": filename,
        "source_url": source_url,
        "video_path": str(out_mp4),
        "status": "downloaded",
    })

print("[2/3] Verifying exactly 15 videos...")

mp4_files = sorted(VIDEO_DIR.glob("*.mp4"))

print("[INFO] MP4 files:", len(mp4_files))
for p in mp4_files:
    print(" ", p)

if len(mp4_files) != 15:
    raise SystemExit(f"[ERROR] Expected exactly 15 KTH MP4 videos, got {len(mp4_files)}")

manifest_path = META_DIR / "manifest_15_kth.json"
manifest_path.write_text(json.dumps(manifest, indent=2))

print("[3/3] DONE.")
print("[DONE] Saved exactly 15 KTH videos in:", VIDEO_DIR)
print("[DONE] Manifest:", manifest_path)
