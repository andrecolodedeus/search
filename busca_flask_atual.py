from flask import Flask, request, render_template_string
import os
import re

app = Flask(__name__)

# Caminhos para as pastas com os arquivos
PASTAS = {
    "fathers": r"C:\Users\andre\Downloads\newadvent\textos\fathers",
    "library": r"C:\Users\andre\Downloads\newadvent\textos\library",
    "bible": r"C:\Users\andre\Downloads\newadvent\textos\bible",
    "cathen": r"C:\Users\andre\Downloads\newadvent\textos\cathen",
    "douay": r"C:\Users\andre\Downloads\newadvent\textos\douay",
    "summa": r"C:\Users\andre\Downloads\newadvent\textos\summa"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    resultados = []
    termo = ''
    pasta_escolhida = 'all'

    if request.method == 'POST':
        termo = request.form['termo'].strip()
        pasta_escolhida = request.form['pasta']

        if termo:
            pastas_busca = PASTAS.values() if pasta_escolhida == 'all' else [PASTAS[pasta_escolhida]]
            for caminho_pasta in pastas_busca:
                try:
                    for nome_arquivo in os.listdir(caminho_pasta):
                        if nome_arquivo.lower().endswith(('.html', '.htm', '.txt')):
                            caminho_arquivo = os.path.join(caminho_pasta, nome_arquivo)
                            try:
                                with open(caminho_arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                                    conteudo = f.read()

                                if termo.lower() in conteudo.lower():
                                    trecho = extrair_trecho(conteudo, termo)
                                    resumo = gerar_resumo(conteudo)
                                    resultados.append({
                                        'arquivo': nome_arquivo,
                                        'caminho': caminho_arquivo,
                                        'trecho': trecho,
                                        'resumo': resumo
                                    })
                            except Exception as e:
                                print(f"Erro ao ler {nome_arquivo}: {e}")
                except Exception as e:
                    print(f"Erro ao listar arquivos da pasta {caminho_pasta}: {e}")

    return render_template_string(TEMPLATE, resultados=resultados, termo=termo, pastas=PASTAS, pasta_escolhida=pasta_escolhida)

def extrair_trecho(texto, termo):
    padrao = re.compile(r'.{0,100}' + re.escape(termo) + r'.{0,100}', re.IGNORECASE)
    match = padrao.search(texto)
    if match:
        # Destaca todas as ocorrências do termo, ignorando case
        highlighted = re.sub(re.escape(termo), f'<mark>{termo}</mark>', match.group(0), flags=re.IGNORECASE)
        return highlighted
    return ''

def gerar_resumo(texto):
    # Remove tags HTML para um texto limpo
    texto_limpo = re.sub('<[^<]+?>', '', texto)
    # Divide em sentenças simples (aprox.)
    sentencas = re.split(r'(?<=[.!?])\s+', texto_limpo)
    resumo_curto = ' '.join(sentencas[:3])  # primeiras 3 sentenças
    if len(resumo_curto) > 300:
        resumo_curto = resumo_curto[:297] + '...'
    return resumo_curto

TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Busca nos Arquivos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        input[type=text] { width: 300px; padding: 8px; }
        select { padding: 6px; }
        .resultado { margin-bottom: 20px; padding: 10px; border: 1px solid #ccc; border-radius: 8px; }
        mark { background-color: yellow; }
    </style>
</head>
<body>
    <h1>🔍 Busca nos Arquivos</h1>
    <form method="post">
        <input type="text" name="termo" value="{{ termo }}" placeholder="Digite o termo para buscar" required>
        <select name="pasta">
            <option value="all" {% if pasta_escolhida == 'all' %}selected{% endif %}>Todas as pastas</option>
            {% for nome, caminho in pastas.items() %}
                <option value="{{ nome }}" {% if pasta_escolhida == nome %}selected{% endif %}>{{ nome }}</option>
            {% endfor %}
        </select>
        <button type="submit">Buscar</button>
    </form>

    <hr>
    {% for resultado in resultados %}
        <div class="resultado">
            <strong>Arquivo:</strong> 
            <a href="file:///{{ resultado.caminho }}" target="_blank">{{ resultado.arquivo }}</a><br>
            <strong>Trecho:</strong> 
            <div>{{ resultado.trecho|safe }}</div>
            <strong>Resumo:</strong> 
            <div>{{ resultado.resumo|safe }}</div>
        </div>
    {% else %}
        {% if termo %}
            <p>Nenhum resultado encontrado para "<strong>{{ termo }}</strong>".</p>
        {% endif %}
    {% endfor %}
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True)
