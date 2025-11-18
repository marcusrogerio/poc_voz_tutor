# aia/agents/curriculum_agent.py
from typing import Optional
from aia.orchestrator.state import SessionState


class CurriculumAgent:
    """
    Futuro agente de currículo.
    Responsável por decidir lições atuais/seguintes.
    """

    def __init__(self):
        ...

    async def get_current_lesson(self, session: SessionState) -> Optional[str]:
        """
        Retorna a lição atual do aluno (por enquanto, só usa o que estiver na sessão).
        No futuro, consultará o banco.
        """
        return session.current_lesson

    async def advance_lesson(self, session: SessionState):
        """
        Avançar a lição (futuro).
        """
        return
