import requests
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import re
import os

load_dotenv()

def login_xrp(user, password) -> None:
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
        "req": [user, password],
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
    
    return session, sid, psid

def get_total(session):
    fecha = datetime.now().strftime('%d/%m/%Y')
    url = "https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros_server.asp"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://svr1.xrp.com.ar',
        'Referer': 'https://svr1.xrp.com.ar/hmarket6/reportes/rendicion_ventas_cobros.asp',
    }
    payload = f'__idmatrix=xrp_mtxDatos_1&__bufferpage=500&modulo=5&accion=filter&fecha={fecha}&idunineg=1'

    response = session.post(url, headers=headers, data=payload)
    matches = re.findall(r'<record[^>]+tipo="Venta"[^>]+denom="(Contado|No Definida)"[^>]+importe="([\d.]+)"', response.text)
    total = sum(float(importe) for _, importe in matches)
    return total

def format_total(monto):
    return f"{monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def enviar_email(asunto, cuerpo_html):
    remitente = os.environ["EMAIL_USER"]
    contraseña = os.environ["EMAIL_PASSWORD"]
    
    # Lista de destinatarios separados por coma en .env
    destinatarios = os.environ["EMAIL_DESTINATARIOS"].split(",")  # Ej: "correo1@gmail.com,correo2@gmail.com"
    
    msg = MIMEText(cuerpo_html, "html")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = ", ".join(destinatarios)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(remitente, contraseña)
        server.send_message(msg)

def generar_html(total_formateado):
    fecha = datetime.now().strftime('%d/%m/%Y')
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 30px;">
            <h2 style="color: #4CAF50;">📈 Reporte de Ventas - {fecha}</h2>
            <p style="font-size: 18px;">Hola! 👋</p>
            <p>El total de ventas del día es:</p>
            <h1 style="font-size: 32px; color: #2196F3;">💵 ${total_formateado}</h1>
            <hr style="margin: 20px 0;">
        </div>
    </body>
    </html>
    """

def main():
    usuario = os.environ["XRP_USUARIO"]
    clave = os.environ["XRP_CLAVE"]

    print("🔐 Logging in...")
    session, sid, psid = login_xrp(usuario, clave)
    
    print("📊 Loading total...")
    total = get_total(session)
    total_formateado = format_total(total)

    print(f"✅ Total: ${total_formateado}")

    cuerpo_html = generar_html(total_formateado)
    enviar_email("📬 Reporte de Ventas Diario - XRP", cuerpo_html)
    print("📬 Email enviado a todos los destinatarios.")


if __name__ == "__main__":
    main()