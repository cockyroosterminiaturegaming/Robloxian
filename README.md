# Robloxian auto-uploader

Pitch-shifts (-15%) local vertical clips and uploads one to YouTube Shorts every 4 hours.
Run this on **your own computer** (the clips are local).

## One-time setup
1. Install Python 3, ffmpeg, then `pip install -r requirements.txt`.
2. Google Cloud Console: create a project, enable **YouTube Data API v3**, create an
   **OAuth client ID (Desktop app)**, download it as `client_secret.json` into this folder.
   Add your Google account as a test user on the OAuth consent screen.
3. Put clips in `clips/` (set `clips_dir` in config.json; currently `C:\Roblox Boss`).
   Clips upload oldest to newest by date modified (`"sort_by": "created"` in config.json uses creation date on Windows).
4. `python prepare.py`   - builds `queue.json` (set `pitch_ratio` to 0.85 to also pitch-shift; null = clips already processed).
   Listen to a few in `processed/` before continuing.
5. `python upload_next.py --auth`   - log in once; saves `token.json`.
6. `python upload_next.py`   - test a single upload (use `"privacy": "private"` in config.json first).

## Schedule (every 4 hours)
- Linux/Mac: `crontab -e` -> `0 */4 * * * cd /path/to/Robloxian && python3 upload_next.py >> upload.log 2>&1`
- Windows: Task Scheduler -> repeat every 4 hours -> `python upload_next.py` (Start in: this folder).
The computer must be on at those times. Missed runs are not made up.

## Notes
- New/unaudited API projects force uploads to **private** until you pass YouTube's API audit.
- Edit title/description/tags in `config.json`. `{n}` in the title is the queue number.
- Quota: ~1,600 units/upload vs 10,000/day default - 3/day is fine.
- 600 clips at 6/day = ~100 days. 6 uploads x 1,600 = 9,600 of the 10,000 daily quota, so little headroom.
