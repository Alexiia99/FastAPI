import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

MONITORING_URL = os.getenv("MONITORING_URL", "http://localhost:8002")
EVIDENTLY_URL = os.getenv("EVIDENTLY_URL", "http://localhost:8001")


def send_drift_notification():
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🌸 Drift detectado en el modelo de Attrition"
    msg["From"] = "monitor@mlops.local"
    msg["To"] = "profesor@mlops.local"

    html = f"""
    <html><body>
    <h2>🌸 Drift detectado en el modelo de Attrition</h2>
    <p>El monitor ha detectado drift en los datos de producción.</p>
    <p><a href="{EVIDENTLY_URL}">Ver dashboard de Evidently</a></p>
    <br>
    <p>¿Quieres reentrenar el modelo con los nuevos datos?</p>
    <br>
    <a href="{MONITORING_URL}/approve-retraining"
       style="background-color:#4CAF50;color:white;padding:12px 24px;
              text-decoration:none;border-radius:5px;font-size:16px">
       🌸 Aprobar reentrenamiento
    </a>
    &nbsp;&nbsp;
    <a href="{MONITORING_URL}/reject-retraining"
       style="background-color:#f44336;color:white;padding:12px 24px;
              text-decoration:none;border-radius:5px;font-size:16px">
       🌸 Rechazar
    </a>
    </body></html>
    """

    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP("mailhog", 1025) as server:
        server.sendmail("monitor@mlops.local", "profesor@mlops.local", msg.as_string())

    print("🌸 Email enviado — ver en http://localhost:8025")