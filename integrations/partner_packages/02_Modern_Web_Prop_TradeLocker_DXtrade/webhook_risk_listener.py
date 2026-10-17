#!/usr/bin/env python3
"""
XPredictor Institutional Webhook Risk Listener
Turnkey receiver for TradeLocker, DXtrade, and proprietary prop firm CRM dashboards.
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class XPredictorWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data.decode('utf-8'))
            print("\n[XPREDICTOR WEBHOOK RECEIVED]")
            print(f"Partner Key:   {payload.get('partner_key')}")
            print(f"Event Type:    {payload.get('event_type')}")
            print(f"Asset / TF:    {payload.get('asset')} ({payload.get('timeframe').upper()})")
            print(f"Current Price: ${payload.get('current_price')}")
            
            cone = payload.get('bayesian_cone', {})
            print(f"P90 (+2.1 sigma): ${cone.get('p90_upper_level')}")
            print(f"Mean E[P]:        ${cone.get('p50_mean_target')}")
            print(f"P10 (-2.1 sigma): ${cone.get('p10_lower_level')}")
            print(f"Confidence:       {cone.get('confidence_score')}%")
            print(f"Advisory:         {payload.get('risk_advisory')}\n")

            # Return HTTP 200 Success ACK
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "success", "event_id": payload.get("event_id"), "ack": True}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            err_resp = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(err_resp).encode('utf-8'))

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>XPredictor Risk Webhook Service Active</h1><p>Send POST notifications with JSON payload.</p>")

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, XPredictorWebhookHandler)
    print(f"[*] XPredictor Webhook Listener running on http://localhost:{port}")
    print("[*] Ready to receive risk alerts from XPredictor Reality Cone engine...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down webhook server.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
