from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any


class Persistence:
    """Small SQLite metadata store; media remains on the filesystem."""
    def __init__(self, workspace: Path):
        self.path = workspace / "autoclip.db"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._init()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=WAL")
        return db

    def _init(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
            INSERT INTO schema_version(version) SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM schema_version);
            CREATE TABLE IF NOT EXISTS projects(
              id TEXT PRIMARY KEY, title TEXT NOT NULL, topic TEXT NOT NULL DEFAULT '',
              status TEXT NOT NULL, created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
              last_opened_at TEXT, keep_flag INTEGER NOT NULL DEFAULT 0,
              current_revision INTEGER NOT NULL DEFAULT 0, confirmed_revision INTEGER,
              trashed_at TEXT, state_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS chat_messages(
              id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              role TEXT NOT NULL, content TEXT NOT NULL, timestamp TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS scenes(
              project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              scene_id TEXT NOT NULL, position INTEGER NOT NULL, data_json TEXT NOT NULL,
              PRIMARY KEY(project_id, scene_id)
            );
            CREATE TABLE IF NOT EXISTS packages(
              id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              revision INTEGER NOT NULL, zip_path TEXT NOT NULL, validation_state TEXT NOT NULL,
              created_at TEXT NOT NULL, size_bytes INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS jobs(
              id TEXT PRIMARY KEY, project_id TEXT, package_id INTEGER, status TEXT NOT NULL,
              progress INTEGER NOT NULL, final_path TEXT, error_json TEXT, created_at TEXT NOT NULL, completed_at TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_projects_updated ON projects(updated_at DESC);
            CREATE INDEX IF NOT EXISTS idx_jobs_project ON jobs(project_id);
            CREATE TABLE IF NOT EXISTS youtube_connections(
              id TEXT PRIMARY KEY, channel_id TEXT NOT NULL, channel_title TEXT NOT NULL,
              channel_handle TEXT, refresh_token TEXT NOT NULL, is_default INTEGER NOT NULL DEFAULT 0,
              connected_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS youtube_publishes(
              id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
              connection_id TEXT NOT NULL REFERENCES youtube_connections(id), channel_id TEXT NOT NULL,
              channel_title TEXT NOT NULL, status TEXT NOT NULL, youtube_video_id TEXT,
              youtube_url TEXT, error_message TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_youtube_publish_project ON youtube_publishes(project_id);
            CREATE TABLE IF NOT EXISTS content_channels(
              id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            """)
            # Incremental, non-destructive migration for databases created by
            # the first MVP schema.
            cols = {r[1] for r in db.execute("PRAGMA table_info(jobs)")}
            if "metadata_json" not in cols: db.execute("ALTER TABLE jobs ADD COLUMN metadata_json TEXT")
            if "source_path" not in cols: db.execute("ALTER TABLE jobs ADD COLUMN source_path TEXT")
            if "interrupted" not in cols: db.execute("ALTER TABLE jobs ADD COLUMN interrupted INTEGER NOT NULL DEFAULT 0")
            if "render_engine" not in cols: db.execute("ALTER TABLE jobs ADD COLUMN render_engine TEXT NOT NULL DEFAULT 'ffmpeg_motion'")
            if "output_format" not in cols: db.execute("ALTER TABLE jobs ADD COLUMN output_format TEXT NOT NULL DEFAULT 'use_json'")
            project_cols = {r[1] for r in db.execute("PRAGMA table_info(projects)")}
            if "published_flag" not in project_cols: db.execute("ALTER TABLE projects ADD COLUMN published_flag INTEGER NOT NULL DEFAULT 0")
            if "published_at" not in project_cols: db.execute("ALTER TABLE projects ADD COLUMN published_at TEXT")
            if "project_type" not in project_cols:
                db.execute("ALTER TABLE projects ADD COLUMN project_type TEXT NOT NULL DEFAULT 'reel'")
                db.execute("UPDATE projects SET project_type='podcast' WHERE id LIKE 'podcast-%'")
            if "channel_id" not in project_cols:
                db.execute("ALTER TABLE projects ADD COLUMN channel_id TEXT NOT NULL DEFAULT 'undefined'")
            db.execute("UPDATE projects SET channel_id='undefined' WHERE channel_id IS NULL OR TRIM(channel_id)=''")
            now = datetime.now().astimezone().isoformat()
            db.execute(
                "INSERT OR IGNORE INTO content_channels(id,name,created_at,updated_at) VALUES('undefined','Undefined',?,?)",
                (now, now),
            )
            for channel_id, name in (
                ("mamase-reel", "Mamase Reel"),
                ("mamase-podcast", "Mamase Podcast"),
                ("khon-nuea-duang", "คนเหนือดวง"),
                ("thai-java-zone", "Thai Java Zone"),
            ):
                db.execute(
                    "INSERT OR IGNORE INTO content_channels(id,name,created_at,updated_at) VALUES(?,?,?,?)",
                    (channel_id, name, now, now),
                )

    def upsert_project(self, project: Any) -> None:
        payload = project.model_dump(mode="json")
        now = payload["updated_at"]
        with self._lock, self._connect() as db:
            channel_id = self.valid_channel_id(getattr(project, "channel_id", "undefined"))
            db.execute("""INSERT INTO projects(id,title,topic,status,created_at,updated_at,current_revision,confirmed_revision,trashed_at,state_json,channel_id)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,topic=excluded.topic,status=excluded.status,updated_at=excluded.updated_at,current_revision=excluded.current_revision,confirmed_revision=excluded.confirmed_revision,trashed_at=excluded.trashed_at,state_json=excluded.state_json""",
              (project.project_id, project.topic or "Mamase Project", project.topic, project.status.value, payload["created_at"], now, project.revision, project.confirmed_revision, None, json.dumps(payload, ensure_ascii=False), channel_id))
            db.execute("DELETE FROM chat_messages WHERE project_id=?", (project.project_id,))
            db.executemany("INSERT INTO chat_messages(project_id,role,content,timestamp) VALUES(?,?,?,?)", [(project.project_id,m.role,m.content,m.timestamp.isoformat()) for m in project.messages])
            db.execute("DELETE FROM scenes WHERE project_id=?", (project.project_id,))
            db.executemany("INSERT INTO scenes(project_id,scene_id,position,data_json) VALUES(?,?,?,?)", [(project.project_id,s.id,i,json.dumps(s.model_dump(mode="json"), ensure_ascii=False)) for i,s in enumerate(project.scenes)])

    def list_projects(self, include_trashed: bool = False) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT * FROM projects WHERE (? OR trashed_at IS NULL) ORDER BY updated_at DESC", (include_trashed,)).fetchall()
            result=[]
            for row in rows:
                item=dict(row); item.pop("state_json", None); item["keep"]=bool(item.pop("keep_flag")); result.append(item)
            return result

    def list_trashed(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT id,title,topic,status,created_at,updated_at,trashed_at,keep_flag FROM projects WHERE trashed_at IS NOT NULL ORDER BY trashed_at DESC").fetchall()
            return [{**dict(r), "keep": bool(r["keep_flag"])} for r in rows]

    def project_exists(self, project_id: str) -> bool:
        with self._connect() as db:
            return db.execute("SELECT 1 FROM projects WHERE id=?", (project_id,)).fetchone() is not None

    def mark_trash(self, project_id: str, trashed_at: str | None) -> None:
        with self._lock, self._connect() as db: db.execute("UPDATE projects SET trashed_at=?,status=? WHERE id=?", (trashed_at, "TRASHED" if trashed_at else "CHATTING", project_id))

    def delete_project(self, project_id: str) -> None:
        with self._lock, self._connect() as db: db.execute("DELETE FROM projects WHERE id=?", (project_id,))

    def project_job_paths(self, project_id: str) -> list[str]:
        with self._connect() as db:
            return [r[0] for r in db.execute("SELECT final_path FROM jobs WHERE project_id=? AND final_path IS NOT NULL", (project_id,)).fetchall()]

    def add_package(self, project_id: str, revision: int, path: Path, state: str) -> None:
        with self._lock, self._connect() as db: db.execute("INSERT INTO packages(project_id,revision,zip_path,validation_state,created_at,size_bytes) VALUES(?,?,?,?,?,?)", (project_id,revision,str(path),state,datetime.now().astimezone().isoformat(),path.stat().st_size if path.exists() else 0))

    def upsert_job(self, record: Any, final_path: Path | None = None, metadata: dict | None = None) -> None:
        with self._lock, self._connect() as db:
            db.execute("""INSERT INTO jobs(id,project_id,status,progress,final_path,error_json,created_at,completed_at,metadata_json,render_engine,output_format)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
              project_id=COALESCE(excluded.project_id,jobs.project_id), status=excluded.status,
              progress=excluded.progress, final_path=COALESCE(excluded.final_path,jobs.final_path),
              error_json=excluded.error_json, completed_at=COALESCE(excluded.completed_at,jobs.completed_at),
              metadata_json=COALESCE(excluded.metadata_json,jobs.metadata_json), render_engine=excluded.render_engine, output_format=excluded.output_format""",
              (record.job_id,record.project_id,record.status,record.progress,str(final_path) if final_path else None,json.dumps(record.error) if record.error else None,record.created_at.isoformat(),datetime.now().astimezone().isoformat() if record.status=="COMPLETED" else None,json.dumps(metadata,ensure_ascii=False) if metadata else (json.dumps(record.metadata,ensure_ascii=False) if getattr(record,"metadata",None) else None),getattr(record,"render_engine","ffmpeg_motion"),getattr(record,"output_format","use_json")))

    def get_job(self, job_id: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            if not row: return None
            result = dict(row)
            result["error"] = json.loads(result.pop("error_json")) if result.get("error_json") else None
            result["metadata"] = json.loads(result.pop("metadata_json")) if result.get("metadata_json") else None
            return result

    def update_job_metadata(self, job_id: str, metadata: dict) -> bool:
        with self._lock, self._connect() as db:
            cur = db.execute("UPDATE jobs SET metadata_json=? WHERE id=?", (json.dumps(metadata, ensure_ascii=False), job_id))
            return cur.rowcount > 0

    def mark_interrupted_jobs(self) -> int:
        with self._lock, self._connect() as db:
            cur = db.execute("UPDATE jobs SET status='FAILED',interrupted=1,error_json=? WHERE status IN ('RECEIVED','VALIDATING','GENERATING_AUDIO','RENDERING_SCENES','COMPOSING')", (json.dumps({"code":"JOB_INTERRUPTED","message":"งานหยุดลงเมื่อ server restart กรุณาสั่งสร้างใหม่"}, ensure_ascii=False),))
            return cur.rowcount

    def ensure_project(self, project_id: str, title: str, scene_count: int, status: str = "RENDERING", project_type: str = "reel", channel_id: str = "undefined") -> None:
        now = datetime.now().astimezone().isoformat()
        channel_id = self.valid_channel_id(channel_id)
        with self._lock, self._connect() as db:
            db.execute("""INSERT INTO projects(id,title,topic,status,created_at,updated_at,state_json,project_type,channel_id)
              VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title,status=excluded.status,updated_at=excluded.updated_at,project_type=excluded.project_type""", (project_id,title,title,status,now,now,json.dumps({"project_id":project_id,"topic":title,"status":status,"scenes":scene_count}),project_type,channel_id))

    def update_project_status(self, project_id: str, status: str) -> None:
        with self._lock, self._connect() as db:
            db.execute("UPDATE projects SET status=?,updated_at=? WHERE id=?", (status, datetime.now().astimezone().isoformat(), project_id))

    def set_keep(self, project_id: str, keep: bool) -> bool:
        with self._lock, self._connect() as db:
            cur=db.execute("UPDATE projects SET keep_flag=? WHERE id=?", (1 if keep else 0, project_id))
            if cur.rowcount == 0: raise KeyError(project_id)
        return keep

    def set_published(self, project_id: str, published: bool) -> dict:
        published_at = datetime.now().astimezone().isoformat() if published else None
        with self._lock, self._connect() as db:
            cur = db.execute(
                "UPDATE projects SET published_flag=?,published_at=? WHERE id=? AND trashed_at IS NULL",
                (1 if published else 0, published_at, project_id),
            )
            if cur.rowcount == 0:
                raise KeyError(project_id)
        return {"projectId": project_id, "published": published, "publishedAt": published_at}

    def get_published(self, project_id: str) -> bool:
        with self._connect() as db:
            row = db.execute("SELECT published_flag FROM projects WHERE id=?", (project_id,)).fetchone()
            return bool(row[0]) if row else False

    def channels(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT id,name,created_at,updated_at FROM content_channels ORDER BY CASE WHEN id='undefined' THEN 0 ELSE 1 END,name COLLATE NOCASE").fetchall()
            return [dict(row) for row in rows]

    def valid_channel_id(self, channel_id: str | None) -> str:
        value = (channel_id or "undefined").strip() or "undefined"
        with self._connect() as db:
            if db.execute("SELECT 1 FROM content_channels WHERE id=?", (value,)).fetchone() is None:
                raise KeyError(value)
        return value

    def create_channel(self, name: str) -> dict:
        clean = " ".join(name.split()).strip()
        if not clean:
            raise ValueError("empty channel name")
        channel_id = f"channel-{__import__('uuid').uuid4().hex[:12]}"
        now = datetime.now().astimezone().isoformat()
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO content_channels(id,name,created_at,updated_at) VALUES(?,?,?,?)", (channel_id, clean, now, now))
        return {"id": channel_id, "name": clean, "created_at": now, "updated_at": now}

    def rename_channel(self, channel_id: str, name: str) -> dict:
        if channel_id == "undefined":
            raise ValueError("Undefined cannot be renamed")
        clean = " ".join(name.split()).strip()
        if not clean:
            raise ValueError("empty channel name")
        now = datetime.now().astimezone().isoformat()
        with self._lock, self._connect() as db:
            cur = db.execute("UPDATE content_channels SET name=?,updated_at=? WHERE id=?", (clean, now, channel_id))
            if cur.rowcount == 0:
                raise KeyError(channel_id)
        return {"id": channel_id, "name": clean, "updated_at": now}

    def delete_unused_channel(self, channel_id: str) -> None:
        """Test/maintenance helper; never removes a channel referenced by content."""
        if channel_id in {"undefined", "mamase-reel", "mamase-podcast", "khon-nuea-duang", "thai-java-zone"}:
            raise ValueError("protected channel")
        with self._lock, self._connect() as db:
            if db.execute("SELECT 1 FROM projects WHERE channel_id=?", (channel_id,)).fetchone():
                raise ValueError("channel is in use")
            db.execute("DELETE FROM content_channels WHERE id=?", (channel_id,))

    def set_project_channel(self, project_id: str, channel_id: str) -> dict:
        channel_id = self.valid_channel_id(channel_id)
        with self._lock, self._connect() as db:
            cur = db.execute("UPDATE projects SET channel_id=?,updated_at=? WHERE id=? AND trashed_at IS NULL", (channel_id, datetime.now().astimezone().isoformat(), project_id))
            if cur.rowcount == 0:
                raise KeyError(project_id)
            channel = db.execute("SELECT name FROM content_channels WHERE id=?", (channel_id,)).fetchone()
        return {"projectId": project_id, "channelId": channel_id, "channelName": channel[0]}

    def get_project_channel(self, project_id: str) -> dict | None:
        with self._connect() as db:
            row = db.execute("SELECT p.channel_id,c.name FROM projects p LEFT JOIN content_channels c ON c.id=p.channel_id WHERE p.id=?", (project_id,)).fetchone()
            return {"channelId": row[0] or "undefined", "channelName": row[1] or "Undefined"} if row else None


    def history(self) -> list[dict]:
        with self._connect() as db:
            rows=db.execute("SELECT p.*, (SELECT COUNT(*) FROM scenes s WHERE s.project_id=p.id) scene_count FROM projects p WHERE p.trashed_at IS NULL ORDER BY p.updated_at DESC").fetchall()
            result = []
            for row in rows:
                item = dict(row)
                raw_state = item.pop("state_json", None)
                item["published"] = bool(item.pop("published_flag", 0))
                channel = db.execute("SELECT name FROM content_channels WHERE id=?", (item.get("channel_id") or "undefined",)).fetchone()
                item["channelId"] = item.pop("channel_id", None) or "undefined"
                item["channelName"] = channel[0] if channel else "Undefined"
                state = json.loads(raw_state) if raw_state else {}
                item["scene_count"] = item.get("scene_count") or (len(state.get("scenes", [])) if isinstance(state.get("scenes"), list) else int(state.get("scenes", 0) or 0))
                latest = db.execute("SELECT * FROM jobs WHERE project_id=? ORDER BY created_at DESC LIMIT 1", (item["id"],)).fetchone()
                if latest:
                    j=dict(latest); video=bool(j.get("final_path") and Path(j["final_path"]).is_file())
                    metadata = json.loads(j.get("metadata_json") or "{}")
                    english_audio = metadata.get("englishAudio") if isinstance(metadata, dict) else {}
                    english_path = self.path.parent / j["id"] / "output" / "podcast-en.wav"
                    english_available = bool(
                        isinstance(english_audio, dict)
                        and english_audio.get("available")
                        and english_path.is_file()
                    )
                    item["latestJob"]={"id":j["id"],"status":j["status"],"progress":j["progress"],"videoAvailable":video,"videoUrl":f"/api/jobs/{j['id']}/video" if video else None,"previewUrl":f"/jobs/{j['id']}/preview" if video else None,"englishAudioAvailable":english_available,"englishAudioUrl":f"/api/jobs/{j['id']}/english-audio" if english_available else None,"englishAudioStatus":english_audio.get("status") if isinstance(english_audio, dict) else None,"createdAt":j["created_at"],"completedAt":j.get("completed_at"),"metadata":metadata}
                    if j["status"] == "COMPLETED": item["status"] = "COMPLETED"
                else: item["latestJob"] = None
                result.append(item)
            return result

    def youtube_connections(self) -> list[dict]:
        with self._connect() as db:
            rows = db.execute("SELECT id,channel_id,channel_title,channel_handle,is_default,connected_at,updated_at FROM youtube_connections ORDER BY is_default DESC, channel_title").fetchall()
            return [dict(r) for r in rows]

    def save_youtube_connection(self, item: dict) -> None:
        with self._lock, self._connect() as db:
            db.execute("INSERT INTO youtube_connections(id,channel_id,channel_title,channel_handle,refresh_token,is_default,connected_at,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET channel_id=excluded.channel_id,channel_title=excluded.channel_title,channel_handle=excluded.channel_handle,refresh_token=COALESCE(NULLIF(excluded.refresh_token,''),youtube_connections.refresh_token),is_default=excluded.is_default,updated_at=excluded.updated_at", tuple(item[k] for k in ('id','channel_id','channel_title','channel_handle','refresh_token','is_default','connected_at','updated_at')))

    def get_youtube_connection(self, connection_id: str) -> dict | None:
        with self._connect() as db:
            row=db.execute("SELECT * FROM youtube_connections WHERE id=?",(connection_id,)).fetchone(); return dict(row) if row else None

    def delete_youtube_connection(self, connection_id: str) -> bool:
        with self._lock, self._connect() as db:
            cur=db.execute("DELETE FROM youtube_connections WHERE id=?",(connection_id,)); return cur.rowcount > 0
