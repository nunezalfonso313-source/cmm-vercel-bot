import requests
import telebot
import datetime
import subprocess
import json

TOKEN = "8708246294:AAFPvEOyPp_CBE_9wFLWkjb6gvoPzFGgk1Q"
GROQ_KEY = "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"

SISTEMA = """Eres AlfIA, un asistente de inteligencia artificial creado por Alfonso desde un teléfono Android con Termux. Respondes siempre en español. Eres directo, inteligente y un poco sarcástico pero siempre útil. Cuando alguien te pregunta quién te creó, dices que fue Alfonso.

Tienes acceso a herramientas. Cuando necesites usarlas responde EXACTAMENTE en este formato JSON y nada más:
{"tool": "nombre_herramienta", "input": "parametro"}

Herramientas disponibles:
- calcular: ejecuta expresiones matemáticas. input: expresión matemática
- fecha_hora: obtiene fecha y hora actual. input: ""
- wikipedia: busca en wikipedia. input: término a buscar
- clima: consulta el clima de una ciudad. input: nombre de ciudad
- noticias: busca noticias recientes. input: tema a buscar
- escribir_archivo: escribe contenido en un archivo. input: {"nombre": "archivo.txt", "contenido": "texto"}
- leer_archivo: lee un archivo. input: nombre del archivo

Si no necesitas herramientas responde normalmente."""

bot = telebot.TeleBot(TOKEN)
historial = {}

# ===== HERRAMIENTAS =====

def calcular(expresion):
    try:
        resultado = eval(expresion, {"__builtins__": {}}, {})
        return f"Resultado: {resultado}"
    except Exception as e:
        return f"Error en cálculo: {str(e)}"

def fecha_hora(_):
    now = datetime.datetime.now()
    return f"Fecha y hora actual: {now.strftime('%d/%m/%Y %H:%M:%S')}"

def buscar_wikipedia(termino):
    try:
        url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{termino.replace(' ', '_')}"
        r = requests.get(url, timeout=10)
        data = r.json()
        if "extract" in data:
            return data["extract"][:500]
        return "No encontré información en Wikipedia."
    except Exception as e:
        return f"Error buscando en Wikipedia: {str(e)}"

def consultar_clima(ciudad):
    try:
        url = f"https://wttr.in/{ciudad.replace(' ', '+')}?format=3"
        r = requests.get(url, timeout=10)
        return r.text
    except Exception as e:
        return f"Error consultando clima: {str(e)}"

def buscar_noticias(tema):
    try:
        url = f"https://news.google.com/rss/search?q={tema.replace(' ', '+')}&hl=es&gl=MX&ceid=MX:es"
        r = requests.get(url, timeout=10)
        import re
        titulos = re.findall(r'<title>(.*?)</title>', r.text)[1:6]
        if titulos:
            return "Noticias recientes:\n" + "\n".join(f"- {t}" for t in titulos)
        return "No encontré noticias."
    except Exception as e:
        return f"Error buscando noticias: {str(e)}"

def escribir_archivo(params):
    try:
        if isinstance(params, str):
            params = json.loads(params)
        nombre = params["nombre"]
        contenido = params["contenido"]
        with open(nombre, "w") as f:
            f.write(contenido)
        return f"Archivo '{nombre}' guardado correctamente."
    except Exception as e:
        return f"Error escribiendo archivo: {str(e)}"

def leer_archivo(nombre):
    try:
        with open(nombre, "r") as f:
            return f.read()
    except Exception as e:
        return f"Error leyendo archivo: {str(e)}"

HERRAMIENTAS = {
    "calcular": calcular,
    "fecha_hora": fecha_hora,
    "wikipedia": buscar_wikipedia,
    "clima": consultar_clima,
    "noticias": buscar_noticias,
    "escribir_archivo": escribir_archivo,
    "leer_archivo": leer_archivo
}

# ===== GROQ =====

def llamar_groq(mensajes):
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": mensajes
    }
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    return r.json()["choices"][0]["message"]["content"]

def preguntar_groq(user_id, mensaje):
    try:
        if user_id not in historial:
            historial[user_id] = []

        historial[user_id].append({"role": "user", "content": mensaje})
        mensajes = [{"role": "system", "content": SISTEMA}] + historial[user_id]

        respuesta = llamar_groq(mensajes)

        # detectar si quiere usar herramienta
        try:
            respuesta_limpia = respuesta.strip()
            if respuesta_limpia.startswith("{") and "tool" in respuesta_limpia:
                tool_call = json.loads(respuesta_limpia)
                tool_name = tool_call.get("tool")
                tool_input = tool_call.get("input", "")

                if tool_name in HERRAMIENTAS:
                    resultado_tool = HERRAMIENTAS[tool_name](tool_input)

                    historial[user_id].append({"role": "assistant", "content": respuesta})
                    historial[user_id].append({"role": "user", "content": f"Resultado de la herramienta {tool_name}: {resultado_tool}"})

                    mensajes2 = [{"role": "system", "content": SISTEMA}] + historial[user_id]
                    respuesta_final = llamar_groq(mensajes2)

                    historial[user_id].append({"role": "assistant", "content": respuesta_final})

                    if len(historial[user_id]) > 30:
                        historial[user_id] = historial[user_id][-30:]

                    return respuesta_final
        except:
            pass

        historial[user_id].append({"role": "assistant", "content": respuesta})

        if len(historial[user_id]) > 30:
            historial[user_id] = historial[user_id][-30:]

        return respuesta

    except Exception as e:
        return f"Error: {str(e)}"

# ===== BOT =====

@bot.message_handler(func=lambda m: True)
def responder(message):
    try:
        bot.send_message(message.chat.id, "Pensando...")
        respuesta = preguntar_groq(message.from_user.id, message.text)
        bot.send_message(message.chat.id, respuesta)
    except Exception as e:
        print(f"Error: {e}")

print("AlfIA Agente iniciado...")
bot.polling(none_stop=True)
