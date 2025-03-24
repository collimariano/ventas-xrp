import os
import re
import shutil
import subprocess
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Variables de entorno
usuario = os.environ["XRP_USUARIO"]
clave = os.environ["XRP_CLAVE"]
telefono = os.environ["CALLMEBOT_PHONE"]
apikey = os.environ["CALLMEBOT_APIKEY"]

# 🔧 Instalación automática de Chrome y ChromeDriver
print("🛠 Instalando Google Chrome y ChromeDriver desde Python...")

subprocess.run(["apt-get", "update"], check=True)
subprocess.run(["apt-get", "install", "-y", "wget", "curl", "unzip", "gnupg2", "software-properties-common"], check=True)

subprocess.run(["wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb"], check=True)
subprocess.run(["apt", "install", "-y", "./google-chrome-stable_current_amd64.deb"], check=True)

chrome_version_output = subprocess.check_output(["google-chrome", "--version"]).decode()
print("📦 Chrome version:", chrome_version_output.strip())

match = re.search(r"(\d+\.\d+\.\d+)", chrome_version_output)
if not match:
    raise Exception("❌ No se pudo obtener la versión de Chrome")
chrome_version = match.group(1)

resp = requests.get("https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json")
data = resp.json()

driver_url = None
for version in data["versions"]:
    if version["version"].startswith(chrome_version):
        for d in version["downloads"]["chromedriver"]:
            if d["platform"] == "linux64":
                driver_url = d["url"]
                break
    if driver_url:
        break

if not driver_url:
    raise Exception("❌ No se encontró una versión de ChromeDriver compatible")

print("📥 Descargando ChromeDriver de:", driver_url)
with open("chromedriver.zip", "wb") as f:
    f.write(requests.get(driver_url).content)

subprocess.run(["unzip", "chromedriver.zip"])
subprocess.run(["mv", "chromedriver-linux64/chromedriver", "/usr/local/bin/chromedriver"])
subprocess.run(["chmod", "+x", "/usr/local/bin/chromedriver"])

print("✅ Chrome y ChromeDriver listos.")

# 🚀 Iniciar Selenium
print("Iniciando sesión con Selenium...")

options = Options()
options.binary_location = "/usr/bin/google-chrome"
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service("/usr/local/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

driver.get("https://account.xrp.net/")
driver.find_element(By.NAME, "txtUsuario").send_keys(usuario)
driver.find_element(By.NAME, "txtClave").send_keys(clave, Keys.RETURN)

driver.implicitly_wait(10)
cookies = driver.get_cookies()
driver.quit()
print("Sesión iniciada y cookies obtenidas.")

# 🌐 Transferir cookies a requests
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie["name"], cookie["value"])
print("Cookies transferidas a la sesión de requests.")

# 📊 Obtener ventas
fecha_hoy = datetime.now().strftime("%d/%m/%Y")
url = "https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros_server.asp"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://svr1.xrp.com.ar",
    "Referer": "https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros.asp",
}
payload = f"__idmatrix=xrp_mtxDatos_1&__bufferpage=500&modulo=5&accion=filter&fecha={fecha_hoy}&idunineg=1"

print("Haciendo request a ventas/cobros...")
response = session.post(url, headers=headers, data=payload)
print("Respuesta recibida.")

matches = re.findall(r'<record[^>]+tipo="Venta"[^>]+denom="(Contado|No Definida)"[^>]+importe="([\d.]+)"', response.text)
print(f"Registros encontrados: {len(matches)}")

total = sum(float(importe) for _, importe in matches)
total_formatted = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
print(f"Total calculado: ${total_formatted}")

# 📤 Enviar mensaje vía CallMeBot
mensaje = f"Fecha: {fecha_hoy}\nVentas: ${total_formatted}"
print("Enviando mensaje vía CallMeBot...")

params = {
    "phone": telefono,
    "text": mensaje,
    "apikey": apikey,
}

res = requests.get("https://api.callmebot.com/whatsapp.php", params=params)

if res.status_code == 200:
    print("✅ Mensaje enviado con éxito.")
else:
    print("❌ Error al enviar el mensaje:", res.text)
