# aia/orchestrator/state.py

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class SessionState:
    """
    Estado cognitivo da sessão atual do aluno no AIA.
    Armazena identidade, histórico, progresso e estados internos dos agentes.
    """

    student_id: str
    student_email: str
    student_name: str

    # Perfil do aluno (estilo cognitivo, preferências, diagnósticos, etc.)
    profile: Dict[str, Any] = field(default_factory=dict)

    # Lição, tópico ou módulo atual do currículo
    current_lesson: Optional[str] = None

    # Últimas mensagens trocadas (curto prazo)
    recent_messages: List[Dict[str, str]] = field(default_factory=list)

    # Resumo consolidado da conversa (para memória longa futura)
    conversation_summary: Optional[str] = None

    # Campo flexível para agentes armazenarem contexto
    extra: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        """
        Armazena uma mensagem no histórico curto da sessão.
        """
        self.recent_messages.append({"role": role, "content": content})

        # Mantém histórico curto controlado
        if len(self.recent_messages) > 20:
            self.recent_messages.pop(0)
