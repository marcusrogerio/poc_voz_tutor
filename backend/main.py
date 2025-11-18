import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.websockets import WebSocketState

from auth import verify_google_credential, create_aia_token, decode_aia_token
from logger import log_info, log_error
from db_worker import queue_student_sync, student_sync_worker

# Importações do AIA
from aia.orchestrator.state import SessionState
from aia.orchestrator.graph import process_user_message


app = FastAPI(title="AIA Backend")


# =============================
#   CORS
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================
#   STARTUP EVENT
# =============================
@app.on_event("startup")
async def startup_event():
    log_info("🔧 Iniciando DB Worker em background...")
    asyncio.create_task(student_sync_worker())
    log_info("DB Worker iniciado.")


# =============================
#   LOGIN GOOGLE
# =============================
@app.post("/auth/google")
async def google_auth(data: dict):
    try:
        google_credential = data.get("credential")
        if not google_credential:
            raise HTTPException(status_code=400, detail="Token Google ausente")

        # 1. Validar credencial Google
        google_payload = verify_google_credential(google_credential)

        # 2. Criar token AIA
        aia_token = create_aia_token(google_payload)

        # 3. Agendar sincronização
        queue_student_sync(google_payload)

        log_info(f"Login Google ok: {google_payload.get('email')}")

        return JSONResponse({
            "status": "OK",
            "token": aia_token,
            "name": google_payload.get("name"),
            "email": google_payload.get("email"),
        })

    except Exception as e:
        log_error(f"Erro no Google Auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================
#   WEBSOCKET (ÁUDIO + TEXTO)
# =============================
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()

        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=4001)
            return

        try:
            user = decode_aia_token(token)
        except Exception as e:
            log_error(f"Token inválido: {e}")
            await websocket.close(code=4002)
            return

        user_id = user["sub"]
        user_name = user.get("name", "Aluno")
        user_email = user.get("email")

        log_info(f"🔊 WebSocket conectado: {user_name}")

        # Criar estado da sessão
        state = SessionState(
            student_id=user_id,
            student_name=user_name,
            student_email=user_email
        )

        # LOOP PRINCIPAL DO WEBSOCKET
        while True:
            try:
                message = await websocket.receive()

                # Caso seja áudio
                if "bytes" in message:
                    audio_bytes = message["bytes"]

                    response = await process_user_message(
                        audio_bytes=audio_bytes,
                        text_input=None,
                        state=state,
                    )

                    await websocket.send_bytes(response.output_audio)
                    await websocket.send_text(json.dumps({
                        "transcript": response.transcript,
                        "agent": response.agent,
                    }))

                # Caso seja texto
                elif "text" in message:
                    text = message["text"]

                    response = await process_user_message(
                        audio_bytes=None,
                        text_input=text,
                        state=state,
                    )

                    await websocket.send_bytes(response.output_audio)
                    await websocket.send_text(json.dumps({
                        "transcript": response.transcript,
                        "agent": response.agent,
                    }))

            except WebSocketDisconnect:
                log_info("🔌 Cliente desconectou.")
                break

            except Exception as e:
                log_error(f"Erro WS: {e}")
                if websocket.application_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json.dumps({"error": str(e)}))
                break

    except Exception as e:
        log_error(f"Erro fatal WS: {e}")
        try:
            await websocket.close()
        except:
            pass


# =============================
#   ROOT
# =============================
@app.get("/")
async def root():
    return {"status": "AIA Backend rodando"}
