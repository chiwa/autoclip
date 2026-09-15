from types import SimpleNamespace

import pytest

from app.services.persistence import Persistence


def project(project_id: str):
    now = "2026-09-11T12:00:00+07:00"
    return SimpleNamespace(
        project_id=project_id,
        topic="Test project",
        status=SimpleNamespace(value="CHATTING"),
        revision=0,
        confirmed_revision=None,
        messages=[],
        scenes=[],
        model_dump=lambda mode: {
            "project_id": project_id,
            "topic": "Test project",
            "status": "CHATTING",
            "revision": 0,
            "confirmed_revision": None,
            "created_at": now,
            "updated_at": now,
            "messages": [],
            "scenes": [],
        },
    )


def test_publish_status_defaults_false_and_can_toggle(tmp_path):
    persistence = Persistence(tmp_path)
    persistence.upsert_project(project("project-1"))
    assert persistence.history()[0]["published"] is False

    marked = persistence.set_published("project-1", True)
    assert marked["published"] is True
    assert marked["publishedAt"]
    assert persistence.history()[0]["published"] is True

    cleared = persistence.set_published("project-1", False)
    assert cleared == {"projectId": "project-1", "published": False, "publishedAt": None}
    assert persistence.history()[0]["published"] is False


def test_publish_status_rejects_unknown_project(tmp_path):
    with pytest.raises(KeyError):
        Persistence(tmp_path).set_published("missing", True)


def test_project_type_is_stored_and_old_podcast_ids_are_migrated(tmp_path):
    persistence = Persistence(tmp_path)
    persistence.ensure_project("podcast-new", "Podcast", 1, project_type="podcast")
    persistence.ensure_project("reel-new", "Reel", 9)
    types = {item["id"]: item["project_type"] for item in persistence.history()}
    assert types == {"podcast-new": "podcast", "reel-new": "reel"}


def test_channels_seed_old_content_as_undefined_and_can_be_managed(tmp_path):
    persistence = Persistence(tmp_path)
    names = {item["name"] for item in persistence.channels()}
    assert {"Undefined", "Mamase Reel", "Mamase Podcast", "คนเหนือดวง", "Thai Java Zone"} <= names

    persistence.ensure_project("old-content", "Old", 1)
    old = next(item for item in persistence.history() if item["id"] == "old-content")
    assert old["channelId"] == "undefined"
    assert old["channelName"] == "Undefined"

    channel = persistence.create_channel("New Channel")
    persistence.set_project_channel("old-content", channel["id"])
    renamed = persistence.rename_channel(channel["id"], "Renamed Channel")
    assert renamed["name"] == "Renamed Channel"
    updated = next(item for item in persistence.history() if item["id"] == "old-content")
    assert updated["channelName"] == "Renamed Channel"


def test_undefined_channel_cannot_be_renamed(tmp_path):
    with pytest.raises(ValueError):
        Persistence(tmp_path).rename_channel("undefined", "Something Else")
