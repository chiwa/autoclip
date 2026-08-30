import json
import zipfile

import pytest

from app.domain.errors import AppError
from app.services.package_service import PackageService


def script(image="images/a.png"):
    return {"project": {"id": "p", "title": "P", "language": "th-TH"}, "voice": {"provider": "dummy", "voice": "test", "speed": 1}, "scenes": [{"id": "s1", "image": image, "narration": "ภาษาไทย", "motion": "none"}]}


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in members.items():
            archive.writestr(name, content)


def test_valid_package(tmp_path):
    package = tmp_path / "p.zip"
    make_zip(package, {"script.json": json.dumps(script(), ensure_ascii=False), "images/a.png": b"png"})
    parsed, bgm = PackageService(10000).extract_and_validate(package, tmp_path / "out")
    assert parsed.scenes[0].narration == "ภาษาไทย"
    assert bgm is None


@pytest.mark.parametrize(("members", "code"), [
    ({"images/a.png": b"x"}, "PACKAGE_INVALID"),
    ({"script.json": b"not-json", "images/a.png": b"x"}, "SCRIPT_JSON_INVALID"),
    ({"script.json": json.dumps(script()), "images/other.png": b"x"}, "ASSET_NOT_FOUND"),
    ({"script.json": json.dumps(script("images/a.gif")), "images/a.gif": b"x"}, "UNSUPPORTED_ASSET_TYPE"),
    ({"../escape": b"x", "script.json": json.dumps(script()), "images/a.png": b"x"}, "ZIP_SECURITY_VIOLATION"),
    ({"bad.sh": b"x", "script.json": json.dumps(script()), "images/a.png": b"x"}, "ZIP_SECURITY_VIOLATION"),
    ({"notes.txt": b"x", "script.json": json.dumps(script()), "images/a.png": b"x"}, "UNSUPPORTED_ASSET_TYPE"),
])
def test_invalid_packages(tmp_path, members, code):
    package = tmp_path / "p.zip"
    make_zip(package, members)
    with pytest.raises(AppError) as caught:
        PackageService(10000).extract_and_validate(package, tmp_path / "out")
    assert caught.value.code == code


def test_extracted_size_limit(tmp_path):
    package = tmp_path / "p.zip"
    make_zip(package, {"script.json": json.dumps(script()), "images/a.png": b"x" * 1000})
    with pytest.raises(AppError) as caught:
        PackageService(100).extract_and_validate(package, tmp_path / "out")
    assert caught.value.code == "UPLOAD_TOO_LARGE"
