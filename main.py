from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import requests
import re
import os

usuario = os.environ["XRP_USUARIO"]
clave = os.environ["XRP_CLAVE"]
telefono = os.environ["CALLMEBOT_PHONE"]
apikey = os.environ["CALLMEBOT_APIKEY"]

options = Options()
options.binary_location = "/usr/bin/chromium"
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://account.xrp.net/")

driver.find_element(By.NAME, "txtUsuario").send_keys(usuario)
driver.find_element(By.NAME, "txtClave").send_keys(clave, Keys.RETURN)

driver.implicitly_wait(10)
cookies = driver.get_cookies()
driver.quit()

session = requests.Session()
for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])

fecha_hoy = datetime.now().strftime('%d/%m/%Y')
url = "https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros_server.asp"
headers = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://svr1.xrp.com.ar',
    'Referer': 'https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros.asp',
}
payload = f'__idmatrix=xrp_mtxDatos_1&__bufferpage=500&modulo=5&accion=filter&fecha={fecha_hoy}&idunineg=1'

response = session.post(url, headers=headers, data=payload)

matches = re.findall(r'<record[^>]+tipo="Venta"[^>]+denom="(Contado|No Definida)"[^>]+importe="([\d.]+)"', response.text)
total = sum(float(importe) for _, importe in matches)
total_formatted = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

mensaje = f"Fecha: {fecha_hoy}\nVentas: ${total_formatted}"
params = {
    'phone': telefono,
    'text': mensaje,
    'apikey': apikey
}

res = requests.get("https://api.callmebot.com/whatsapp.php", params=params)
