from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.domain.models import Script


@dataclass(frozen=True)
class ReelWarning:
    code: str
    message: str
    scene_id: str | None = None
    details: dict[str, float | int | str] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ReelQualityResult:
    total_duration: float
    warnings: list[ReelWarning]


class ReelQualityValidator:
    """Non-blocking retention checks for vertical short-form projects."""

    def __init__(self, *, max_duration: float = 60.0, max_static_scene: float = 6.0, max_hook_scene: float = 5.0, max_average_refresh: float = 6.0):
        self.max_duration = max_duration
        self.max_static_scene = max_static_scene
        self.max_hook_scene = max_hook_scene
        self.max_average_refresh = max_average_refresh

    @staticmethod
    def is_vertical(script: Script) -> bool:
        width, height = (int(value) for value in script.project.resolution.split("x", 1))
        return height > width

    @staticmethod
    def _effective_total(durations: list[float], transitions: list[str], transition_seconds: float) -> float:
        overlap = sum(transition_seconds for transition in transitions if transition != "none")
        return max(0.0, sum(durations) - overlap)

    def evaluate(self, script: Script, durations: list[float], transitions: list[str] | None = None, transition_seconds: float = 0.0) -> ReelQualityResult:
        if not self.is_vertical(script):
            return ReelQualityResult(sum(durations), [])

        transitions = transitions or []
        total = self._effective_total(durations, transitions, transition_seconds)
        warnings: list[ReelWarning] = []
        if total > self.max_duration:
            warnings.append(ReelWarning("REEL_DURATION_LONG", f"Reel duration is {total:.1f}s; target 45–55s and keep under 60s when possible.", details={"durationSeconds": round(total, 3)}))

        for index, (scene, duration) in enumerate(zip(script.scenes, durations)):
            is_outro = scene.role == "outro" or "outro" in scene.id.lower()
            if duration > self.max_static_scene and scene.motion == "none" and not is_outro:
                warnings.append(ReelWarning("SCENE_VISUAL_TOO_LONG", f"Scene uses one static visual for {duration:.1f}s without motion.", scene.id, {"durationSeconds": round(duration, 3)}))
            is_hook = scene.role == "hook" or (index == 0 and not any(item.role == "hook" for item in script.scenes))
            if is_hook and duration > self.max_hook_scene:
                warnings.append(ReelWarning("HOOK_SCENE_TOO_LONG", f"Hook scene lasts {duration:.1f}s; reach the first payoff within about 3–5s.", scene.id, {"durationSeconds": round(duration, 3)}))

        scene_count = len(script.scenes)
        average_refresh = total / scene_count
        if total >= 45.0 and (scene_count <= 5 or average_refresh > self.max_average_refresh):
            warnings.append(ReelWarning("LOW_VISUAL_REFRESH_RATE", f"{scene_count} visual sources across {total:.1f}s averages {average_refresh:.1f}s per visual; consider splitting the script into more scenes.", details={"sceneCount": scene_count, "averageSecondsPerVisual": round(average_refresh, 3)}))
        return ReelQualityResult(total, warnings)
