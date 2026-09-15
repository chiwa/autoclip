from datetime import date
from pathlib import Path
import pytest

from app.domain.errors import AppError
from app.services.zodiac_ephemeris_service import ZodiacEphemerisService, julian_day


def test_julian_day_calculation():
    # J2000 epoch 2000-01-01 12:00 TT is 2451545.0. At 00:00 UTC it is 2451544.5
    jd = julian_day(date(2000, 1, 1))
    assert jd == 2451544.5


def test_calculate_positions_for_known_date(tmp_path):
    service = ZodiacEphemerisService(tmp_path)
    positions = service.calculate_positions(date(2026, 9, 14))

    assert "sun" in positions
    assert positions["sun"]["sign"] == "virgo"
    assert positions["sun"]["sign_th"] == "กันย์"
    assert 170.0 <= positions["sun"]["longitude_deg"] <= 173.0

    assert "jupiter" in positions
    assert positions["jupiter"]["sign"] == "leo"
    assert positions["jupiter"]["sign_th"] == "สิงห์"

    assert "saturn" in positions
    assert positions["saturn"]["sign"] == "aries"
    assert positions["saturn"]["sign_th"] == "เมษ"


def test_weekly_research_and_caching(tmp_path):
    service = ZodiacEphemerisService(tmp_path)
    start = date(2026, 9, 14)
    end = date(2026, 9, 20)

    # First call: computes and creates cache
    research = service.get_weekly_research(start, end)
    assert research["verified"] is True
    assert research["week"]["start_date"] == "2026-09-14"
    assert research["week"]["end_date"] == "2026-09-20"
    assert "planetary_positions" in research
    assert len(research["planetary_positions"]) == 10
    assert "summary_th" in research

    cache_file = tmp_path / "ephemeris-cache" / "ephemeris-2026-09-14-to-2026-09-20.json"
    assert cache_file.is_file()

    # Second call: loads from cache
    cached = service.get_weekly_research(start, end)
    assert cached["week"] == research["week"]
    assert cached["calculated_at"] == research["calculated_at"]


def test_invalid_date_range_raises_error(tmp_path):
    service = ZodiacEphemerisService(tmp_path)
    with pytest.raises(AppError) as exc:
        service.get_weekly_research(date(2026, 9, 20), date(2026, 9, 14))
    assert exc.value.code == "INVALID_DATE_RANGE"
