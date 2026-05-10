from http.server import BaseHTTPRequestHandler
import os, json, requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length',0))
            body = json.loads(self.rfile.read(length))
            message = body.get('message','')
            system = body.get('system','Eres instructor técnico de GD&T y CMM. Responde en español.')
            key = os.environ.get('GROQ_KEY','')
            r = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},
                json={'model':'llama-3.1-8b-instant','messages':[{'role':'system','content':system},{'role':'user','content':message}],'temperature':0.0},
                timeout=30)
            resp = r.json()['choices'][0]['message']['content']
            self.send_response(200)
            self.send_header('Content-Type','application/json')
            self.send_header('Access-Control-Allow-Origin','*')
            self.end_headers()
            self.wfile.write(json.dumps({'response':resp}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type','application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response':f'Error: {str(e)}'}).encode())
