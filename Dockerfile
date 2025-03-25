FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    chromium chromium-driver curl unzip gnupg2 \
    libglib2.0-0 libnss3 libgconf-2-4 libxss1 libappindicator3-1 \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/lib/chromium/"

# Exponer el puerto para Flask (Render necesita saberlo)
EXPOSE 10000

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
