FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    libglib2.0-0 libnss3 libgconf-2-4 libxss1 \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 \
    curl unzip gnupg2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
