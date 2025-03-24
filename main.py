import os
import re
import shutil
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import os

# DEBUG: forzar ejecución del .sh desde el script (sin sudo ni apt-get dentro del .py)
if os.path.exists("./install-chrome.sh"):
    print("🧪 Ejecutando install-chrome.sh desde main.py...")
    subprocess.run(["chmod", "+x", "./install-chrome.sh"], check=True)
    subprocess.run(["./install-chrome.sh"], check=True)
else:
    print("⚠️ No se encontró install-chrome.sh")


# Variables de entorno
usuario = os.environ["XRP_USUARIO"]
clave = os.environ["XRP_CLAVE"]
telefono = os.environ["CALLMEBOT_PHONE"]
apikey = os.environ["CALLMEBOT_APIKEY"]

# Configuración de Chrome
chrome_path = shutil.which("google-chrome") or "/usr/bin/google-chrome"
driver_path = shutil.which("chromedriver") or "/usr/local/bin/chromedriver"

options = Options()
options.binary_location = chrome_path
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(driver_path)

print("Iniciando sesión con Selenium...")
driver = webdriver.Chrome(service=service, options=options)
driver.get("https://account.xrp.net/")

driver.find_element(By.NAME, "txtUsuario").send_keys(usuario)
driver.find_element(By.NAME, "txtClave").send_keys(clave, Keys.RETURN)

driver.implicitly_wait(10)
cookies = driver.get_cookies()
driver.quit()
print("Sesión iniciada y cookies obtenidas.")

# Transferir cookies a requests
session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie["name"], cookie["value"])
print("Cookies transferidas a la sesión de requests.")

# Hacer request a ventas
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

matches = re.findall(
    r'<record[^>]+tipo="Venta"[^>]+denom="(Contado|No Definida)"[^>]+importe="([\d.]+)"',
    response.text,
)
print(f"Registros encontrados: {len(matches)}")

total = sum(float(importe) for _, importe in matches)
total_formatted = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
print(f"Total calculado: ${total_formatted}")

# Enviar por WhatsApp
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
