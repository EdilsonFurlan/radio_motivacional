from django.shortcuts import render

from django.shortcuts import render
from django.conf import settings
from pathlib import Path
import uuid
import subprocess
import math
import openai
import firebase_admin
from firebase_admin import messaging, credentials
from decouple import config # Para carregar chaves seguras
from django.core.files import File as DjangoFile
from .models import Mensagem_Voz_Audio
from accounts.models import CadastroUsuario

from firebase_admin import messaging
from decouple import config

from django.conf import settings
from notifications.firebase import enviar_para_varios

#

FFMPEG = "ffmpeg"
FFPROBE = "ffprobe"

# Chave da OpenAI

openai.api_key = config("OPENAI_API_KEY")



# Função utilitária para rodar subprocessos
def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr)
    return p

# TTS usando OpenAI
def tts_openai(text: str, out_mp3: Path):
    resp = openai.audio.speech.create(model="gpt-4o-mini-tts", voice="alloy", input=text)
    out_mp3.write_bytes(resp.read())
    return out_mp3

# Adiciona pausas e converte para WAV
def add_pauses_and_convert(in_mp3: Path, out_wav: Path, silence_seconds=1):
    tmp_wav = in_mp3.with_suffix(".wav")
    run([FFMPEG, "-y", "-i", str(in_mp3), "-ar", "44100", "-ac", "2", str(tmp_wav)])
    silence = in_mp3.with_name("silence.wav")
    run([FFMPEG, "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
         "-t", str(silence_seconds), "-ar", "44100", "-ac", "2", str(silence)])
    with open("list.txt", "w", encoding="utf-8") as f:
        f.write(f"file '{silence}'\n")
        f.write(f"file '{tmp_wav}'\n")
        f.write(f"file '{silence}'\n")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", str(out_wav)])
    try:
        tmp_wav.unlink()
        Path("list.txt").unlink()
        silence.unlink()
    except: pass
    return out_wav

# Mix com música de fundo
def mix_with_music(voice_wav: Path, music_mp3: Path, out_mp3: Path, bg_volume=0.18, fade_seconds=3):
    proc = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(voice_wav)])
    duration = float(proc.stdout.strip() or 0.0)
    total = math.ceil(duration) + 1
    fade_out_start = max(0, total - fade_seconds)
    looped = music_mp3.with_name("musica_loop.mp3")
    run([FFMPEG, "-y", "-stream_loop", "-1", "-i", str(music_mp3),
         "-t", str(total),
         "-af", f"volume={bg_volume},afade=t=in:ss=0:d={fade_seconds},afade=t=out:st={fade_out_start}:d={fade_seconds}",
         "-ar", "44100", "-ac", "2", str(looped)])
    run([FFMPEG, "-y", "-i", str(voice_wav), "-i", str(looped),
         "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0,volume=1",
         "-c:a", "libmp3lame", "-q:a", "2", str(out_mp3)])
    try:
        looped.unlink()
    except: pass
    return out_mp3

# Função para enviar notificação FCM
def enviar_mensagem_fcm(request, titulo: str, corpo: str, url: str = None):
    usuarios = CadastroUsuario.objects.all()
    tokens = [u.token_fcm for u in usuarios if u.token_fcm]

    if not tokens:
        print("[FCM] Nenhum token encontrado.")
        return {"erro": "Nenhum token encontrado."}

    full_url = request.build_absolute_uri(settings.MEDIA_URL + url) if url else None
    data_payload = {"audio_url": full_url, "texto": corpo, "click_action": "OPEN_WISDOM_MESSAGE"} if full_url else {}

    # --- INÍCIO DA CORREÇÃO ---
    # 1. Cria uma LISTA de mensagens, uma para cada token
    messages = [
        messaging.Message(
            notification=messaging.Notification(title=titulo, body=corpo),
            data=data_payload,
            token=token
        ) for token in tokens
    ]
    
    # 2. Envia a lista de uma vez usando 'send_each'
    try:
        print(f"[FCM] Tentando enviar {len(messages)} mensagens com send_each...")
        # A nova função recomendada para a versão 7.x
        response = messaging.send_each(messages)
        
        print(f"[FCM] Envio com send_each. Sucesso: {response.success_count}, Falha: {response.failure_count}")
        return {"success_count": response.success_count, "failure_count": response.failure_count}
        
    except Exception as e:
        print(f"!!! [FCM] ERRO GERAL ao enviar com send_each: {e}")
        return {"erro": str(e)}
    # --- FIM DA CORREÇÃO ---
# View principal para gerar áudio, salvar e enviar notificação
def gerar_mensagem_view(request):
    if request.method == "POST":
        texto = request.POST.get("texto", "").strip()
        if not texto:
            return render(request, "mensagem_voz/mensagem.html", {"error": "Texto vazio"})
            
        print('Estou Aqui**************************************************')
        
        # --- SEU CÓDIGO DE GERAÇÃO DE ÁUDIO (INTACTO) ---
        media_dir = Path(settings.MEDIA_ROOT)
        audio_dir = media_dir / "audios"
        db_audio_dir = media_dir / "audios_db"
        music_dir = media_dir / "musicas"
        audio_dir.mkdir(parents=True, exist_ok=True)
        db_audio_dir.mkdir(parents=True, exist_ok=True)
        music_dir.mkdir(parents=True, exist_ok=True)

        audio_id = uuid.uuid4().hex
        voice_mp3 = audio_dir / f"{audio_id}_voice.mp3"
        voice_padded_wav = audio_dir / f"{audio_id}_voice_padded.wav"
        final_mp3 = audio_dir / f"{audio_id}.mp3"

        music_file = music_dir / "musica_suave.mp3"
        if not music_file.exists():
            return render(request, "mensagem_voz/mensagem.html", {"error": "Arquivo de música não encontrado."})

        tts_openai(texto, voice_mp3)
        add_pauses_and_convert(voice_mp3, voice_padded_wav, silence_seconds=1)
        mix_with_music(voice_padded_wav, music_file, final_mp3, bg_volume=0.18, fade_seconds=3)

        db_final_mp3 = db_audio_dir / f"{audio_id}.mp3"
        final_mp3.replace(db_final_mp3)
        # Atenção aqui: o nome do modelo deve ser o correto do seu models.py
        audio_obj = Mensagem_Voz_Audio(id=audio_id, title="Mensagem", text=texto, music_used="musica_suave.mp3") 
        with open(db_final_mp3, "rb") as f:
            django_file = DjangoFile(f)
            audio_obj.file.save(f"{audio_id}.mp3", django_file, save=True)

        try:
            proc = subprocess.run(
                ["ffprobe","-v","error","-show_entries","format=duration",
                 "-of","default=noprint_wrappers=1:nokey=1", str(db_final_mp3)],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            audio_obj.duration = float(proc.stdout.strip() or 0.0)
            audio_obj.save(update_fields=["duration"])
        except Exception:
            pass
        # --- FIM DO SEU CÓDIGO ORIGINAL ---

      # --- INÍCIO DO BLOCO CORRIGIDO ---
        audio_url = f"{settings.BASE_URL}{audio_obj.file.url}"

        try:
            tokens = list(CadastroUsuario.objects.exclude(token_fcm__isnull=True).exclude(token_fcm='').values_list('token_fcm', flat=True))
            if tokens:
                titulo = "Nova Mensagem de Sabedoria"
                corpo = texto
                data_payload = {
                    'click_action': 'OPEN_WISDOM_MESSAGE',
                    'texto': texto,
                    'audio_url': audio_url
                }
                # Assumindo que sua função de envio se chama 'enviar_para_varios'
                enviar_para_varios(tokens, titulo, corpo, data=data_payload)
        except Exception as e:
            print(f"ERRO AO ENVIAR FCM: {e}")
        # --- FIM DO BLOCO CORRIGIDO ---
        
        # apagar temporários
        try:
            voice_mp3.unlink()
            voice_padded_wav.unlink()
        except: pass

        # URL para o template (relativa)
        audio_url_template = settings.MEDIA_URL + "audios_db/" + db_final_mp3.name

        return render(request, "mensagem_voz/mensagem.html", {
            "success": True,
            "texto": texto,
            "audio_url": audio_url, # <-- Use a variável 'audio_url' que acabamos de criar
            "audio_obj": audio_obj
        })

    return render(request, "mensagem_voz/mensagem.html")

