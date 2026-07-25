"""
server.py — JHA PDF Generator API for Render.com
"""
import json
import os
import smtplib
import tempfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── Allow CORS from GitHub Pages and all origins ──────────────
ALLOWED_ORIGINS = [
    'https://orrodriguez9731-ux.github.io',
    'http://localhost',
    'http://127.0.0.1',
]

def add_cors(response):
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin']  = origin if origin in ALLOWED_ORIGINS else '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response.headers['Access-Control-Max-Age']       = '3600'
    return response

app.after_request(add_cors)

# ── Email credentials ──────────────────────────────────────────
SMTP_USER = "orrodriguez9731@gmail.com"
SMTP_PASS = "xzbp grbw kxix onmc"
TO_EMAIL  = "omarr@dwilsonconstruction.com"

# ── Health check ───────────────────────────────────────────────
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "JHA server running"}), 200

# ── Main endpoint ──────────────────────────────────────────────
@app.route('/submit-jha', methods=['POST', 'OPTIONS'])
def submit_jha():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers['Access-Control-Allow-Origin']  = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response, 200

    try:
        data = request.get_json(force=True)
        if not data:
            print("ERROR: No JSON data received", flush=True)
            return jsonify({"success": False, "error": "No data received"}), 400

        company  = data.get('company',  'Unknown')
        name     = data.get('name',     'Unknown')
        date_str = data.get('date',     'Unknown')
        print(f"Received JHA: {company} / {name} / {date_str}", flush=True)

        # Build the PDF
        print("Building PDF...", flush=True)
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w',
                                         delete=False) as jf:
            json.dump(data, jf)
            json_path = jf.name

        pdf_path = json_path.replace('.json', '.pdf')

        from build_jha_pdf import build
        build(json_path, pdf_path)
        print(f"PDF built: {pdf_path}", flush=True)

        # Email the PDF
        print(f"Sending email to {TO_EMAIL}...", flush=True)
        subject = f"JHA — {company} — {name} — {date_str}"
        msg = MIMEMultipart()
        msg['From']    = SMTP_USER
        msg['To']      = TO_EMAIL
        msg['Subject'] = subject

        body = (
            f"Job Hazard Analysis submitted.\n\n"
            f"Company:  {company}\n"
            f"Foreman:  {name}\n"
            f"Date:     {date_str}\n"
            f"Location: {data.get('location', '')}\n\n"
            f"See attached PDF for the complete filled-out JHA."
        )
        msg.attach(MIMEText(body, 'plain'))

        filename = f"JHA_{company.replace(' ','_')}_{date_str}.pdf"
        with open(pdf_path, 'rb') as pf:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pf.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename="{filename}"')
        msg.attach(part)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())
        print("Email sent successfully!", flush=True)

        # Clean up
        try:
            os.unlink(json_path)
            os.unlink(pdf_path)
        except Exception:
            pass

        return jsonify({"success": True,
                        "message": "PDF emailed successfully"}), 200

    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
