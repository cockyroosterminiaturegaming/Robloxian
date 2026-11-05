#!/usr/bin/env python3
"""Upload the next pending clip to YouTube. Run this every 8 hours.

First run opens a browser for Google login (use `python upload_next.py --auth`
on your own machine). Needs client_secret.json from Google Cloud Console.
"""
import json, sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
cfg = json.loads(Path("config.json").read_text())
qfile = Path(cfg["queue_file"])

def creds():
    tok = Path("token.json")
    c = Credentials.from_authorized_user_file(tok, SCOPES) if tok.exists() else None
    if c and c.valid:
        return c
    if c and c.expired and c.refresh_token:
        c.refresh(Request())
    else:
        c = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES).run_local_server(port=0)
    tok.write_text(c.to_json())
    return c

def main():
    c = creds()
    if "--auth" in sys.argv:
        print("Authorized; token.json saved.")
        return
    queue = json.loads(qfile.read_text())
    item = next((q for q in queue if not q["uploaded"]), None)
    if not item:
        print("Queue empty - all clips uploaded.")
        return
    yt = build("youtube", "v3", credentials=c)
    body = {
        "snippet": {
            "title": cfg["title_template"].format(n=item["n"])[:100],
            "description": cfg["description"],
            "tags": cfg["tags"],
            "categoryId": cfg["category_id"],
        },
        "status": {"privacyStatus": cfg["privacy"], "selfDeclaredMadeForKids": cfg["made_for_kids"]},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(item["file"], resumable=True, chunksize=-1))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    item["uploaded"], item["video_id"] = True, resp["id"]
    qfile.write_text(json.dumps(queue, indent=2))
    print(f"Uploaded #{item['n']} {item['source']} -> https://youtu.be/{resp['id']}")

main()
