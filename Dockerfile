FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 AUTOCLIP_CONFIG=/app/config.yaml
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl git fonts-noto-core fonts-thai-tlwg && rm -rf /var/lib/apt/lists/* \
    && ffmpeg -version >/dev/null && ffprobe -version >/dev/null
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ARG INSTALL_THONBURIAN=0
COPY requirements-thonburian.txt constraints-thonburian.txt ./
RUN if [ "$INSTALL_THONBURIAN" = "1" ]; then \
      pip install --no-cache-dir -c constraints-thonburian.txt -r requirements-thonburian.txt; \
      git clone --depth 1 https://github.com/biodatlab/thonburian-tts.git /tmp/thonburian-src; \
      cp -r /tmp/thonburian-src/flowtts /usr/local/lib/python3.12/site-packages/flowtts; \
      rm -rf /tmp/thonburian-src; \
    fi
ARG INSTALL_BIRD=1
COPY requirements-bird.txt ./
RUN if [ "$INSTALL_BIRD" = "1" ]; then pip install --no-cache-dir -r requirements-bird.txt; fi
COPY scripts/warm_tts_models.py /app/scripts/warm_tts_models.py
RUN mkdir -p /app/workspaces /app/voices && python scripts/warm_tts_models.py
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
