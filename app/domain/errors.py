from __future__ import annotations

from typing import Any


class AppError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def public_error(error: AppError) -> dict[str, Any]:
    result: dict[str, Any] = {"code": error.code, "message": error.message}
    if error.details:
        result["details"] = error.details
    return result

