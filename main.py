from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import requests
import re
import os

app = Flask(__name__)

@app.route("/")
def run_script():
    usuario = os.environ["XRP_USUARIO"]
    clave = os.environ["XRP_CLAVE"]
    telefono = os.environ["CALLMEBOT_PHONE"]
    apikey = os.environ["CALLMEBOT_APIKEY"]

    options = Options()
    options.binary_location = "/usr/bin/chromium"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://account.xrp.net/")
        driver.find_element(By.NAME, "txtUsuario").send_keys(usuario)
        driver.find_element(By.NAME, "txtClave").send_keys(clave, Keys.RETURN)
        driver.implicitly_wait(10)
        cookies = driver.get_cookies()
        driver.quit()
    except Exception as e:
        driver.quit()
        return f"❌ Error en Selenium: {str(e)}"

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

    return "✅ Mensaje enviado" if res.status_code == 200 else f"❌ Error al enviar mensaje: {res.text}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
