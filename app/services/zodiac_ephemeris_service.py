from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path

from app.domain.errors import AppError


ZODIAC_SIGNS = (
    ("aries", "เมษ"),
    ("taurus", "พฤษภ"),
    ("gemini", "เมถุน"),
    ("cancer", "กรกฎ"),
    ("leo", "สิงห์"),
    ("virgo", "กันย์"),
    ("libra", "ตุลย์"),
    ("scorpio", "พิจิก"),
    ("sagittarius", "ธนู"),
    ("capricorn", "มังกร"),
    ("aquarius", "กุมภ์"),
    ("pisces", "มีน"),
)

# NASA JPL Keplerian Elements for Approximate Positions of the Major Planets (1800-2050)
# [a0, e0, I0, L0, w0, node0, da, de, dI, dL, dw, dnode]
# Semi-major axis in AU, angles in degrees, rates per Julian century (36525 days)
JPL_PLANETS: dict[str, tuple[float, ...]] = {
    "mercury": (0.38709927, 0.20563593, 7.00497902, 252.25032350, 77.45779628, 48.33076593,
                0.00000037, 0.00001906, -0.00594749, 149472.67411175, 0.16047689, -0.12534081),
    "venus":   (0.72333566, 0.00677672, 3.39467605, 181.97909950, 131.60246718, 76.67984255,
                0.00000026, -0.00004107, -0.00078890, 58517.81538729, 0.00268329, -0.27769418),
    "earth":   (1.00000261, 0.01671123, -0.00001531, 100.46457166, 102.93768193, 0.0,
                0.00000562, -0.00004392, -0.01294668, 35999.37244981, 0.32327364, 0.0),
    "mars":    (1.52371034, 0.09339410, 1.84969142, -4.55343205, -23.94362959, 49.55953891,
                0.00001847, 0.00007882, -0.00813131, 19140.30268499, 0.44441088, -0.29257343),
    "jupiter": (5.20288700, 0.04838624, 1.30439695, 34.39644051, 14.72847983, 100.47390909,
                -0.00011607, -0.00013253, -0.00183714, 3034.74612775, 0.21252668, 0.20469106),
    "saturn":  (9.53667594, 0.05386179, 2.48599187, 49.95424423, 92.59887831, 113.66242448,
                -0.00125060, -0.00050991, 0.00193609, 1222.49362201, -0.41897216, -0.28867794),
    "uranus":  (19.18916464, 0.04725744, 0.77263783, 313.23810451, 170.95427630, 74.01692503,
                -0.00196150, -0.00004397, -0.00242939, 428.48202785, 0.40805281, 0.04240589),
    "neptune": (30.06992276, 0.00859048, 1.77004347, -55.12002969, 44.96476227, 131.78422574,
                0.00026291, 0.00005105, 0.00035372, 218.45945325, -0.32241464, -0.00508664),
    "pluto":   (39.48211675, 0.24882730, 17.14001206, 238.92903833, 224.06891629, 110.30393608,
                -0.00031596, 0.00005170, 0.00004818, 145.20780515, -0.04062942, -0.01183482),
}

PLANET_NAMES_TH: dict[str, str] = {
    "sun": "ดวงอาทิตย์",
    "moon": "ดวงจันทร์",
    "mercury": "ดาวพุธ",
    "venus": "ดาวศุกร์",
    "mars": "ดาวอังคาร",
    "jupiter": "ดาวพฤหัสบดี",
    "saturn": "ดาวเสาร์",
    "uranus": "ดาวยูเรนัส",
    "neptune": "ดาวเนปจูน",
    "pluto": "ดาวพลูโต",
}


def julian_day(d: date) -> float:
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3
    return d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045 - 0.5


def centuries_since_j2000(d: date) -> float:
    return (julian_day(d) - 2451545.0) / 36525.0


def _helio_coords(body: str, t: float) -> tuple[float, float, float]:
    params = JPL_PLANETS[body]
    a = params[0] + params[6] * t
    e = params[1] + params[7] * t
    i_rad = math.radians(params[2] + params[8] * t)
    l_deg = (params[3] + params[9] * t) % 360
    w_bar = (params[4] + params[10] * t) % 360
    node = math.radians((params[5] + params[11] * t) % 360)
    omega = math.radians((w_bar - math.degrees(node)) % 360)
    m_rad = math.radians((l_deg - w_bar) % 360)

    e_ano = m_rad
    for _ in range(15):
        de = (m_rad - (e_ano - e * math.sin(e_ano))) / (1.0 - e * math.cos(e_ano))
        e_ano += de
        if abs(de) < 1e-9:
            break

    x_prime = a * (math.cos(e_ano) - e)
    y_prime = a * math.sqrt(max(0.0, 1 - e**2)) * math.sin(e_ano)

    cos_w, sin_w = math.cos(omega), math.sin(omega)
    cos_n, sin_n = math.cos(node), math.sin(node)
    cos_i, sin_i = math.cos(i_rad), math.sin(i_rad)

    x = (cos_w * cos_n - sin_w * sin_n * cos_i) * x_prime + (-sin_w * cos_n - cos_w * sin_n * cos_i) * y_prime
    y = (cos_w * sin_n + sin_w * cos_n * cos_i) * x_prime + (-sin_w * sin_n + cos_w * cos_n * cos_i) * y_prime
    z = (sin_w * sin_i) * x_prime + (cos_w * sin_i) * y_prime
    return x, y, z


def _sun_tropical_longitude(t: float) -> float:
    # High-precision solar coordinates (Meeus Astronomical Algorithms)
    l0 = (280.46646 + 36000.76983 * t + 0.0003032 * t**2) % 360
    m = math.radians((357.52911 + 35999.05029 * t - 0.0001537 * t**2) % 360)
    c = (1.914602 - 0.004817 * t - 0.000014 * t**2) * math.sin(m) \
        + (0.019993 - 0.000101 * t) * math.sin(2 * m) \
        + 0.000289 * math.sin(3 * m)
    true_lon = (l0 + c) % 360
    # Apparent longitude corrected for nutation and aberration
    omega = math.radians((125.04 - 1934.136 * t) % 360)
    apparent_lon = true_lon - 0.00569 - 0.00478 * math.sin(omega)
    return apparent_lon % 360


def _moon_tropical_longitude(t: float) -> float:
    # Truncated ELP2000 / Meeus lunar coordinates (~0.05 deg precision)
    l_prime = (218.3164477 + 481267.88128 * t) % 360
    d = math.radians((297.8501921 + 445267.1142 * t) % 360)
    m = math.radians((357.5291092 + 35999.05029 * t) % 360)
    m_prime = math.radians((134.9633964 + 477198.8675 * t) % 360)
    f = math.radians((93.2720950 + 483202.0175 * t) % 360)

    sigma_l = (
        6.288774 * math.sin(m_prime)
        + 1.274027 * math.sin(2 * d - m_prime)
        + 0.658314 * math.sin(2 * d)
        + 0.213618 * math.sin(2 * m_prime)
        - 0.185116 * math.sin(m)
        - 0.114332 * math.sin(2 * f)
        + 0.058793 * math.sin(2 * d - 2 * m_prime)
        + 0.057066 * math.sin(2 * d - m - m_prime)
        + 0.053322 * math.sin(2 * d + m_prime)
        + 0.045758 * math.sin(2 * d - m)
        - 0.040923 * math.sin(m_prime - m)
        - 0.034720 * math.sin(d)
        - 0.030383 * math.sin(m + m_prime)
        + 0.015327 * math.sin(2 * d - 2 * f)
    )
    return (l_prime + sigma_l) % 360


def _planet_tropical_longitude(planet: str, t: float, earth_coords: tuple[float, float, float]) -> float:
    px, py, pz = _helio_coords(planet, t)
    ex, ey, ez = earth_coords
    gx, gy = px - ex, py - ey
    # J2000 ecliptic longitude
    j2000_lon = math.degrees(math.atan2(gy, gx)) % 360
    # General precession in longitude from J2000 to equinox of date
    precession = (1.396971 * t + 0.0003086 * t**2) % 360
    return (j2000_lon + precession) % 360


class ZodiacEphemerisService:
    """Deterministic celestial calculation service for tropical zodiac ephemeris and transits."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir / "ephemeris-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def calculate_positions(self, target_date: date) -> dict[str, dict]:
        t = centuries_since_j2000(target_date)
        earth_coords = _helio_coords("earth", t)

        positions: dict[str, dict] = {}

        # 1. Sun
        sun_lon = _sun_tropical_longitude(t)
        positions["sun"] = self._format_body_data("sun", sun_lon)

        # 2. Moon
        moon_lon = _moon_tropical_longitude(t)
        positions["moon"] = self._format_body_data("moon", moon_lon)

        # 3. Major planets
        for planet in ("mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"):
            p_lon = _planet_tropical_longitude(planet, t, earth_coords)
            positions[planet] = self._format_body_data(planet, p_lon)

        return positions

    def get_weekly_research(self, start_date: date, end_date: date) -> dict:
        if end_date < start_date:
            raise AppError("INVALID_DATE_RANGE", "วันที่สิ้นสุดต้องไม่ก่อนวันที่เริ่มต้น")

        cache_file = self.cache_dir / f"ephemeris-{start_date.isoformat()}-to-{end_date.isoformat()}.json"
        if cache_file.is_file():
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                self._validate_research(cached)
                return cached
            except Exception:
                # If cached file corrupted, regenerate
                pass

        try:
            research = self._build_weekly_research(start_date, end_date)
            self._validate_research(research)
            temp = cache_file.with_suffix(".tmp")
            temp.write_text(json.dumps(research, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.replace(cache_file)
            return research
        except AppError:
            raise
        except Exception as exc:
            raise AppError("EPHEMERIS_UNAVAILABLE", f"ไม่สามารถคำนวณตำแหน่งดวงดาวประจำสัปดาห์ได้: {exc}") from exc

    def _build_weekly_research(self, start_date: date, end_date: date) -> dict:
        start_positions = self.calculate_positions(start_date)
        end_positions = self.calculate_positions(end_date)

        # Determine retrograde status: planet longitude decreases over the week
        for planet in start_positions:
            if planet in ("sun", "moon"):
                start_positions[planet]["is_retrograde"] = False
                continue
            s_lon = start_positions[planet]["longitude_deg"]
            e_lon = end_positions[planet]["longitude_deg"]
            # Handle 360 wrap-around
            diff = (e_lon - s_lon + 180) % 360 - 180
            start_positions[planet]["is_retrograde"] = diff < 0.0

        # Aspects detection between major planets at mid-week
        mid_days = max(1, (end_date - start_date).days // 2)
        mid_date = start_date + timedelta(days=mid_days)
        mid_positions = self.calculate_positions(mid_date)

        aspects = self._detect_aspects(mid_positions, mid_date)
        moon_phases = self._detect_moon_phases(start_date, end_date)

        # Generate clear summary
        summary_lines = [
            f"ตำแหน่งดวงอาทิตย์: ราศี{start_positions['sun']['sign_th']} ({start_positions['sun']['degree_in_sign']:.1f}°)",
            f"ตำแหน่งดวงจันทร์: เริ่มสัปดาห์ที่ราศี{start_positions['moon']['sign_th']} ย้ายไปยังราศี{end_positions['moon']['sign_th']}",
        ]
        retro_planets = [f"{PLANET_NAMES_TH.get(k, k)} (ราศี{v['sign_th']})" for k, v in start_positions.items() if v.get("is_retrograde")]
        if retro_planets:
            summary_lines.append(f"ดาวเคราะห์ที่กำลังโคจรถอยหลัง (Retrograde): {', '.join(retro_planets)}")

        if moon_phases:
            phases_str = ", ".join(f"{p['phase_th']} ({p['date']})" for p in moon_phases)
            summary_lines.append(f"เฟสดวงจันทร์: {phases_str}")

        if aspects:
            aspect_str = "; ".join(a["description_th"] for a in aspects[:5])
            summary_lines.append(f"มุมสัมพันธ์สำคัญ (Major Aspects): {aspect_str}")

        return {
            "week": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "source": "ZodiacEphemerisService (JPL Keplerian / Meeus Astronomical Calculations)",
            "verified": True,
            "calculated_at": datetime.now().astimezone().isoformat(),
            "planetary_positions": start_positions,
            "end_planetary_positions": end_positions,
            "moon_phases": moon_phases,
            "major_aspects": aspects,
            "summary_th": "\n".join(summary_lines),
        }

    @staticmethod
    def _format_body_data(body: str, longitude_deg: float) -> dict:
        norm_lon = longitude_deg % 360.0
        sign_idx = int(norm_lon // 30)
        sign_id, sign_th = ZODIAC_SIGNS[sign_idx]
        deg_in_sign = round(norm_lon % 30.0, 2)

        return {
            "id": body,
            "name_th": PLANET_NAMES_TH.get(body, body),
            "sign": sign_id,
            "sign_th": sign_th,
            "longitude_deg": round(norm_lon, 2),
            "degree_in_sign": deg_in_sign,
            "is_retrograde": False,
        }

    @staticmethod
    def _detect_aspects(positions: dict[str, dict], date_ref: date) -> list[dict]:
        bodies = ("sun", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto")
        aspect_targets = (
            (0, "Conjunction", "กุม (0°)", 4.0),
            (60, "Sextile", "โยค (60°)", 3.0),
            (90, "Square", "จตุโกณ (90°)", 3.5),
            (120, "Trine", "ตรีโกณ (120°)", 3.5),
            (180, "Opposition", "เล็ง (180°)", 4.0),
        )

        detected = []
        for i, b1 in enumerate(bodies):
            for b2 in bodies[i + 1:]:
                lon1 = positions[b1]["longitude_deg"]
                lon2 = positions[b2]["longitude_deg"]
                diff = abs((lon1 - lon2 + 180) % 360 - 180)

                for target_deg, en_name, th_name, max_orb in aspect_targets:
                    orb = abs(diff - target_deg)
                    if orb <= max_orb:
                        detected.append({
                            "planets": [b1, b2],
                            "type": en_name.lower(),
                            "type_th": th_name,
                            "angle_deg": round(diff, 1),
                            "orb_deg": round(orb, 2),
                            "date": date_ref.isoformat(),
                            "description_th": f"{PLANET_NAMES_TH[b1]} {th_name} กับ {PLANET_NAMES_TH[b2]}",
                        })
        return detected

    def _detect_moon_phases(self, start_date: date, end_date: date) -> list[dict]:
        phases = []
        curr = start_date
        prev_elong = None

        while curr <= end_date:
            pos = self.calculate_positions(curr)
            sun_lon = pos["sun"]["longitude_deg"]
            moon_lon = pos["moon"]["longitude_deg"]
            elong = (moon_lon - sun_lon) % 360

            if prev_elong is not None:
                # Check phase crossings
                # New Moon ~0
                if prev_elong > 330 and elong < 30:
                    phases.append({"phase": "new_moon", "phase_th": "จันทร์ดับ (New Moon)", "date": curr.isoformat()})
                # First Quarter ~90
                elif prev_elong < 90 <= elong:
                    phases.append({"phase": "first_quarter", "phase_th": "จันทร์ครึ่งดวงข้างขึ้น (First Quarter)", "date": curr.isoformat()})
                # Full Moon ~180
                elif prev_elong < 180 <= elong:
                    phases.append({"phase": "full_moon", "phase_th": "จันทร์เพ็ญ (Full Moon)", "date": curr.isoformat()})
                # Third Quarter ~270
                elif prev_elong < 270 <= elong:
                    phases.append({"phase": "third_quarter", "phase_th": "จันทร์ครึ่งดวงข้างแรม (Third Quarter)", "date": curr.isoformat()})

            prev_elong = elong
            curr += timedelta(days=1)

        return phases

    @staticmethod
    def _validate_research(research: dict) -> None:
        if not isinstance(research, dict):
            raise AppError("EPHEMERIS_INVALID", "โครงสร้างข้อมูลดาราศาสตร์ไม่ถูกต้อง")
        if not research.get("verified"):
            raise AppError("EPHEMERIS_INVALID", "ข้อมูลดาราศาสตร์ยังไม่ผ่านการยืนยัน")
        positions = research.get("planetary_positions")
        if not isinstance(positions, dict) or len(positions) < 10:
            raise AppError("EPHEMERIS_INVALID", "ตำแหน่งดาวเคราะห์ไม่ครบ 10 ดวงหลัก")
        for key in ("sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"):
            if key not in positions:
                raise AppError("EPHEMERIS_INVALID", f"ไม่พบตำแหน่งดาว {key}")
            body = positions[key]
            if not (0.0 <= body.get("longitude_deg", -1.0) <= 360.0):
                raise AppError("EPHEMERIS_INVALID", f"พิกัดดาว {key} อยู่นอกช่วง 0-360 องศา")
