import asyncio
import json
import base64
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# --- IMPORTS DO PROJETO ---
from auth import verify_google_credential, create_aia_token, decode_aia_token
from logger import log_info, log_error
from db_worker import queue_student_sync, student_sync_worker
from config import OPENAI_API_KEY, REALTIME_MODEL

# Tenta importar tools de 'aia.tools' ou da raiz 'tools'
try:
    from aia.tools import TOOLS_SCHEMA, execute_tool
except ImportError:
    from tools import TOOLS_SCHEMA, execute_tool

app = FastAPI(title="AIA Voice Engine (Realtime + Barge-In)")

# URL da API Realtime
REALTIME_URL = f"wss://api.openai.com/v1/realtime?model={REALTIME_MODEL}"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    log_info("🔧 Iniciando DB Worker...")
    asyncio.create_task(student_sync_worker())

@app.post("/auth/google")
async def google_auth(data: dict):
    try:
        cred = data.get("credential")
        payload = verify_google_credential(cred)
        token = create_aia_token(payload)
        queue_student_sync(payload)
        return JSONResponse({"status": "OK", "token": token, "name": payload.get("name"), "email": payload.get("email")})
    except Exception as e:
        log_error(f"Erro Auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    token = websocket.query_params.get("token")
    if not token:
        log_error("Conexão rejeitada: Token ausente")
        await websocket.close(code=4001)
        return

    try:
        user = decode_aia_token(token)
        student_id = user["sub"]
        student_name = user.get("name", "Aluno")
    except:
        log_error("Conexão rejeitada: Token inválido")
        await websocket.close(code=4002)
        return

    log_info(f"🔊 Conectado: {student_name}")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1",
    }

    try:
        async with websockets.connect(REALTIME_URL, extra_headers=headers) as openai_ws:
            log_info("✅ Conectado à OpenAI Realtime API")

            # ==========================================
            # 1. CONFIGURAÇÃO DA SESSÃO (VAD AJUSTADO)
            # ==========================================
            session_config = {
                "type": "session.update",
                "session": {
                    "modalities": ["audio", "text"],
                    "instructions": (
                        f"Você é o Tutor AIA. O aluno é {student_name}. "
                        "Fale português do Brasil. Seja breve, simpático e didático. "
                        "Responda de forma direta. "
                        "Use a tool 'get_current_lesson' se precisar saber o conteúdo."
                    ),
                    "voice": "alloy",
                    "input_audio_format": "pcm16",
                    "output_audio_format": "pcm16",
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.6,            # Mais alto = ignora respiração/ruído
                        "prefix_padding_ms": 300,    # Salva um pouco antes da fala para não cortar
                        "silence_duration_ms": 500,  # Tempo de silêncio para considerar fim de frase
                        "create_response": True
                    },
                    "tools": TOOLS_SCHEMA,
                    "tool_choice": "auto",
                }
            }
            await openai_ws.send(json.dumps(session_config))

            # ==========================================
            # 2. LOOP CLIENTE -> OPENAI
            # ==========================================
            async def receive_from_client():
                try:
                    while True:
                        message = await websocket.receive()
                        
                        if "bytes" in message:
                            data = message["bytes"]
                            if len(data) > 0:
                                b64_audio = base64.b64encode(data).decode("utf-8")
                                event = {
                                    "type": "input_audio_buffer.append",
                                    "audio": b64_audio
                                }
                                await openai_ws.send(json.dumps(event))
                                
                except WebSocketDisconnect:
                    log_info("🔌 Cliente desconectou.")
                except Exception as e:
                    log_error(f"Erro Client->OpenAI: {e}")

            # ==========================================
            # 3. LOOP OPENAI -> CLIENTE
            # ==========================================
            async def receive_from_openai():
                try:
                    async for raw_msg in openai_ws:
                        event = json.loads(raw_msg)
                        evt_type = event.get("type")

                        # A. INTERRUPÇÃO (BARGE-IN)
                        if evt_type == "input_audio_buffer.speech_started":
                            log_info("🗣️ Fala detectada - Interrompendo áudio...")
                            
                            # 1. Manda o Frontend calar a boca imediatamente
                            await websocket.send_text(json.dumps({"type": "interrupt"}))
                            
                            # 2. Opcional: Limpa o buffer da OpenAI para ela parar de processar o áudio antigo
                            await openai_ws.send(json.dumps({"type": "input_audio_buffer.clear"}))

                        # B. Áudio chegando (Stream)
                        elif evt_type == "response.audio.delta":
                            audio_b64 = event.get("delta", "")
                            if audio_b64:
                                audio_bytes = base64.b64decode(audio_b64)
                                await websocket.send_bytes(audio_bytes)

                        # C. Execução de Ferramentas (Tools)
                        elif evt_type == "response.function_call_arguments.done":
                            call_id = event["call_id"]
                            f_name = event["name"]
                            args = json.loads(event["arguments"])
                            
                            log_info(f"🤖 Executando Tool: {f_name}")
                            result = await execute_tool(f_name, args, student_id)
                            
                            # Devolve o resultado para a IA
                            await openai_ws.send(json.dumps({
                                "type": "conversation.item.create",
                                "item": {
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": result
                                }
                            }))
                            # Força a geração de resposta
                            await openai_ws.send(json.dumps({"type": "response.create"}))

                        # D. Erros
                        elif evt_type == "error":
                            log_error(f"❌ OpenAI Erro: {event.get('error', {}).get('message')}")

                except Exception as e:
                    log_error(f"Erro OpenAI->Client: {e}")

            await asyncio.gather(receive_from_client(), receive_from_openai())

    except Exception as e:
        log_error(f"Falha na conexão OpenAI: {e}")
        await websocket.close(code=1011)