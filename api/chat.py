import json
import requests

GROQ_KEY = "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"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def handler(request):
    try:
        data = request.json()
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
        
        return {"statusCode": 200, "body": json.dumps({"response": response}), "headers": {"Content-Type": "application/json"}}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"response": f"Error: {str(e)})"}), "headers": {"Content-Type": "application/json"}}
