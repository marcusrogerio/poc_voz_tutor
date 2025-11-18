# aia/agents/memory_agent.py
from typing import Optional
from aia.orchestrator.state import SessionState


class MemoryAgent:
    """
    Futuro agente de memória do AIA.
    Por enquanto, apenas esqueleto para integração futura.
    """

    def __init__(self):
        ...

    async def load_profile(self, session: SessionState):
        """
        Carregar perfil estendido do aluno (futuro).
        """
        return

    async def save_session_summary(self, session: SessionState, summary: str):
        """
        Salvar resumo da sessão (futuro).
        """
        session.conversation_summary = summary
