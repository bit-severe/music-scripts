FROM python:3.12

WORKDIR /app

RUN apt update && apt install -y \
    python3-venv \
    supercollider \
    ffmpeg \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip && pip install -r requirements.txt

VOLUME ["/mnt/audio"]

CMD ["python"]
