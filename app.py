from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from services.agent import SalesforceAgent

load_dotenv()

app = Flask(__name__)
CORS(app) 

bot = SalesforceAgent()

print("\n--- 🚀 SERVIDOR RODANDO (LOCAL) ---")

@app.route("/chat_web", methods=["POST"])
def chat_website():
    try:
        dados = request.get_json()
        texto = dados.get("message")
        
        print(f"👤 Site: {texto}")
        
        resposta = bot.pensar(texto)
        
        print(f"🤖 Bot: {resposta}")
        return jsonify({"response": resposta})

    except Exception as e:
        print(f"❌ Erro: {e}")
        return jsonify({"response": "Erro no servidor."}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)