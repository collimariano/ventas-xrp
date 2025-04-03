import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from dotenv import load_dotenv
import re
import os

load_dotenv()

usuario = os.environ["XRP_USUARIO"]
clave = os.environ["XRP_CLAVE"]

session = requests.Session()

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://account.xrp.com.ar",
    "Referer": "https://account.xrp.com.ar/",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
    "xrp-application-id": "6463ce5794dbd60533c2bf36c057f38c5db15858a8371b8327abcaf6efc7b04bdea2c78c9388f1ad7b7761f8f3853c5a5fdfa42c3ebf1faf269c518b440b17ce"
}

payload = {
    "req": [usuario, clave],
    "remember": 0
}

response = session.post("https://account.xrp.com.ar/login/", headers=headers, json=payload)
data = response.json()["data"]

login_url = data["url"]
parsed = urlparse(login_url)
qs = parse_qs(parsed.query)
sid = qs.get("sid", [""])[0]
psid = qs.get("psid", [""])[0]

session.cookies.set("ssid_xrp", session.cookies.get("ssid_xrp"), domain="svr1.xrp.com.ar", path="/")
session.cookies.set("_sid", sid, domain="svr1.xrp.com.ar", path="/")
session.cookies.set("_psid", psid, domain="svr1.xrp.com.ar", path="/")

fecha_hoy = datetime.now().strftime('%d/%m/%Y')
url = "https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros_server.asp"
headers_post = {
    'User-Agent': 'Mozilla/5.0',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://svr1.xrp.com.ar',
    'Referer': 'https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros.asp',
}
payload_post = f'__idmatrix=xrp_mtxDatos_1&__bufferpage=500&modulo=5&accion=filter&fecha={fecha_hoy}&idunineg=1'

ventas_response = session.post(url, headers=headers_post, data=payload_post)
matches = re.findall(r'<record[^>]+tipo="Venta"[^>]+denom="(Contado|No Definida)"[^>]+importe="([\d.]+)"', ventas_response.text)
total = sum(float(importe) for _, importe in matches)
total_formatted = f"{total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

print(f"✅ Total ventas: ${total_formatted}")
