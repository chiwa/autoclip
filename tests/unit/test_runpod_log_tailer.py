from app.services.wan_service import RunpodComfyLogTailer


def test_comfy_log_tailer_removes_terminal_codes_and_keeps_latest_progress():
    raw = "\x1b[32m[INFO]\x1b[0m loading\r 64%|######4 | 16/25 [01:53<01:05, 7.30s/it]\n"

    assert RunpodComfyLogTailer._sanitize(raw) == "64%|######4 | 16/25 [01:53<01:05, 7.30s/it]"


def test_comfy_log_tailer_redacts_secret_values():
    assert RunpodComfyLogTailer._sanitize("token=abc123\n") == "token=[redacted]"
