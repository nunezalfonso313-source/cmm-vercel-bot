import os
import json
import requests
from http.server import BaseHTTPRequestHandler

GROQ_KEY = os.environ.get("GROQ_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            message = data.get("message", "")
            system = data.get("system", "Eres un instructor técnico de GD&T y CMM.")

            payload = {
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.0
            }
            headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
            r = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
            response = r.json()["choices"][0]["message"]["content"]

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"response": response}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"response": f"Error: {str(e)}"}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
