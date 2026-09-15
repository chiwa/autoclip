from __future__ import annotations

import pytest

from app.config.settings import AppSettings, Settings, load_settings
from app.domain.ai_models import AiProjectStatus, AiScene
from app.domain.errors import AppError
from app.services.ai_service import AiProjectService
from app.services.reel_hook_validator import MamaseReelHookGate


def scene(scene_id: str, narration: str, *, tts_text: str | None = None, image_prompt: str | None = None) -> AiScene:
    return AiScene(
        id=scene_id,
        narration=narration,
        tts_text=tts_text,
        image_prompt=image_prompt or "A specific cinematic scientific scene showing the exact physical mystery from the narration",
    )


def test_hook_gate_accepts_a_direct_truthful_curiosity_opening():
    result = MamaseReelHookGate().evaluate([
        scene("scene-01", "เรารู้ได้ยังไงว่าไม่มีอะไรเร็วกว่าแสง? คำตอบอยู่ในกฎของอวกาศและเวลา"),
        scene("scene-02", "ยิ่งวัตถุมีมวลเข้าใกล้ความเร็วแสง มันยิ่งต้องใช้พลังงานมากขึ้น"),
        scene("scene-03", "ดังนั้นความเร็วแสงจึงเป็นขีดจำกัดของข้อมูลตามฟิสิกส์ที่เราทดสอบได้"),
    ])

    assert result.passed is True
    assert len(result.checks) == 10


def test_hook_gate_flags_greeting_and_missing_curiosity_gap():
    result = MamaseReelHookGate().evaluate([
        scene("scene-01", "สวัสดีครับ วันนี้เราจะมาพูดถึงความเร็วแสง"),
        scene("scene-02", "ความเร็วแสงเป็นหัวข้อหนึ่งในวิชาฟิสิกส์"),
    ])

    assert result.passed is False
    failed = {check.number for check in result.checks if not check.passed}
    assert {2, 4, 10} <= failed


def test_hook_gate_flags_generic_first_visual_and_unsupported_certainty():
    result = MamaseReelHookGate().evaluate([
        scene("scene-01", "เราพบเอเลียนแล้ว", image_prompt="generic stars"),
        scene("scene-02", "หลักฐานนี้เปลี่ยนทุกอย่าง"),
    ])

    failed = {check.number for check in result.checks if not check.passed}
    assert 5 in failed
    assert 6 in failed


def test_image_generation_is_blocked_until_hook_gate_passes(tmp_path):
    service = AiProjectService(Settings(app=AppSettings(workspace=tmp_path / "workspaces")))
    project = service.create("ความเร็วแสง")
    project.scenes = [scene("scene-01", "สวัสดีครับ วันนี้เราจะมาพูดถึงความเร็วแสง")]
    project.status = AiProjectStatus.SCRIPT_READY
    service._save(project)

    with pytest.raises(AppError) as error:
        service.start_image_generation(project.project_id)

    assert error.value.code == "REEL_HOOK_GATE_FAILED"
    assert error.value.details["issues"]
    assert service.get(project.project_id).hook_gate["passed"] is False


def test_editing_scene_refreshes_persisted_hook_gate(tmp_path):
    service = AiProjectService(Settings(app=AppSettings(workspace=tmp_path / "workspaces")))
    project = service.create("ความเร็วแสง")
    project.scenes = [scene("scene-01", "สวัสดีครับ วันนี้เราจะมาพูดถึงความเร็วแสง")]
    project.status = AiProjectStatus.SCRIPT_READY
    service._save(project)

    updated = service.update_scene(project.project_id, "scene-01", {
        "narration": "เรารู้ได้ยังไงว่าไม่มีอะไรเร็วกว่าแสง?",
        "tts_text": "เรารู้ได้ยังไงว่าไม่มีอะไรเร็วกว่าแสง?",
        "image_prompt": "A spacecraft racing beside a brilliant photon boundary in curved spacetime, cinematic and specific",
    })

    assert updated.hook_gate["passed"] is True


def test_hook_gate_reads_environment_configuration(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "AUTOCLIP_REEL_HOOK_GATE_ENABLED=false\nAUTOCLIP_REEL_HOOK_MAX_CHARACTERS=80\n",
        encoding="utf-8",
    )

    settings = load_settings(tmp_path / "config.yaml")

    assert settings.reel_hook_gate.enabled is False
    assert settings.reel_hook_gate.max_hook_characters == 80


def test_hook_gate_flags_generic_cta_and_prohibited_openings():
    # Test prohibited opening "รู้หรือไม่"
    result_opening = MamaseReelHookGate().evaluate([
        scene("scene-01", "รู้หรือไม่ว่าดาวอังคารเคยมีแม่น้ำ? แล้วน้ำหายไปไหน"),
        scene("scene-02", "หลักฐานบ่งชี้ว่าลมสุริยะพัดพามันไป"),
    ])
    assert result_opening.passed is False
    failed_opening = {c.number for c in result_opening.checks if not c.passed}
    assert 2 in failed_opening

    # Test generic CTA rejection
    result_generic_cta = MamaseReelHookGate().evaluate([
        scene("scene-01", "ดาวอังคารเคยมีแม่น้ำ แล้วน้ำทั้งหมดหายไปไหน?"),
        scene("scene-02", "ชั้นบรรยากาศที่เบาบางทำให้โมเลกุลน้ำหลุดสู่อวกาศ"),
        scene("scene-03", "อย่าลืมกดติดตาม และคอมเมนต์คุยกันนะครับ"),
    ])
    assert result_generic_cta.passed is False
    failed_cta = {c.number for c in result_generic_cta.checks if not c.passed}
    assert 9 in failed_cta

    # Test topic-specific discussion CTA passes
    result_topic_cta = MamaseReelHookGate().evaluate([
        scene("scene-01", "ดาวอังคารเคยมีแม่น้ำ แล้วน้ำทั้งหมดหายไปไหน?"),
        scene("scene-02", "ชั้นบรรยากาศที่เบาบางทำให้โมเลกุลน้ำหลุดสู่อวกาศ"),
        scene("scene-03", "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?"),
    ])
    assert result_topic_cta.passed is True

