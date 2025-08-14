import psycopg2
import psycopg2.extras
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

# ========================
# DATABASE CONNECTION
# ========================
conn_params = {
    "host": "dpg-d1l8cgre5dus73fcn8mg-a.frankfurt-postgres.render.com",
    "port": 5432,
    "dbname": "flask_coets_db_0qzt",
    "user": "flask_coets_db_0qzt_user",
    "password": "vx9DALf0LaxT4bRKpsA2GssaxSA8sN16",
    "sslmode": "require"
}

# ========================
# EMAIL SETTINGS
# ========================
SMTP_SERVER = "smtp-1and1.live.any.po.server.lan"     # For IONOS France
SMTP_PORT = 587                   # STARTTLS port
SMTP_USER = "mp1046780269-1744043653745"
SMTP_PASSWORD = "Bounces&Rebonds2025"
EMAIL_FROM = "johann.harscoet@bouncymedia.com"
EMAIL_TO = "jharscoet@gmail.com"
EMAIL_SUBJECT = "NWSL Appended Table Results"

# ========================
# HTML TEMPLATE
# ========================
html_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; background: #f9f9f9; color: #222; }
    h2 { text-align: center; color: #444; }
    table { border-collapse: collapse; width: 100%; background: white; }
    th, td { border: 1px solid #ccc; padding: 8px 12px; text-align: left; }
    th { background-color: #d60000; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    a { color: #d60000; text-decoration: none; }
  </style>
</head>
<body>

<h2>Table: nwsl_appended</h2>

{% if rows %}
<table>
  <thead>
    <tr>
      {% for col in columns %}
        <th>{{ col }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for row in rows %}
      <tr>
        {% for col in columns %}
          {% if col|lower == "link" %}
            <td>
              {% if row[col] %}
                <a href="{{ row[col] }}" target="_blank">{{ row[col] }}</a>
              {% endif %}
            </td>
          {% else %}
            <td>{{ row[col] }}</td>
          {% endif %}
        {% endfor %}
      </tr>
    {% endfor %}
  </tbody>
</table>
{% else %}
  <p>Aucun enregistrement trouvé.</p>
{% endif %}

</body>
</html>
"""

def fetch_data():
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute('SELECT * FROM "nwsl_appended";')
    rows = cur.fetchall()
    columns = list(rows[0].keys()) if rows else []
    cur.close()
    conn.close()
    return rows, columns

def send_email(html_content):
    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = EMAIL_SUBJECT

    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

if __name__ == "__main__":
    rows, columns = fetch_data()
    template = Template(html_template)
    html_content = template.render(rows=rows, columns=columns)
    send_email(html_content)
    print("Email sent successfully!")
