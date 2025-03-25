FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Instalar Chromium y ChromeDriver
RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    libglib2.0-0 libnss3 libgconf-2-4 libxss1 \
    libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libgtk-3-0 \
    curl unzip gnupg2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear symlink para que el binario esté donde Selenium lo espera
RUN ln -s /usr/lib/chromium/chromedriver /usr/bin/chromedriver || true

# Variables de entorno
ENV CHROME_BIN=/usr/bin/chromium
ENV PATH="${PATH}:/usr/bin"

# Crear carpeta de trabajo
WORKDIR /app
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
