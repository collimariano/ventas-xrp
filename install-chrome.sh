#!/bin/bash

set -e

echo "🔧 Instalando dependencias..."
apt-get update
apt-get install -y wget curl unzip gnupg2 software-properties-common

echo "🌐 Instalando Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || apt --fix-broken install -y

echo "🔍 Obteniendo versión de Chrome instalada..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

echo "⬇️ Descargando ChromeDriver para versión $CHROME_VERSION..."
DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | grep -A 10 "$CHROME_VERSION" | grep "url" | grep "linux64" | grep "chromedriver-linux64" | grep -o 'https://[^"]*')
wget -q "$DRIVER_VERSION" -O chromedriver.zip
unzip chromedriver.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

echo "✅ ChromeDriver instalado en /usr/local/bin/chromedriver"
