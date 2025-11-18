# aia/agents/tutor.py

from dataclasses import dataclass
from typing import Optional

from openai import AsyncOpenAI

from aia.orchestrator.state import SessionState
from config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL_TEXT,
    OPENAI_MODEL_STT,
    OPENAI_MODEL_TTS,
    OPENAI_TTS_VOICE,
)


@dataclass
class StudentProfile:
    nome: Optional[str] = None
    nivel: str = "iniciante"
    objetivo: str = "aprender de forma estruturada e prática"


class TutorAgent:
    """
    AGENTE TUTOR PESSOAL (ATP) do AIA.

    Implementa:
    - transcribe_audio(audio_bytes)  -> texto do aluno
    - generate_reply(text, session)  -> resposta textual
    - synthesize_voice(text)         -> áudio (bytes)
    - build_instructions(session)    -> prompt pedagógico completo
    """

    def __init__(self):
        self.default_profile = StudentProfile()
        self.client = AsyncOpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )

    # -------------------------------------------------------
    # 1. STT - TRANSCRIÇÃO
    # -------------------------------------------------------
    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Recebe bytes em formato WEBM/OPUS (enviados pelo frontend via MediaRecorder)
        e usa o modelo de STT configurado (por padrão, whisper-1).
        """
        try:
            resp = await self.client.audio.transcriptions.create(
                model=OPENAI_MODEL_STT,
                file=("audio.webm", audio_bytes, "audio/webm"),
            )
            text = getattr(resp, "text", "") or ""
            print(f"[TutorAgent] Transcrição: {text}")
            return text.strip()
        except Exception as e:
            print("[TutorAgent] Erro na transcrição:", e)
            return ""

    # -------------------------------------------------------
    # 2. GERAÇÃO DA RESPOSTA (LLM)
    # -------------------------------------------------------
    async def generate_reply(self, user_text: str, session: SessionState) -> str:
        """
        Gera a resposta do tutor com base no texto do aluno e no estado da sessão.
        """
        try:
            system_prompt = self.build_instructions(session)

            resp = await self.client.chat.completions.create(
                model=OPENAI_MODEL_TEXT,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
            )

            content = resp.choices[0].message.content or ""
            answer = content.strip()
            print(f"[TutorAgent] Resposta gerada: {answer}")
            return answer

        except Exception as e:
            print("[TutorAgent] Erro ao gerar resposta:", e)
            return "Desculpe, tive um problema técnico ao gerar a resposta. Podemos tentar novamente?"

    # -------------------------------------------------------
    # 3. TTS - SÍNTESE DE VOZ
    # -------------------------------------------------------
    async def synthesize_voice(self, text: str) -> bytes:
        """
        Converte a resposta textual em áudio usando o modelo de TTS configurado.
        """
        try:
            speech = await self.client.audio.speech.create(
                model=OPENAI_MODEL_TTS,
                voice=OPENAI_TTS_VOICE,
                input=text,
            )
            # BinaryResponse -> convertemos para bytes
            audio_bytes = bytes(speech)
            return audio_bytes
        except Exception as e:
            print("[TutorAgent] Erro ao sintetizar voz:", e)
            return b""

    # -------------------------------------------------------
    # 4. INSTRUÇÕES PEDAGÓGICAS COMPLETAS
    # -------------------------------------------------------
    def build_instructions(self, session: SessionState) -> str:
        """
        Recupera o prompt pedagógico completo, com o mesmo conteúdo que você usava antes.
        """
        nome = session.student_name or self.default_profile.nome or "aluno"
        nivel = self.default_profile.nivel
        objetivo = self.default_profile.objetivo

        contexto_extra = ""
        if session.conversation_summary:
            contexto_extra += f"\nResumo recente da conversa: {session.conversation_summary}"
        if session.current_lesson:
            contexto_extra += f"\nLição atual: {session.current_lesson}"

        base_instructions = f"""
Você é o AGENTE TUTOR PESSOAL (ATP) do Ambiente Inteligente de Aprendizagem (AIA).

Seu papel é atuar como um professor particular multimodal,
falando com o aluno em voz, de forma clara, humana e estruturada.

PERFIL DO ALUNO:
- Nome (quando conhecido): {nome}
- Nível atual aproximado: {nivel}
- Objetivo principal declarado: {objetivo}
{contexto_extra}

REGRAS GERAIS DE COMPORTAMENTO:
1. Fale SEMPRE em português do Brasil, em tom amigável, respeitoso e motivador.
2. Adapte o vocabulário ao nível do aluno (iniciante, intermediário ou avançado),
   evitando jargões desnecessários quando perceber dificuldade.
3. Comece entendendo o contexto: faça perguntas curtas para entender
   o que o aluno já sabe e o que ele quer alcançar.
4. Explique conceitos de forma progressiva:
   - primeiro uma visão geral simples,
   - depois detalhes,
   - por fim, exemplos práticos.
5. Use frases relativamente curtas, adequadas para voz,
   com ritmo natural, evitando monólogos longos.
6. Ao final de cada explicação, faça UMA pergunta de checagem,
   para verificar se o aluno entendeu ou se deseja aprofundar.
7. Nunca critique, nunca humilhe, nunca desmotive.
   Corrija com cuidado e reforce que errar faz parte do aprendizado.
8. Se o aluno parecer confuso, reduza a complexidade e use analogias.
9. Se o aluno demonstrar domínio, aprofunde gradualmente o nível técnico,
   inclusive utilizando matemática, fórmulas ou código quando adequado.
10. Sempre mantenha o foco pedagógico: se o aluno desviar muito do tema,
    traga gentilmente de volta ao objetivo principal.

PARTICULARIDADES PARA INTERAÇÃO POR VOZ:
- Suas respostas devem ser claras e objetivas, evitando parágrafos muito longos.
- Quando estiver explicando algo mais complexo, quebre em passos concretos.
- Leve em conta que o aluno pode interromper sua fala no meio (barge-in),
  portanto mantenha cada bloco de explicação razoavelmente curto.

OBJETIVO GLOBAL:
Ajudar {nome} a {objetivo}, com clareza, paciência, profundidade progressiva
e foco no desenvolvimento real de competências, não apenas memorização.
"""
        return "\n".join(line.rstrip() for line in base_instructions.splitlines())
