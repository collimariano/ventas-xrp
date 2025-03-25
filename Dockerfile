FROM python:3.11-slim

# Instalar dependencias necesarias para Chrome
RUN apt-get update && \
    apt-get install -y wget curl unzip gnupg2 software-properties-common \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 \
    libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 \
    libxdamage1 libxrandr2 xdg-utils

# Instalar Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb || apt --fix-broken install -y

# Instalar ChromeDriver compatible
# Obtener versión de Chrome instalada
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    echo "🔍 Versión completa de Chrome: $CHROME_VERSION" && \
    echo "$CHROME_VERSION" > /tmp/chrome_version.txt

# Descargar JSON de versiones de ChromeDriver y extraer URL
# Descargar JSON de versiones y extraer URL del ChromeDriver correspondiente
RUN CHROME_VERSION=$(cat /tmp/chrome_version.txt) && \
    curl -s https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json -o versions.json && \
    grep -A 10 "\"version\": \"$CHROME_VERSION\"" versions.json > chunk.json && \
    grep "url" chunk.json | grep "linux64" | grep "chromedriver-linux64" | grep -o 'https://[^"]*' > /tmp/driver_url.txt


# Descargar y configurar ChromeDriver
RUN DRIVER_URL=$(cat /tmp/driver_url.txt) && \
    wget "$DRIVER_URL" -O chromedriver.zip && \
    unzip chromedriver.zip && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver


# Crear carpeta de trabajo y copiar archivos
WORKDIR /app
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando de inicio
CMD ["python", "main.py"]
