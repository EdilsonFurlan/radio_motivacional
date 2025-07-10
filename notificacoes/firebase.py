import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("notificacoes/firebase_credentials.json")
firebase_admin.initialize_app(cred)


def enviar_notificacao(token: str, titulo: str, corpo: str, tipo=None, url=None):
    data_payload = {
        "titulo": titulo,
        "mensagem": corpo,  # <-- ALTERADO de "corpo" para "mensagem"
    }
    if tipo:
        data_payload["tipo"] = tipo
    if url:
        data_payload["url"] = url

    mensagem = messaging.Message(
        data=data_payload,
        token=token,
        android=messaging.AndroidConfig(priority="high")
    )
    resposta = messaging.send(mensagem)
    return resposta

def enviar_para_varios(tokens: list[str], titulo: str, corpo: str, tipo=None, url=None):
    mensagens = []

    data_payload = {
        "mensagem": corpo,
    }
    if tipo is not None:
        data_payload["tipo"] = tipo
    if url is not None:
        data_payload["url"] = url  # ← ESSA LINHA NÃO PODE FALTAR

    for token in tokens:
        mensagens.append(
            messaging.Message(
                data=data_payload,
                token=token,
                android=messaging.AndroidConfig(priority="high")
            )
        )

    responses = []
    for msg in mensagens:
        try:
            resposta = messaging.send(msg)
            responses.append({"token": msg.token, "resposta": resposta})
        except Exception as e:
            responses.append({"token": msg.token, "erro": str(e)})

    return responses