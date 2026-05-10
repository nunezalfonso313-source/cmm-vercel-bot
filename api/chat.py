import os, json, requests

GROQ_KEY = os.environ.get("GROQ_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def handler(req, res):
    try:
        data = req.body
        message = data.get("message", "")
        system = data.get("system", "Eres instructor técnico de GD&T y CMM. Responde en español.")

        if not GROQ_KEY:
            return res.status(500).json({"response": "Error: GROQ_KEY no configurada en variables de entorno"})

        r = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system}, {"role": "user", "content": message}], "temperature": 0.0},
            timeout=30)

        data_r = r.json()
        if "choices" not in data_r:
            return res.status(500).json({"response": f"Error Groq: {json.dumps(data_r)}"})

        response = data_r["choices"][0]["message"]["content"]
        res.headers["Access-Control-Allow-Origin"] = "*"
        return res.status(200).json({"response": response})

    except Exception as e:
        return res.status(500).json({"response": f"Error: {str(e)}"})
