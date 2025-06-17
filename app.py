from flask import Flask, request, jsonify
from newspaper import Article
import openai
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite acesso do frontend hospedado externamente (GitHub Pages)

# Sua chave da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/resumir", methods=["POST"])
def resumir():
    data = request.get_json()
    url = data.get("url")

    try:
        artigo = Article(url)
        artigo.download()
        artigo.parse()
        texto = artigo.text
    except:
        return jsonify({"resumo": "Erro ao extrair o conteúdo do link."})

    prompt = f"""Resuma o texto abaixo de forma clara, lógica e cronológica, numerando os pontos principais:
    
    {texto}
    """

    resposta = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    resumo = resposta['choices'][0]['message']['content']
    return jsonify({"resumo": resumo})

if __name__ == "__main__":
    app.run(debug=True)