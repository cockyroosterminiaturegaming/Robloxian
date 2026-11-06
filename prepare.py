#!/usr/bin/env python3
"""Sort clips oldest to newest, lower audio pitch, and build the upload queue.

Usage: python prepare.py
Reads config.json. Safe to re-run: already-processed clips are skipped,
and existing queue entries (and their upload status) are preserved.
"""
import json, re, subprocess, sys
from pathlib import Path

cfg = json.loads(Path("config.json").read_text())
src, dst = Path(cfg["clips_dir"]), Path(cfg["processed_dir"])
qfile = Path(cfg["queue_file"])
ratio = cfg.get("pitch_ratio")  # null = clips already pitch-shifted, skip processing
if ratio is not None:
    dst.mkdir(exist_ok=True)

def age_key(p):
    s = p.stat()
    t = s.st_ctime if cfg.get("sort_by") == "created" and sys.platform == "win32" else s.st_mtime
    return (t, p.name.lower())  # oldest first, name breaks ties

def sample_rate(f):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
         "stream=sample_rate", "-of", "csv=p=0", str(f)],
        capture_output=True, text=True).stdout.strip()
    return int(out) if out else None

def shift(f, out):
    sr = sample_rate(f)
    if sr is None:  # no audio track: just copy
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-c", "copy", str(out)], check=True)
        return
    af = f"asetrate={sr}*{ratio},aresample={sr},atempo={1/ratio:.6f}"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(f), "-c:v", "copy",
         "-af", af, "-c:a", "aac", "-b:a", "192k", str(out)], check=True)

queue = json.loads(qfile.read_text()) if qfile.exists() else []
known = {q["source"] for q in queue}
clips = sorted((p for p in src.iterdir() if p.suffix.lower() in {".mp4", ".mov", ".mkv", ".webm"}), key=age_key)

for p in clips:
    if ratio is None:  # clips already processed: queue the originals as-is
        out = p
    else:
        out = dst / (p.stem + ".mp4")
    if ratio is not None and not out.exists():
        print("processing", p.name)
        try:
            shift(p, out)
        except subprocess.CalledProcessError:
            print("FAILED", p.name, file=sys.stderr)
            out.unlink(missing_ok=True)
            continue
    if p.name not in known:
        queue.append({"source": p.name, "file": str(out.resolve()), "uploaded": False, "video_id": None})

for i, q in enumerate(queue, 1):
    q["n"] = i
qfile.write_text(json.dumps(queue, indent=2))
print(f"{len(queue)} clips in queue, {sum(not q['uploaded'] for q in queue)} pending")
