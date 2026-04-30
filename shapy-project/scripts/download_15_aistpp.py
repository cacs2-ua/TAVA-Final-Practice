from pathlib import Path
import urllib.request
import zipfile
import json
import time

OUT_ROOT = Path("datasets_shapy_eval/aistpp")
VIDEO_DIR = OUT_ROOT / "videos"
META_DIR = OUT_ROOT / "metadata"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)

MOTIONS_ZIP_URL = "https://github.com/google/aistplusplus_dataset/releases/download/v1.0/motions.zip"
MOTIONS_ZIP = META_DIR / "motions.zip"

VIDEO_BASE_URL = "https://aistdancedb.ongaaccel.jp/v1.0.0/video/10M"

def download_file(url, dst, retries=2):
    if dst.exists() and dst.stat().st_size > 0:
        print(f"[OK] Already exists: {dst}")
        return True

    for attempt in range(1, retries + 1):
        try:
            print(f"[DOWNLOAD] {url}")
            urllib.request.urlretrieve(url, dst)
            if dst.exists() and dst.stat().st_size > 0:
                print(f"[OK] Saved: {dst}")
                return True
        except Exception as exc:
            print(f"[WARN] Attempt {attempt}/{retries} failed: {exc}")
            time.sleep(1)

    if dst.exists() and dst.stat().st_size == 0:
        dst.unlink()

    return False

print("[1/4] Downloading AIST++ motions.zip if needed...")
download_file(MOTIONS_ZIP_URL, MOTIONS_ZIP, retries=5)

print("[2/4] Extracting valid AIST++ sequence names...")
with zipfile.ZipFile(MOTIONS_ZIP, "r") as zf:
    names = zf.namelist()

seq_names = []

for name in names:
    # Ignore macOS metadata garbage inside the zip.
    if "__MACOSX" in name:
        continue

    filename = Path(name).name

    if filename.startswith("._"):
        continue

    if not filename.endswith(".pkl"):
        continue

    stem = Path(filename).stem

    if stem.startswith("._"):
        continue

    if "_cAll_" not in stem:
        continue

    seq_names.append(stem)

seq_names = sorted(set(seq_names))

print(f"[INFO] Valid motion sequences found: {len(seq_names)}")

if len(seq_names) == 0:
    raise SystemExit("[ERROR] No valid AIST++ sequence names found.")

print("[INFO] First 10 valid names:")
for s in seq_names[:10]:
    print(" ", s)

print("[3/4] Downloading exactly 15 real AIST videos...")

manifest = []
used_video_names = set()

for seq in seq_names:
    if len(manifest) >= 15:
        break

    # AIST++ annotation names use cAll.
    # Real videos use concrete camera IDs c01...c09.
    for cam_idx in range(1, 10):
        cam = f"c{cam_idx:02d}"
        video_name = seq.replace("_cAll_", f"_{cam}_")

        if video_name.startswith("._"):
            continue

        if video_name in used_video_names:
            continue

        url = f"{VIDEO_BASE_URL}/{video_name}.mp4"
        out_path = VIDEO_DIR / f"{len(manifest):02d}_{video_name}.mp4"

        print(f"[TRY] {len(manifest):02d}: {video_name}")

        ok = download_file(url, out_path, retries=1)

        if ok:
            manifest.append({
                "index": len(manifest),
                "aistpp_sequence": seq,
                "camera": cam,
                "video_name": video_name,
                "url": url,
                "video_path": str(out_path),
            })
            used_video_names.add(video_name)
            print(f"[OK] Added video {len(manifest)}/15: {out_path}")
            break

if len(manifest) != 15:
    raise SystemExit(f"[ERROR] Expected exactly 15 videos, downloaded {len(manifest)}")

manifest_path = META_DIR / "manifest_15_aistpp.json"
manifest_path.write_text(json.dumps(manifest, indent=2))

print("[4/4] Done.")
print(f"[DONE] Saved exactly {len(manifest)} videos")
print(f"[DONE] Manifest: {manifest_path}")
