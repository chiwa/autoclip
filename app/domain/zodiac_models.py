from __future__ import annotations

from datetime import date

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


THAI_MONTHS = ("", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.")


def thai_week_range(start: date, end: date) -> str:
    if end < start:
        raise ValueError("end date precedes start date")
    year = end.year + 543
    if start.month == end.month:
        return f"{start.day} - {end.day} {THAI_MONTHS[end.month]} {year}"
    start_year = start.year + 543
    if start.year == end.year:
        return f"{start.day} {THAI_MONTHS[start.month]} - {end.day} {THAI_MONTHS[end.month]} {year}"
    return f"{start.day} {THAI_MONTHS[start.month]} {start_year} - {end.day} {THAI_MONTHS[end.month]} {year}"


class ZodiacBatchRequest(BaseModel):
    start_date: date
    end_date: date
    tts_provider: str = Field(default="google-gemini", min_length=1, max_length=64)

    @model_validator(mode="after")
    def valid_range(self) -> "ZodiacBatchRequest":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ZodiacReading(BaseModel):
    id: str
    hook: str = Field(min_length=1)
    overview: str | None = None
    work: str = Field(min_length=1)
    finance: str = Field(min_length=1)
    love: str = Field(min_length=1)
    advice: str = Field(min_length=1)
    # Optional means truly optional: never synthesize an implicit outro that
    # was not present in the imported/AI-approved narration JSON.
    closing: str | None = None


class ZodiacWeek(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    start_date: date = Field(validation_alias=AliasChoices("start_date", "startDate"))
    end_date: date = Field(validation_alias=AliasChoices("end_date", "endDate"))
    display_th: str | None = Field(default=None, validation_alias=AliasChoices("display_th", "displayTh"))

    @model_validator(mode="after")
    def valid_range(self) -> "ZodiacWeek":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if not self.display_th or not self.display_th.strip():
            self.display_th = thai_week_range(self.start_date, self.end_date)
        return self


class ZodiacDateOverlay(BaseModel):
    enabled: bool = True
    text_source: str = Field(default="week.display_th", pattern="^week\.display_th$")
    preserve_master_image: bool = True


class ZodiacMotion(BaseModel):
    enabled: bool = False
    preset: str = Field(default="none", pattern="^(none|auto)$")

    @model_validator(mode="after")
    def consistent_motion(self) -> "ZodiacMotion":
        if not self.enabled and self.preset != "none":
            raise ValueError("motion.preset must be none when motion.enabled is false")
        return self


class ZodiacVisual(BaseModel):
    use_template_as_primary_visual: bool = True
    generate_new_images: bool = False
    date_overlay: ZodiacDateOverlay = Field(default_factory=ZodiacDateOverlay)
    motion: ZodiacMotion = Field(default_factory=ZodiacMotion)

    @model_validator(mode="after")
    def supported_visual_mode(self) -> "ZodiacVisual":
        if not self.use_template_as_primary_visual:
            raise ValueError("use_template_as_primary_visual must be true")
        if self.generate_new_images:
            raise ValueError("generate_new_images is not supported for fixed zodiac templates")
        if not self.date_overlay.preserve_master_image:
            raise ValueError("preserve_master_image must be true")
        return self


class ZodiacVoice(BaseModel):
    voice: str = Field(default="Iapetus", min_length=1, max_length=80)
    language: str = Field(default="th-TH", pattern="^th-TH$")
    speed: float = Field(default=1.10, ge=0.5, le=2.0)


class ZodiacBatchImport(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    schema_name: str = Field(default="autoclip.zodiac-weekly-batch.v1", alias="schema")
    week: ZodiacWeek
    zodiacs: list[ZodiacReading] = Field(default_factory=list)
    tts_provider: str = "google-gemini"
    visual: ZodiacVisual = Field(default_factory=ZodiacVisual)
    voice: ZodiacVoice = Field(default_factory=ZodiacVoice)
    curator: dict | None = None
    channel_id: str = Field(default="undefined", validation_alias=AliasChoices("channel_id", "channelId"))

    @model_validator(mode="after")
    def valid_batch(self) -> "ZodiacBatchImport":
        if self.zodiacs:
            ids = [item.id for item in self.zodiacs]
            expected = {
                "capricorn", "aquarius", "pisces", "aries", "taurus", "gemini",
                "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius",
            }
            if len(ids) != 12 or len(set(ids)) != 12 or set(ids) != expected:
                raise ValueError("zodiacs must contain all 12 unique zodiac ids")
        return self

    @property
    def start_date(self) -> date:
        return self.week.start_date

    @property
    def end_date(self) -> date:
        return self.week.end_date


class ZodiacMetadataUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    description: str = Field(min_length=1, max_length=5000)
    hashtags: list[str] = Field(min_length=1, max_length=8)
    tags: list[str] = Field(min_length=1, max_length=20)
    visibility: str = Field(default="private", pattern="^(private|unlisted|public)$")


class ZodiacDefinition(BaseModel):
    id: str
    order: int
    name_th: str
    name_en: str
    birth_range_th: str
    template: str
