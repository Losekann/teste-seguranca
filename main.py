from fastapi import FastAPI

app = FastAPI(title="Aplicação de Teste DAST")


@app.get("/")
def raiz():
    return {"mensagem": "Aplicação no ar para teste de segurança DAST"}


@app.get("/saudacao/{nome}")
def saudacao(nome: str):
    return {"mensagem": f"Olá, {nome}!"}


@app.get("/health")
def health():
    return {"status": "ok"}
