from datetime import date
import pytest

from app.domain.errors import AppError
from app.services.zodiac_curator import ZodiacCurator
from app.services.zodiac_service import ZODIACS


def sample_readings():
    readings = []
    for z in ZODIACS:
        readings.append({
            "id": z.id,
            "hook": f"ราศี{z.name_th} สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ",
            "overview": "ภาพรวมสัปดาห์นี้มีแนวโน้มได้ทบทวนเป้าหมาย",
            "work": "งานมีความก้าวหน้าจากการสื่อสารที่ชัดเจน",
            "finance": "การเงินควรเน้นการวางแผนล่วงหน้า",
            "love": "ความสัมพันธ์ต้องการความเข้าใจและเวลาให้กัน",
            "advice": "รักษาความสงบและรอบคอบในการตัดสินใจ",
            "closing": "ขอให้เป็นสัปดาห์ที่ดี เจอกันใหม่สัปดาห์หน้าครับ",
        })
    return readings


def test_curate_batch_success():
    payload = {"zodiacs": sample_readings()}
    start = date(2026, 9, 14)
    end = date(2026, 9, 20)

    curated = ZodiacCurator.curate_batch(payload, start, end)

    assert len(curated["zodiacs"]) == 12
    assert curated["week"]["display_th"] == "14 - 20 ก.ย. 2569"
    assert curated["zodiacs"][0]["id"] == "capricorn"
    assert curated["zodiacs"][0]["hook"].startswith("ราศีมังกร")


def test_reject_cjk_characters():
    readings = sample_readings()
    readings[0]["overview"] = "ภาพรวมสัปดาห์นี้มีแนวโน้มที่ดี 摩羯座"
    payload = {"zodiacs": readings}

    with pytest.raises(AppError) as exc:
        ZodiacCurator.curate_batch(payload, date(2026, 9, 14), date(2026, 9, 20))
    assert exc.value.code == "ZODIAC_INVALID_CHARACTERS"


def test_reject_wrong_count():
    readings = sample_readings()[:11]
    payload = {"zodiacs": readings}

    with pytest.raises(AppError) as exc:
        ZodiacCurator.curate_batch(payload, date(2026, 9, 14), date(2026, 9, 20))
    assert exc.value.code == "ZODIAC_COUNT_INVALID"


def test_hook_normalization_and_weak_hook_rewriting():
    # 1. Hook missing exact prefix
    hook1 = ZodiacCurator.curate_hook("scorpio", "พิจิก", "สำหรับชาวพิจิก สัปดาห์นี้อย่าเพิ่งไว้ใจคำสัญญาหวานหูครับ", "")
    assert hook1.startswith("ราศีพิจิก ")
    assert "อย่าเพิ่งไว้ใจ" in hook1

    # 2. Weak hook rewritten
    hook2 = ZodiacCurator.curate_hook("leo", "สิงห์", "สวัสดีครับราศีสิงห์", "")
    assert hook2.startswith("ราศีสิงห์ ")
    assert len(hook2) > 30


def test_decant_technical_astrology_and_remove_repetitive_stars():
    reading = {
        "id": "scorpio",
        "hook": "ราศีพิจิก สัปดาห์นี้เสน่ห์ของคุณกลับมา แต่ระวังการใช้จ่ายตามใจตัวเองครับ",
        "overview": "ดาวศุกร์สถิตในราศีของคุณ ทำให้ภาพรวมโดดเด่น",
        "work": "ดาวอังคารในเรือนอาชีพทำให้คุณมีพลังผลักดันงานอย่างชัดเจน",
        "finance": "ดาวศุกร์ในเรือนการเงินทำมุมจตุโกณกับดาวพลูโต ระวังการใช้จ่ายเพื่อความบันเทิง",
        "love": "ดาวพลูโตถอยหลังในเรือนคู่สัมพันธ์ ชวนให้ทบทวนความต้องการจริงใจ",
        "advice": "ดาวพุธในเรือนจิตใต้สำนึกบอกให้พักผ่อน",
        "closing": "เจอกันใหม่สัปดาห์หน้า",
    }

    ZodiacCurator.decant_technical_astrology(reading)
    ZodiacCurator.fix_repetitive_star_openings(reading)

    # Check that sections do NOT repeatedly start with "ดาว..."
    assert not reading["work"].startswith("ดาว")
    assert not reading["finance"].startswith("ดาว")
    assert not reading["love"].startswith("ดาว")
    assert reading["work"].startswith("ด้านการงาน")
    assert reading["finance"].startswith("ด้านการเงิน")
    assert reading["love"].startswith("ด้านความรัก")


def test_exact_duplicate_hooks_detected_and_resolved():
    readings = sample_readings()
    # Give capricorn and aquarius the exact same hook body
    readings[0]["hook"] = "ราศีมังกร สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ"
    readings[1]["hook"] = "ราศีกุมภ์ สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ"
    # Give others distinct hooks so they don't collide
    for i in range(2, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    zodiacs = curated["zodiacs"]

    # Capricorn (first) preserved
    assert zodiacs[0]["hook"] == "ราศีมังกร สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ"
    # Aquarius (duplicate) rewritten
    assert zodiacs[1]["hook"] != "ราศีกุมภ์ สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ"
    assert zodiacs[1]["hook"].startswith("ราศีกุมภ์")

    rewritten_ids = [item["id"] for item in curated["curator"]["rewritten_hooks"]]
    assert "aquarius" in rewritten_ids
    assert "capricorn" not in rewritten_ids


def test_high_structural_similarity_detected_and_rewritten():
    readings = sample_readings()
    # Capricorn and Aquarius hooks share ~88% text
    readings[0]["hook"] = "ราศีมังกร สัปดาห์นี้มีโอกาสทางการเงินเข้ามา แต่ต้องระวังอย่าให้ความเกรงใจทำให้เสียเปรียบ"
    readings[1]["hook"] = "ราศีกุมภ์ สัปดาห์นี้มีโอกาสทางการงานเข้ามา แต่ต้องระวังอย่าให้ความใจดีทำให้เสียเปรียบ"
    for i in range(2, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    zodiacs = curated["zodiacs"]

    assert zodiacs[0]["hook"] == readings[0]["hook"]
    # Aquarius was too similar to capricorn, so rewritten
    assert zodiacs[1]["hook"] != readings[1]["hook"]
    report = curated["curator"]
    similar_entry = next(item for item in report["rewritten_hooks"] if item["id"] == "aquarius")
    assert "similarity" in similar_entry["reason"]


def test_dissimilar_strong_hooks_preserved_without_change():
    readings = sample_readings()
    # 12 diverse, strong hooks with different openings and tensions
    unique_hooks = [
        "ราศีมังกร สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ เพราะคำตอบอาจมาช้ากว่าที่คิด",
        "ราศีกุมภ์ สัปดาห์นี้ความคิดแปลกใหม่อาจสร้างโอกาสใหญ่ แต่ต้องเลือกคนที่ไว้ใจได้ร่วมทาง",
        "ราศีมีน สัปดาห์นี้สัญชาตญาณคุณแม่นยำมาก แต่เรื่องเงินต้องดูหลักฐานจริงเป็นหลัก",
        "ราศีเมษ สัปดาห์นี้ยิ่งใจร้อนยิ่งสะดุด ชะลอจังหวะลงนิดเดียวจะเห็นทางออกที่ง่ายกว่าเดิม",
        "ราศีพฤษภ สัปดาห์นี้มีโอกาสทางการเงินเข้ามา แต่ต้องระวังอย่าให้ความเกรงใจทำให้เสียเปรียบ",
        "ราศีเมถุน สัปดาห์นี้คำพูดของคุณมีพลังสูงมาก เลือกสื่อสารให้ถูกจังหวะแล้วทุกอย่างจะราบรื่น",
        "ราศีกรกฎ สัปดาห์นี้มีพลังผลักดันเรื่องงานเต็มที่ แต่สิ่งสำคัญคืออย่าแบกปัญหาของคนอื่นไว้คนเดียว",
        "ราศีสิงห์ สัปดาห์นี้ผลงานเด่นชัดเป็นที่ยอมรับ แต่ต้องรักษาความสัมพันธ์กับคนรอบข้างให้เหนียวแน่น",
        "ราศีกันย์ สัปดาห์นี้ทุกอย่างอยู่ในสายตาคุณ รายละเอียดเล็กๆ ที่คุณเห็นจะพาไปสู่ความสำเร็จ",
        "ราศีตุลย์ สัปดาห์นี้อย่าลังเลนานเกินไป การตัดสินใจที่ชัดเจนจะปลดล็อกเรื่องที่ค้างคามานาน",
        "ราศีพิจิก สัปดาห์นี้เสน่ห์และความเฉียบคมของคุณกลับมา ใช้ขับเคลื่อนเป้าหมายแล้วจะเห็นผลลัพธ์ชัดเจน",
        "ราศีธนู สัปดาห์นี้โอกาสใหม่กำลังเปิดออก แต่ต้องวางแผนภาระให้รัดกุมก่อนก้าวไปข้างหน้า",
    ]
    for i in range(12):
        readings[i]["hook"] = unique_hooks[i]

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))

    # All 12 hooks preserved completely without modification
    for i in range(12):
        assert curated["zodiacs"][i]["hook"] == unique_hooks[i]

    assert curated["curator"]["rewritten_hooks_count"] == 0
    assert curated["curator"]["status"] == "passed"


def test_shared_opening_pattern_capped_at_max():
    readings = sample_readings()
    # 3 signs starting with "มีโอกาส"
    readings[0]["hook"] = "ราศีมังกร สัปดาห์นี้มีโอกาสใหม่ในการขยายงาน แต่ต้องคุมค่าใช้จ่ายให้ดี"
    readings[1]["hook"] = "ราศีกุมภ์ สัปดาห์นี้มีโอกาสได้เดินทางไกล แต่ต้องตรวจเอกสารให้รอบคอบ"
    readings[2]["hook"] = "ราศีมีน สัปดาห์นี้มีโอกาสได้เซ็นสัญญาสำคัญ แต่ต้องเช็กข้อผูกมัดก่อน"
    for i in range(3, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))

    # First 2 allowed under MAX_SHARED_OPENING_PATTERN = 2
    assert curated["zodiacs"][0]["hook"] == readings[0]["hook"]
    assert curated["zodiacs"][1]["hook"] == readings[1]["hook"]
    # 3rd sign exceeded pattern cap -> rewritten
    assert curated["zodiacs"][2]["hook"] != readings[2]["hook"]
    pisces_entry = next(item for item in curated["curator"]["rewritten_hooks"] if item["id"] == "pisces")
    assert "shared_opening_pattern" in pisces_entry["reason"]


def test_hook_rewrite_derived_from_reading_content():
    reading = {
        "id": "cancer",
        "hook": "สั้น",  # weak hook
        "overview": "ภาพรวมสัปดาห์นี้",
        "work": "ด้านการงาน สัปดาห์นี้มีโปรเจกต์ท้าทายเข้ามา แต่ต้องระวังความขัดแย้งกับผู้ร่วมงานครับ",
        "finance": "การเงินราบรื่น",
        "love": "ความรักปกติ",
        "advice": "พักผ่อนให้เพียงพอ",
    }
    curated_hook = ZodiacCurator.curate_hook("cancer", "กรกฎ", reading["hook"], reading["overview"], reading)
    assert curated_hook.startswith("ราศีกรกฎ")
    # Must derive tension from the work section
    assert "ระวังความขัดแย้ง" in curated_hook
    # Must NOT be the static strong hook template for cancer
    assert curated_hook != ZodiacCurator.STRONG_HOOK_TEMPLATES["cancer"]


def test_fallback_to_template_when_content_insufficient():
    # Reading has weak hook and no substance in sections
    reading = {
        "id": "libra",
        "hook": "ราศีตุลย์",
        "overview": "",
        "work": "ดี",
        "finance": "พอใช้",
        "love": "สงบ",
        "advice": "",
    }
    curated_hook = ZodiacCurator.curate_hook("libra", "ตุลย์", reading["hook"], reading["overview"], reading)
    assert curated_hook == ZodiacCurator.STRONG_HOOK_TEMPLATES["libra"]


def test_curator_report_populated_correctly():
    readings = sample_readings()
    # Introduce one weak hook
    readings[4]["hook"] = "สั้นไป"
    for i in range(12):
        if i != 4:
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    report = curated["curator"]

    assert report["version"] == "1.2.1"
    assert report["status"] == "curated"
    assert report["rewritten_hooks_count"] >= 1
    assert isinstance(report["rewritten_hooks"], list)
    assert isinstance(report["technical_terms_removed"], int)
    assert isinstance(report["repeated_prefixes_fixed"], int)
    assert isinstance(report["similar_hooks_detected"], list)
    assert isinstance(report["warnings"], list)


def test_technical_astrology_decanted_and_counted():
    readings = sample_readings()
    # Add technical astrology in readings
    readings[0]["work"] = "ดาวอังคารในเรือนอาชีพทำให้มีไฟทำงาน"
    readings[0]["finance"] = "ดาวศุกร์ในเรือนการเงินทำมุมจตุโกณกับดาวพลูโต ระวังการใช้จ่าย"
    for i in range(1, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาดครับ"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    report = curated["curator"]

    assert report["technical_terms_removed"] >= 2
    # Ensure translated
    capricorn = curated["zodiacs"][0]
    assert "จังหวะงานช่วงนี้" in capricorn["work"]
    assert "ด้านการเงินช่วงนี้" in capricorn["finance"]


def test_repetitive_star_openings_fixed_and_counted():
    readings = sample_readings()
    readings[0]["work"] = "ดาวอังคารทำให้งานเดินหน้า"
    readings[0]["finance"] = "ดวงอาทิตย์ส่งผลให้การเงินเริ่มคลี่คลาย"
    for i in range(1, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาดครับ"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    report = curated["curator"]

    assert report["repeated_prefixes_fixed"] >= 2
    capricorn = curated["zodiacs"][0]
    assert capricorn["work"].startswith("ด้านการงาน")
    assert capricorn["finance"].startswith("ด้านการเงิน")


def test_full_batch_all_12_signs_maintain_diversity():
    # Pass sample readings where all hooks were originally identical
    readings = sample_readings()
    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))

    final_zodiacs = curated["zodiacs"]
    assert len(final_zodiacs) == 12

    hooks = [z["hook"] for z in final_zodiacs]
    norms = [ZodiacCurator.normalize_hook(z["hook"], ZODIACS[i].name_th) for i, z in enumerate(final_zodiacs)]
    patterns = [ZodiacCurator.extract_opening_pattern(z["hook"], ZODIACS[i].name_th) for i, z in enumerate(final_zodiacs)]

    # 1. All hooks start with respective zodiac name
    for i, z in enumerate(final_zodiacs):
        assert z["hook"].startswith(f"ราศี{ZODIACS[i].name_th}")
        assert len(z["hook"]) >= 28

    # 2. Pairwise similarity < 0.80 across all 12 signs
    for i in range(12):
        for j in range(i + 1, 12):
            sim = ZodiacCurator.calculate_similarity(norms[i], norms[j])
            assert sim < ZodiacCurator.HOOK_SIMILARITY_THRESHOLD, f"Signs {final_zodiacs[i]['id']} and {final_zodiacs[j]['id']} are too similar ({sim:.2f})"

    # 3. No pattern dominates (> 2 times)
    pattern_freq: dict[str, int] = {}
    for p in patterns:
        pattern_freq[p] = pattern_freq.get(p, 0) + 1
        assert pattern_freq[p] <= ZodiacCurator.MAX_SHARED_OPENING_PATTERN, f"Pattern '{p}' exceeded max allowed"


def test_semantic_curiosity_without_keyword_preserved():
    # Semantic curiosity without predefined tokens (e.g. "คนอื่นจะเห็นความเปลี่ยนแปลงในตัวคุณก่อนที่คุณจะรู้ตัว")
    readings = sample_readings()
    readings[1]["hook"] = "ราศีกุมภ์ สัปดาห์นี้คนอื่นจะเห็นความเปลี่ยนแปลงในตัวคุณก่อนที่คุณจะรู้ตัว"
    for i in range(2, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    aquarius_hook = curated["zodiacs"][1]["hook"]
    assert aquarius_hook == "ราศีกุมภ์ สัปดาห์นี้คนอื่นจะเห็นความเปลี่ยนแปลงในตัวคุณก่อนที่คุณจะรู้ตัว"
    rewritten_ids = [item["id"] for item in curated["curator"]["rewritten_hooks"]]
    assert "aquarius" not in rewritten_ids


def test_overlong_hook_shortened_to_under_120():
    readings = sample_readings()
    # Create hook > 120 chars
    readings[0]["hook"] = (
        "ราศีมังกร สัปดาห์นี้เรื่องงานที่คุณทุ่มเทมานานกำลังจะส่งผลลัพธ์ที่น่าพอใจอย่างมาก "
        "แต่ในขณะเดียวกันก็ต้องระมัดระวังเรื่องเอกสารสัญญาและข้อตกลงต่างๆ ให้รอบคอบที่สุดเพื่อไม่ให้เสียเปรียบในอนาคตครับผม"
    )
    assert len(readings[0]["hook"]) > 120
    for i in range(1, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    capricorn_hook = curated["zodiacs"][0]["hook"]
    assert len(capricorn_hook) <= 120
    assert curated["curator"]["overlong_hooks_rewritten"] >= 1
    overlong_entry = next(item for item in curated["curator"]["rewritten_hooks"] if item["id"] == "capricorn")
    assert "overlong_hook" in overlong_entry["reason"]


def test_hook_length_45_to_90_preserved():
    hook = "ราศีสิงห์ สัปดาห์นี้ผลงานเด่นชัดเป็นที่ยอมรับ แต่ต้องระวังอย่าประมาท"
    assert 45 <= len(hook) <= 90
    curated_hook = ZodiacCurator.curate_hook("leo", "สิงห์", hook, "ภาพรวมสัปดาห์นี้", {})
    assert curated_hook == hook


def test_hook_identical_to_overview_rewritten():
    readings = sample_readings()
    body_text = "ภาพรวมสัปดาห์นี้มีแนวโน้มได้ทบทวนเป้าหมายสำคัญและระวังความผิดพลาด"
    readings[0]["hook"] = f"ราศีมังกร {body_text}"
    readings[0]["overview"] = body_text
    for i in range(1, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    capricorn_hook = curated["zodiacs"][0]["hook"]
    # Must NOT be identical to overview
    assert body_text not in capricorn_hook
    assert curated["curator"]["hook_body_duplicates_rewritten"] >= 1
    dup_entry = next(item for item in curated["curator"]["rewritten_hooks"] if item["id"] == "capricorn")
    assert "duplicate_body_section_overview" in dup_entry["reason"]


def test_hook_identical_to_work_rewritten():
    readings = sample_readings()
    work_text = "งานมีความก้าวหน้าจากการสื่อสารที่ชัดเจน แต่ระวังความเข้าใจผิดกับเพื่อนร่วมทีม"
    readings[2]["hook"] = f"ราศีมีน {work_text}"
    readings[2]["work"] = work_text
    for i in range(12):
        if i != 2:
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    pisces_hook = curated["zodiacs"][2]["hook"]
    assert work_text not in pisces_hook
    assert curated["curator"]["hook_body_duplicates_rewritten"] >= 1


def test_hook_identical_to_finance_rewritten():
    readings = sample_readings()
    finance_text = "การเงินมีโชคลาภเข้ามาจากงานเสริม แต่ต้องระวังรายจ่ายกะทันหันเรื่องสุขภาพ"
    readings[3]["hook"] = f"ราศีเมษ {finance_text}"
    readings[3]["finance"] = finance_text
    for i in range(12):
        if i != 3:
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    aries_hook = curated["zodiacs"][3]["hook"]
    assert finance_text not in aries_hook
    assert curated["curator"]["hook_body_duplicates_rewritten"] >= 1


def test_hook_identical_to_love_rewritten():
    readings = sample_readings()
    love_text = "ความสัมพันธ์ต้องการความชัดเจนในการสื่อสาร แต่อย่าเพิ่งด่วนตัดสินใจจากอารมณ์ชั่ววูบ"
    readings[4]["hook"] = f"ราศีพฤษภ {love_text}"
    readings[4]["love"] = love_text
    for i in range(12):
        if i != 4:
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    taurus_hook = curated["zodiacs"][4]["hook"]
    assert love_text not in taurus_hook
    assert curated["curator"]["hook_body_duplicates_rewritten"] >= 1


def test_hook_identical_to_advice_rewritten():
    readings = sample_readings()
    advice_text = "รักษาความสงบและรอบคอบในการตัดสินใจ อย่าเพิ่งเชื่อข่าวลือที่ยังไม่ได้ตรวจสอบ"
    readings[5]["hook"] = f"ราศีเมถุน {advice_text}"
    readings[5]["advice"] = advice_text
    for i in range(12):
        if i != 5:
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    gemini_hook = curated["zodiacs"][5]["hook"]
    assert advice_text not in gemini_hook
    assert curated["curator"]["hook_body_duplicates_rewritten"] >= 1


def test_body_similarity_threshold_075_triggers_rewrite():
    # Test checking 0.75 threshold trigger
    reading = {
        "id": "leo",
        "hook": "ราศีสิงห์ สัปดาห์นี้มีโอกาสทางการเงินเข้ามา แต่ต้องระวังอย่าให้ความเกรงใจทำให้เสียเปรียบ",
        "overview": "ภาพรวม",
        "work": "งาน",
        "finance": "ด้านการเงิน สัปดาห์นี้มีโอกาสทางการเงินเข้ามา แต่ระวังอย่าให้ความเกรงใจทำให้เสียเปรียบมากเกินไป",
        "love": "รัก",
        "advice": "แนะนำ",
    }
    is_dup, sec, sim = ZodiacCurator.check_body_similarity(reading["hook"], "สิงห์", reading)
    assert is_dup is True
    assert sec == "finance"
    assert sim >= 0.75


def test_polite_ending_krub_removed_from_hook():
    hook, changed = ZodiacCurator.strip_hook_polite_ending("ราศีพิจิก สัปดาห์นี้มีพลังมากครับ")
    assert hook == "ราศีพิจิก สัปดาห์นี้มีพลังมาก"
    assert changed is True


def test_polite_ending_ka_removed_from_hook():
    hook, changed = ZodiacCurator.strip_hook_polite_ending("ราศีพฤษภ สัปดาห์นี้มีโอกาสดีค่ะ")
    assert hook == "ราศีพฤษภ สัปดาห์นี้มีโอกาสดี"
    assert changed is True


def test_polite_ending_nakrub_removed_from_hook():
    hook, changed = ZodiacCurator.strip_hook_polite_ending("ราศีกุมภ์ สัปดาห์นี้ต้องระวังนะครับ")
    assert hook == "ราศีกุมภ์ สัปดาห์นี้ต้องระวัง"
    assert changed is True


def test_polite_ending_naka_removed_from_hook():
    hook, changed = ZodiacCurator.strip_hook_polite_ending("ราศีมีน สัปดาห์นี้สัญชาตญาณแม่นยำนะคะ")
    assert hook == "ราศีมีน สัปดาห์นี้สัญชาตญาณแม่นยำ"
    assert changed is True


def test_polite_ending_in_body_preserved():
    readings = sample_readings()
    readings[0]["work"] = "ด้านการงาน มีความก้าวหน้าชัดเจนมากครับ"
    readings[0]["closing"] = "ขอให้โชคดีตลอดทั้งสัปดาห์นะคะ"
    for i in range(1, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    capricorn = curated["zodiacs"][0]
    # Body sections should preserve polite endings
    assert capricorn["work"].endswith("ครับ")
    assert capricorn["closing"].endswith("นะคะ")


def test_duplicated_section_prefix_love_cleaned():
    reading = {"love": "ด้านความรัก ความรักช่วงนี้ต้องการความเข้าใจและเวลาให้กัน"}
    count = ZodiacCurator.clean_duplicated_section_prefixes(reading)
    assert count == 1
    assert reading["love"] == "ด้านความรัก ช่วงนี้ต้องการความเข้าใจและเวลาให้กัน"


def test_duplicated_section_prefix_finance_cleaned():
    reading = {"finance": "ด้านการเงิน การเงินช่วงนี้มีโอกาสได้โชคลาภก้อนใหม่"}
    count = ZodiacCurator.clean_duplicated_section_prefixes(reading)
    assert count == 1
    assert reading["finance"] == "ด้านการเงิน ช่วงนี้มีโอกาสได้โชคลาภก้อนใหม่"


def test_duplicated_section_prefix_work_cleaned():
    reading = {"work": "ด้านการงาน งานช่วงนี้กำลังเดินหน้าอย่างราบรื่น"}
    count = ZodiacCurator.clean_duplicated_section_prefixes(reading)
    assert count == 1
    assert reading["work"] == "ด้านการงาน ช่วงนี้กำลังเดินหน้าอย่างราบรื่น"


def test_week_display_th_buddhist_era_year_2569():
    readings = sample_readings()
    for i in range(12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    # 2026 + 543 = 2569
    assert curated["week"]["display_th"] == "14 - 20 ก.ย. 2569"
    assert "2569" in curated["week"]["display_th"]


def test_curator_report_contains_all_editorial_counters():
    readings = sample_readings()
    # Add a hook with polite ending to verify polite_hook_endings_removed counter
    readings[0]["hook"] = "ราศีมังกร สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจครับ"
    # Add a hook > 120 chars
    readings[1]["hook"] = "ราศีกุมภ์ สัปดาห์นี้เรื่องราวต่างๆ ที่เข้ามามากมายอาจทำให้คุณรู้สึกสับสนและลังเลจนไม่รู้จะเลือกทางไหนดี แต่ถ้าชะลอจังหวะลงจะเห็นทางออกที่ชัดเจนและเรียบง่ายกว่าที่คิดไว้ครับผม"
    # Add duplicated prefix in love
    readings[2]["love"] = "ด้านความรัก ความรักช่วงนี้หวานชื่นดี"
    for i in range(3, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    report = curated["curator"]

    assert "overlong_hooks_rewritten" in report
    assert "hook_body_duplicates_rewritten" in report
    assert "polite_hook_endings_removed" in report
    assert "duplicated_section_prefixes_removed" in report
    assert "semantic_hooks_preserved" in report
    assert report["polite_hook_endings_removed"] >= 1
    assert report["overlong_hooks_rewritten"] >= 1
    assert report["duplicated_section_prefixes_removed"] >= 1
    assert report["semantic_hooks_preserved"] >= 1


def test_is_merely_advice_hook_detection():
    # Mere advice without tension should be detected
    assert ZodiacCurator.is_merely_advice_hook("ราศีมีน สัปดาห์นี้พักผ่อนให้เพียงพอและหลีกเลี่ยงการแบกปัญหาคนอื่น", "มีน") is True
    assert ZodiacCurator.is_merely_advice_hook("ราศีมีน สัปดาห์นี้ควรพักผ่อนให้เพียงพอ", "มีน") is True
    assert ZodiacCurator.is_merely_advice_hook("ราศีมีน สัปดาห์นี้ดูแลตัวเองให้ดี", "มีน") is True
    assert ZodiacCurator.is_merely_advice_hook("ราศีมีน สัปดาห์นี้รักษาความสงบและรอบคอบในการตัดสินใจ", "มีน") is True
    assert ZodiacCurator.is_merely_advice_hook("ราศีเมษ สัปดาห์นี้ฝึกความอดทนและโฟกัสทีละเรื่อง", "เมษ") is True

    # Hooks with tension/contrast must NOT be classified as mere advice
    assert ZodiacCurator.is_merely_advice_hook(
        "ราศีมีน สัปดาห์นี้เรื่องของคนอื่นอาจเข้ามาหนักกว่าที่คิด แต่ไม่ใช่ทุกอย่างที่คุณต้องรับไว้", "มีน"
    ) is False
    assert ZodiacCurator.is_merely_advice_hook(
        "ราศีมีน สัปดาห์นี้ถ้าชะลอจังหวะลงจะเห็นทางออกที่ชัดเจนและเรียบง่ายกว่าที่คิดไว้มาก", "มีน"
    ) is False
    assert ZodiacCurator.is_merely_advice_hook("ราศีมีน สัปดาห์นี้มีเรื่องสำคัญที่อย่าเพิ่งรีบตัดสินใจ", "มีน") is False


def test_overlong_hook_shortens_preferring_original_meaning_over_advice():
    readings = sample_readings()
    # Pisces with overlong hook and mere advice
    readings[2]["hook"] = (
        "ราศีมีน สัปดาห์นี้เรื่องราวต่างๆ ที่เข้ามามากมายอาจทำให้คุณรู้สึกสับสนและลังเลจนไม่รู้จะเลือกทางไหนดี "
        "แต่ถ้าชะลอจังหวะลงจะเห็นทางออกที่ชัดเจนและเรียบง่ายกว่าที่คิดไว้มากครับผม"
    )
    readings[2]["advice"] = "พักผ่อนให้เพียงพอและหลีกเลี่ยงการแบกปัญหาคนอื่น"
    for i in range(12):
        if i != 2:
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    pisces_hook = curated["zodiacs"][2]["hook"]

    # Must NOT be the advice text
    assert "พักผ่อนให้เพียงพอ" not in pisces_hook
    # Must derive from the original hook's core tension
    assert len(pisces_hook) <= 120
    assert "สับสนและลังเล" in pisces_hook or "ชะลอจังหวะ" in pisces_hook
    assert curated["curator"]["overlong_hooks_rewritten"] >= 1


def test_overlong_hook_priority_order_overview_before_work_before_advice():
    # If original hook has no extractable sub-clause under 120, prefer overview over work over advice
    reading = {
        "id": "gemini",
        "hook": "ราศีเมถุน " + ("ก" * 130),  # cannot be shortened from original hook clauses
        "overview": "ภาพรวมสัปดาห์นี้มีจุดเปลี่ยนสำคัญที่ทำให้ต้องทบทวนแผนใหม่",
        "work": "ด้านการงาน มีความท้าทายใหม่ที่น่าจับตา",
        "finance": "การเงินปกติ",
        "love": "ความรักปกติ",
        "advice": "พักผ่อนให้เพียงพอและหลีกเลี่ยงความเครียด",
    }
    curated_hook = ZodiacCurator.curate_hook("gemini", "เมถุน", reading["hook"], reading["overview"], reading)

    # Source 2 (overview) should take priority over Source 3 (work) and Source 4 (advice)
    assert "จุดเปลี่ยนสำคัญ" in curated_hook
    assert "พักผ่อน" not in curated_hook


def test_preserve_strong_semantic_tension_hooks_without_curiosity_markers():
    """Regression test: hooks with semantic tension/open loops must NOT be rewritten
    solely because they lack predefined curiosity tokens.
    """
    readings = sample_readings()

    # 1. Pisces: "ราศีมีน ความสัมพันธ์อาจเปลี่ยนทิศ เพราะมีคนกำลังรอให้คุณพูดก่อน"
    pisces_expected = "ราศีมีน ความสัมพันธ์อาจเปลี่ยนทิศ เพราะมีคนกำลังรอให้คุณพูดก่อน"
    readings[2]["hook"] = pisces_expected

    # 2. Cancer: "ราศีกรกฎ ครอบครัวกับงานกำลังแย่งเวลา และคุณต้องเลือกก่อนใคร"
    cancer_expected = "ราศีกรกฎ ครอบครัวกับงานกำลังแย่งเวลา และคุณต้องเลือกก่อนใคร"
    readings[6]["hook"] = cancer_expected

    for i in range(12):
        if i not in (2, 6):
            readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    zodiacs = curated["zodiacs"]

    # Both hooks must be preserved as-is without being flagged as weak_hook
    assert zodiacs[2]["hook"] == pisces_expected
    assert zodiacs[6]["hook"] == cancer_expected

    rewritten_ids = [item["id"] for item in curated["curator"]["rewritten_hooks"]]
    assert "pisces" not in rewritten_ids
    assert "cancer" not in rewritten_ids


def test_normalize_duplicated_time_prefixes():
    """Never generate hooks containing duplicated time prefixes e.g.
    'สัปดาห์นี้ช่วงนี้...', 'ช่วงนี้สัปดาห์นี้', 'สัปดาห์นี้สัปดาห์นี้'.
    """
    # Test normalization helper directly
    assert ZodiacCurator.normalize_hook_time_prefixes("ราศีมีน สัปดาห์นี้ช่วงนี้เรื่องงานเด่น") == "ราศีมีน สัปดาห์นี้เรื่องงานเด่น"
    assert ZodiacCurator.normalize_hook_time_prefixes("ราศีกุมภ์ ช่วงนี้สัปดาห์นี้ระวังการเงิน") == "ราศีกุมภ์ ช่วงนี้ระวังการเงิน"
    assert ZodiacCurator.normalize_hook_time_prefixes("ราศีเมษ สัปดาห์นี้สัปดาห์นี้มีโอกาสใหญ่") == "ราศีเมษ สัปดาห์นี้มีโอกาสใหญ่"
    assert ZodiacCurator.normalize_hook_time_prefixes("ราศีสิงห์ สัปดาห์นี้ ในสัปดาห์นี้งานหนัก") == "ราศีสิงห์ สัปดาห์นี้งานหนัก"

    # Test through curate_hook and clean_hook_prefix
    cleaned = ZodiacCurator.clean_hook_prefix("สัปดาห์นี้ช่วงนี้ ความสัมพันธ์อาจเปลี่ยนทิศ เพราะมีคนรออยู่", "มีน")
    assert cleaned.startswith("ราศีมีน สัปดาห์นี้")
    assert "ช่วงนี้" not in cleaned


def test_derive_hook_excludes_technical_astrology_when_life_first_tension_exists():
    """Hooks derived from content must not select technical astrology jargon
    (e.g., 'ดาวอังคารโคจรอยู่ในราศี...', 'เรือนภพที่ 10') when life-first tension exists.
    """
    reading = {
        "id": "cancer",
        "hook": "สั้น",  # triggers derivation
        "overview": "ภาพรวมสัปดาห์นี้ดาวอังคารโคจรทำมุมจตุโกณกับดาวเสาร์ในเรือนภพที่สี่",
        "work": "ด้านการงาน ครอบครัวกับงานกำลังแย่งเวลา และคุณต้องตัดสินใจเลือกให้ชัดเจนก่อนใคร",
        "finance": "การเงินราบรื่นดี",
        "love": "ความรักปกติ",
        "advice": "พักผ่อนให้เพียงพอ",
    }

    curated_hook = ZodiacCurator.curate_hook("cancer", "กรกฎ", reading["hook"], reading["overview"], reading)

    # Must select life-first tension from work section, NOT technical astro from overview
    assert "ครอบครัวกับงานกำลังแย่งเวลา" in curated_hook
    assert "ดาวอังคาร" not in curated_hook
    assert "เรือนภพ" not in curated_hook
    assert "จตุโกณ" not in curated_hook


def test_curator_version_is_1_2_1():
    assert ZodiacCurator.CURATOR_VERSION == "1.2.1"


def test_soften_deterministic_claims_and_health_safety_rules():
    reading = {
        "id": "aries",
        "hook": "ราศีเมษ สัปดาห์นี้จะได้เงินแน่นอนและปัญหาหนี้สินจะหายไป",
        "overview": "เรื่องที่กังวลจะหายแน่นอน",
        "work": "งานนี้จะสำเร็จแน่นอน และจะได้งานแน่นอน",
        "finance": "ด้านการเงินจะรวยแน่นอน และแน่นอน 100%",
        "love": "คนโสดจะพบเนื้อคู่แน่นอน",
        "advice": "พักผ่อนให้เพียงพอและดูแลสุขภาพ ไม่ควรขับรถเร็วเพราะจะเกิดอุบัติเหตุ",
        "closing": "คำทำนายนี้เป็นแนวทาง ขอให้โชคดีครับ",
    }
    count = ZodiacCurator.soften_deterministic_claims(reading)
    assert count >= 7

    # Verifications of softened claims
    assert "มีโอกาสได้เงิน" in reading["hook"]
    assert "อาจค่อย ๆ คลี่คลาย" in reading["hook"]
    assert "มีแนวโน้มดีขึ้น" in reading["overview"]
    assert "มีโอกาสสำเร็จสูง" in reading["work"]
    assert "มีโอกาสได้งาน" in reading["work"]
    assert "มีโอกาสทางการเงินที่ดีขึ้น" in reading["finance"]
    assert "มีโอกาสพบคนที่ถูกใจ" in reading["love"]

    # Verification of health/safety rules
    assert "ควรระมัดระวังความปลอดภัยในการเดินทาง" in reading["advice"]
    assert "จะเกิดอุบัติเหตุ" not in reading["advice"]

    # General wellness advice preserved
    assert "พักผ่อนให้เพียงพอและดูแลสุขภาพ" in reading["advice"]


def test_curate_batch_reports_softened_claims_count():
    readings = sample_readings()
    readings[0]["finance"] = "สัปดาห์นี้จะได้เงินแน่นอน และหนี้จะหายไป"
    for i in range(1, 12):
        readings[i]["hook"] = f"ราศี{ZODIACS[i].name_th} สัปดาห์นี้มีเอกลักษณ์ข้อที่ {i} แต่ต้องระวังจุดผิดพลาด"

    curated = ZodiacCurator.curate_batch({"zodiacs": readings}, date(2026, 9, 14), date(2026, 9, 20))
    report = curated["curator"]

    assert report["version"] == "1.2.1"
    assert report["deterministic_claims_softened"] >= 2
    assert "มีโอกาสได้เงิน" in curated["zodiacs"][0]["finance"]
    assert "อาจค่อย ๆ คลี่คลาย" in curated["zodiacs"][0]["finance"]

