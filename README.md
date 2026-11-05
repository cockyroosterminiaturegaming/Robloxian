# Robloxian auto-uploader

Pitch-shifts (-15%) local vertical clips and uploads one to YouTube Shorts every 8 hours.
Run this on **your own computer** (the clips are local).

## One-time setup
1. Install Python 3, ffmpeg, then `pip install -r requirements.txt`.
2. Google Cloud Console: create a project, enable **YouTube Data API v3**, create an
   **OAuth client ID (Desktop app)**, download it as `client_secret.json` into this folder.
   Add your Google account as a test user on the OAuth consent screen.
3. Put clips in `clips/` (names sort naturally: clip1, clip2, clip10...).
   Rename them first if you want a specific upload order.
4. `python prepare.py`   - pitch-shifts all clips into `processed/` and builds `queue.json`.
   Listen to a few in `processed/` before continuing.
5. `python upload_next.py --auth`   - log in once; saves `token.json`.
6. `python upload_next.py`   - test a single upload (use `"privacy": "private"` in config.json first).

## Schedule (every 8 hours)
- Linux/Mac: `crontab -e` -> `0 */8 * * * cd /path/to/Robloxian && python3 upload_next.py >> upload.log 2>&1`
- Windows: Task Scheduler -> repeat every 8 hours -> `python upload_next.py` (Start in: this folder).
The computer must be on at those times. Missed runs are not made up.

## Notes
- New/unaudited API projects force uploads to **private** until you pass YouTube's API audit.
- Edit title/description/tags in `config.json`. `{n}` in the title is the queue number.
- Quota: ~1,600 units/upload vs 10,000/day default - 3/day is fine.
- 600 clips at 3/day = ~200 days.
