#!/bin/bash

apt-get update
apt-get install -y wget gnupg unzip curl

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

CHROME_VERSION=$(google-chrome --version | grep -oP "\d+\.\d+\.\d+")
DRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | grep -A 10 $CHROME_VERSION | grep "linux64" | grep "url" | cut -d '"' -f4)

mkdir -p /usr/local/bin/chromedriver
curl -sSL $DRIVER_VERSION -o chromedriver.zip
unzip chromedriver.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver
