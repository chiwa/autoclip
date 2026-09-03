from __future__ import annotations
import secrets, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
import requests
from app.domain.errors import AppError

class YouTubeService:
    AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN = "https://oauth2.googleapis.com/token"
    def __init__(self, settings, persistence): self.settings, self.persistence, self._states = settings, persistence, set()
    def configured(self): return bool(self.settings.youtube.oauth.client_id and self.settings.youtube.oauth.client_secret)
    def auth_url(self):
        if not self.configured(): raise AppError("YOUTUBE_NOT_CONFIGURED", "ยังไม่ได้ตั้งค่า YouTube OAuth")
        state=secrets.token_urlsafe(24); self._states.add(state)
        q={"client_id":self.settings.youtube.oauth.client_id,"redirect_uri":self.settings.youtube.oauth.redirect_uri,"response_type":"code","scope":self.settings.youtube.oauth.scope,"access_type":"offline","prompt":"consent","state":state}
        return self.AUTH+"?"+urlencode(q)
    def callback(self, code, state):
        if state not in self._states: raise AppError("YOUTUBE_OAUTH_STATE_INVALID", "OAuth state ไม่ถูกต้อง")
        self._states.discard(state)
        r=requests.post(self.TOKEN,data={"code":code,"client_id":self.settings.youtube.oauth.client_id,"client_secret":self.settings.youtube.oauth.client_secret,"redirect_uri":self.settings.youtube.oauth.redirect_uri,"grant_type":"authorization_code"},timeout=20)
        if r.status_code >= 400: raise AppError("YOUTUBE_OAUTH_FAILED", "ไม่สามารถเชื่อมต่อ YouTube ได้")
        token=r.json(); access=token.get("access_token"); refresh=token.get("refresh_token")
        if not access: raise AppError("YOUTUBE_OAUTH_FAILED", "ไม่ได้รับสิทธิ์ YouTube")
        items=[]; page=None
        while True:
            params={"part":"snippet","mine":"true","maxResults":50}
            if page: params["pageToken"]=page
            response=requests.get("https://www.googleapis.com/youtube/v3/channels",params=params,headers={"Authorization":f"Bearer {access}"},timeout=20)
            if response.status_code >= 400: raise AppError("YOUTUBE_CHANNEL_NOT_FOUND", "ไม่สามารถอ่านรายการช่อง YouTube ได้")
            info=response.json(); items.extend(info.get("items") or []); page=info.get("nextPageToken")
            if not page: break
        if not items: raise AppError("YOUTUBE_CHANNEL_NOT_FOUND", "ไม่พบช่อง YouTube")
        existing_connections=self.persistence.youtube_connections(); now=datetime.now(timezone.utc).astimezone().isoformat()
        for item in items:
            cid=item["id"]; existing=next((x for x in existing_connections if x["channel_id"]==cid),None)
            self.persistence.save_youtube_connection({"id":existing["id"] if existing else str(uuid.uuid4()),"channel_id":cid,"channel_title":item.get("snippet",{}).get("title",cid),"channel_handle":None,"refresh_token":refresh or (existing["refresh_token"] if existing else ""),"is_default":1 if not existing_connections and not existing else 0,"connected_at":existing["connected_at"] if existing else now,"updated_at":now})
    def upload(self, connection_id, video: Path, title, description, tags, privacy):
        c=self.persistence.get_youtube_connection(connection_id)
        if not c: raise AppError("YOUTUBE_CONNECTION_NOT_FOUND", "ไม่พบช่อง YouTube ที่เลือก")
        if not video.is_file(): raise AppError("VIDEO_NOT_READY", "ไม่พบไฟล์วิดีโอ")
        if privacy not in {"private","unlisted","public"}: raise AppError("INVALID_METADATA", "Visibility ไม่ถูกต้อง")
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.auth.transport.requests import Request
            cred=Credentials(None,refresh_token=c["refresh_token"],token_uri=self.TOKEN,client_id=self.settings.youtube.oauth.client_id,client_secret=self.settings.youtube.oauth.client_secret,scopes=[self.settings.youtube.oauth.scope])
            cred.refresh(Request()); yt=build("youtube","v3",credentials=cred,cache_discovery=False)
            req=yt.videos().insert(part="snippet,status",body={"snippet":{"title":title,"description":description,"tags":tags},"status":{"privacyStatus":privacy}},media_body=MediaFileUpload(str(video),mimetype="video/mp4",resumable=True))
            result=None
            while result is None: _,result=req.next_chunk()
            vid=result["id"]; return {"videoId":vid,"url":f"https://www.youtube.com/watch?v={vid}","channelTitle":c["channel_title"]}
        except AppError: raise
        except Exception as exc: raise AppError("YOUTUBE_UPLOAD_FAILED", "อัปโหลด YouTube ไม่สำเร็จ") from exc
