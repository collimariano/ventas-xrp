#!/bin/bash

apt-get update
apt-get install -y wget curl unzip gnupg2 software-properties-common

# Instalar Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || apt --fix-broken install -y

# Instalar ChromeDriver correspondiente
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | grep -A 10 $CHROME_VERSION | grep "url" | grep "linux64" | grep -o 'https://[^"]*')
wget "$DRIVER_VERSION" -O chromedriver.zip
unzip chromedriver.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
