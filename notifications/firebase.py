import firebase_admin
from firebase_admin import credentials, messaging
from decouple import config

# --- INICIALIZAÇÃO SEGURA ---
try:
    if not firebase_admin._apps:
        cred_path = config("FIREBASE_CREDENTIALS_PATH")
        project_id = config("FIREBASE_PROJECT_ID")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {'projectId': project_id})
        print(">>> Firebase SDK inicializado <<<")
except Exception as e:
    print(f"!!! ERRO ao inicializar Firebase: {e}")



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


# --- FUNÇÃO DE ENVIO (MÉTODO varios) ---
def enviar_para_varios(tokens, titulo, corpo, data=None):
    if not tokens:
        return {"success_count": 0, "failure_count": 0}

    data_payload = data if data is not None else {}

    # Cria uma LISTA de mensagens individuais
    messages = [
        messaging.Message(
            notification=messaging.Notification(title=titulo, body=corpo),
            data=data_payload,
            token=token
        ) for token in tokens
    ]

    try:
        # 👇 USA A NOVA FUNÇÃO CORRETA 👇
        response = messaging.send_each(messages)
        
        print(f"[FCM] Envio com send_each. Sucesso: {response.success_count}, Falha: {response.failure_count}")
        return {
            "success_count": response.success_count,
            "failure_count": response.failure_count,
        }
    except Exception as e:
        print(f"!!! [FCM] ERRO GERAL ao enviar com send_each: {e}")
        raise e