from collections import deque

_HISTORY = deque(maxlen=200)

def push(user_name: str, message: str):
    _HISTORY.append({
        "user_name": user_name or "Anônimo",
        "message": message or ""
    })

def snapshot(limit: int = 100):
    data = list(_HISTORY)[-limit:]
    return data
