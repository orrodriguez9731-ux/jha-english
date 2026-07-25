"""
server.py — JHA PDF Generator API for Render.com
Uses SendGrid HTTPS API to send email (avoids Render's SMTP port block)
"""
import json
import os
import base64
import tempfile
import urllib.request
import urllib.error
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── CORS ──────────────────────────────────────────────────────
def add_cors(response):
    response.headers['Access-Control-Allow-Origin']  = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Accept'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

app.after_request(add_cors)

# ── Credentials ────────────────────────────────────────────────
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')
FROM_EMAIL       = 'orrodriguez9731@gmail.com'
FROM_NAME        = 'D. Wilson Construction JHA'
TO_EMAIL         = 'omarr@dwilsonconstruction.com'

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

        # ── Build the PDF ──────────────────────────────────────
        print("Building PDF...", flush=True)
        with tempfile.NamedTemporaryFile(suffix='.json', mode='w',
                                         delete=False) as jf:
            json.dump(data, jf)
            json_path = jf.name

        pdf_path = json_path.replace('.json', '.pdf')
        from build_jha_pdf import build
        build(json_path, pdf_path)
        print(f"PDF built: {pdf_path}", flush=True)

        # ── Read PDF as base64 for SendGrid attachment ─────────
        with open(pdf_path, 'rb') as pf:
            pdf_b64 = base64.b64encode(pf.read()).decode('utf-8')

        filename = f"JHA_{company.replace(' ','_')}_{date_str}.pdf"

        # ── Send via SendGrid HTTPS API ────────────────────────
        print("Sending email via SendGrid...", flush=True)
        subject = f"JHA — {company} — {name} — {date_str}"
        body_text = (
            f"Job Hazard Analysis submitted.\n\n"
            f"Company:  {company}\n"
            f"Foreman:  {name}\n"
            f"Date:     {date_str}\n"
            f"Location: {data.get('location', '')}\n\n"
            f"See attached PDF for the complete filled-out JHA."
        )

        payload = json.dumps({
            "personalizations": [{"to": [{"email": TO_EMAIL}]}],
            "from": {"email": FROM_EMAIL, "name": FROM_NAME},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body_text}],
            "attachments": [{
                "content":     pdf_b64,
                "type":        "application/pdf",
                "filename":    filename,
                "disposition": "attachment"
            }]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.sendgrid.com/v3/mail/send',
            data=payload,
            headers={
                'Authorization': f'Bearer {SENDGRID_API_KEY}',
                'Content-Type':  'application/json'
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
            print(f"SendGrid response: {status}", flush=True)

        # Clean up temp files
        try:
            os.unlink(json_path)
            os.unlink(pdf_path)
        except Exception:
            pass

        print("Email sent successfully!", flush=True)
        return jsonify({"success": True,
                        "message": "PDF emailed successfully"}), 200

    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        print(f"SendGrid error {e.code}: {err_body}", flush=True)
        return jsonify({"success": False,
                        "error": f"Email error {e.code}: {err_body}"}), 500
    except Exception as e:
        print(f"ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
