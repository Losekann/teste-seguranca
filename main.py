### CORRIGIDO AS FALHAS APONTADAS NO RELATORIO

import sqlite3
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.middleware("http")
async def adicionar_cabecalhos_seguranca(request: Request, call_next):
    response = await call_next(request)

    ## Proteção contra Cache (Informacional)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    # Anti-clickjacking e Anti-MIME-Sniffing
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Content Security Policy e Permissions Policy
    # form-action 'self' garante que formulários só enviem dados para a própria origem
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "frame-ancestors 'none'; "
        "form-action 'self'"
    )

    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # Proteções Cross-Origin
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

    return response

def init_db():
    conn = sqlite3.connect("universidade.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS alunos (id INTEGER, nome TEXT, nota REAL, segredo TEXT)")
    cursor.execute("DELETE FROM alunos")
    cursor.execute("INSERT INTO alunos VALUES (1, 'Ana', 9.5, 'SenhaAdmin123')")
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
def index(busca: str = Query(default="")):
    html_content = f"""
    <html>
        <body>
            <h1>Portal de Notas</h1>
            <p>Você buscou por: <b>{busca}</b></p>
            <form method="GET" action="/buscar">
                <input type="text" name="aluno" placeholder="Nome do aluno">
                <button type="submit">Buscar Notas</button>
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/buscar")
def buscar_aluno(aluno: str):
    conn = sqlite3.connect("universidade.db")
    cursor = conn.cursor()

    # CORREÇÃO DO SQL INJECTION
    # 1. Removemos a f-string.
    # 2. Substituímos a variável diretamente na string por um placeholder '?'.
    # Em bancos de dados como o PostgreSQL (via psycopg2) usar-se-ia '%s',
    # mas no SQLite a convenção é a interrogação.
    query = "SELECT nome, nota FROM alunos WHERE nome = ?"

    try:
        # Passamos a variável 'aluno' como uma tupla (aluno,) no segundo argumento do método execute.
        # A separação entre instrução e dados é feita internamente pelo driver do SQLite.
        cursor.execute(query, (aluno,))

        resultados = cursor.fetchall()
        return {"resultados": resultados}
    except Exception:
        # Substituído o retorno do erro nativo por uma mensagem genérica para evitar Information Disclosure.
        return {"erro": "Ocorreu um erro interno ao processar a busca."}
    finally:
        conn.close()
