import pytest

from app.domain.errors import AppError
from app.services.zodiac_narration_guard import ZodiacNarrationGuard


class Scene:
    narration = "ราศีมังกร สัปดาห์นี้ควรเลือกจังหวะให้ดีครับ"
    tts_text = narration


class Pronunciation:
    def normalize(self, text):
        return text.replace("TTS", "ทีทีเอส")


def test_provider_receives_exactly_final_narration_without_defaults():
    text = ZodiacNarrationGuard.provider_text(Scene(), Pronunciation())
    assert text == Scene.narration
    assert "สวัสดี" not in text
    assert "กดไลก์" not in text
    assert "คนเหนือดวง" not in text


def test_pronunciation_replacement_is_the_only_allowed_transformation():
    scene = Scene()
    scene.narration = "ทดลอง TTS สัปดาห์นี้"
    scene.tts_text = scene.narration
    assert ZodiacNarrationGuard.provider_text(scene, Pronunciation()) == "ทดลอง ทีทีเอส สัปดาห์นี้"


@pytest.mark.parametrize("extra", [
    "สวัสดีครับ ",
    "",  # covered separately below with a suffix
])
def test_intro_or_outro_added_before_provider_is_rejected(extra):
    final = Scene.narration
    sent = extra + final if extra else final + " ฝากกดติดตามด้วยครับ"
    with pytest.raises(AppError) as error:
        ZodiacNarrationGuard.verify_provider_text(final, sent, Pronunciation())
    assert error.value.code == "ZODIAC_NARRATION_MISMATCH"


def test_whitespace_normalization_does_not_create_false_failure():
    ZodiacNarrationGuard.verify_provider_text("ราศีมีน\n  สัปดาห์นี้", "ราศีมีน สัปดาห์นี้", Pronunciation())


@pytest.mark.parametrize("fragment", [
    "Read aloud", "slightly mysterious", "reassuring", "trusted person",
    "weekly insight", "news anchor", "advertisement", "Speed:", "Language:",
])
def test_known_style_fragments_can_never_reach_final_narration(fragment):
    scene = Scene()
    scene.narration = f"ราศีมังกร {fragment} เนื้อหาประจำสัปดาห์"
    scene.tts_text = scene.narration
    with pytest.raises(AppError) as error:
        ZodiacNarrationGuard.provider_text(scene, Pronunciation())
    assert error.value.code == "ZODIAC_TTS_STYLE_LEAK"


def test_style_and_final_narration_remain_separate_values():
    style = "Read aloud like a trusted person"
    final = Scene.narration
    sent = ZodiacNarrationGuard.provider_text(Scene(), Pronunciation())
    assert sent == final
    assert style not in sent
