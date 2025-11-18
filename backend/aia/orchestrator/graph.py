# aia/orchestrator/graph.py

from typing import Optional

from aia.orchestrator.state import SessionState
from aia.agents.tutor import TutorAgent
from aia.agents.memory_agent import MemoryAgent
from aia.agents.curriculum_agent import CurriculumAgent


class AIAResponse:
    """
    Estrutura padrão de resposta do orquestrador.
    Contém: transcrição, áudio e identificador do agente.
    """
    def __init__(self, transcript: str, output_audio: bytes, agent: str):
        self.transcript = transcript
        self.output_audio = output_audio
        self.agent = agent


class AIAOrchestrator:
    """
    Orquestrador cognitivo simples do AIA (versão 0.1).

    Nesta versão:
    - Se vier áudio: transcreve → gera resposta → sintetiza voz.
    - Se vier texto: usa diretamente → gera resposta → sintetiza voz.
    - Futuramente: integrar MemoryAgent, CurriculumAgent, LangGraph, etc.
    """

    def __init__(self):
        self.tutor = TutorAgent()
        self.memory = MemoryAgent()
        self.curriculum = CurriculumAgent()

    async def process(
        self,
        audio_bytes: Optional[bytes],
        text_input: Optional[str],
        session: SessionState,
    ) -> AIAResponse:
        # 1) Determinar texto de entrada
        transcript = ""
        user_text = text_input or ""

        if audio_bytes:
            transcript = await self.tutor.transcribe_audio(audio_bytes)
            user_text = transcript

        # 2) Geração da resposta textual
        reply_text = await self.tutor.generate_reply(user_text, session)

        # 3) Síntese de voz
        audio_out = await self.tutor.synthesize_voice(reply_text)

        # 4) (Opcional) atualizar memória / currículo futuramente
        # self.memory.update(session, user_text, reply_text)
        # self.curriculum.track_progress(session, user_text, reply_text)

        return AIAResponse(
            transcript=transcript or user_text,
            output_audio=audio_out,
            agent="tutor",
        )


# Instância global do orquestrador
_orchestrator = AIAOrchestrator()


async def process_user_message(audio_bytes=None, text_input=None, state=None):
    """
    Função unificada chamada pelo main.py
    """
    return await _orchestrator.process(
        audio_bytes=audio_bytes,
        text_input=text_input,
        session=state,
    )
