"""Private RunPod-side F5 Thai V2 worker; invoked only through SSH stdin/argv."""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

from f5_tts.api import F5TTS


def main() -> None:
    payload = json.loads(base64.urlsafe_b64decode(sys.argv[1]).decode("utf-8"))
    output = Path(payload["output"])
    output.parent.mkdir(parents=True, exist_ok=True)
    tts = F5TTS(
        model="F5TTS_V2_train",
        ckpt_file=payload["checkpoint"],
        vocab_file=payload["vocab"],
        device="cuda",
    )
    tts.infer(
        ref_file=payload["reference"],
        ref_text=payload["reference_text"],
        gen_text=payload["text"],
        nfe_step=32,
        cfg_strength=2.0,
        speed=min(1.0, max(0.9, float(payload["speed"]))),
        file_wave=str(output),
    )
    print(json.dumps({"output": str(output)}))


if __name__ == "__main__":
    main()
