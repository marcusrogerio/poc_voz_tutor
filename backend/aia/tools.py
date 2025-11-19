# Arquivo: aia/tools.py
import json
from sqlalchemy import select
from db import AsyncSessionLocal
from models import Student, Lesson
from logger import log_info

# Definição para a OpenAI (Schema)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "name": "get_current_lesson",
        "description": "Busca a lição atual do aluno no banco de dados.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

# Lógica de Execução
async def execute_tool(name: str, args: dict, student_id: str):
    """Executa a ferramenta solicitada pela IA"""
    if name == "get_current_lesson":
        return await _get_current_lesson(student_id)
    return {"error": "Ferramenta desconhecida"}

async def _get_current_lesson(student_id: str):
    async with AsyncSessionLocal() as session:
        # Busca aluno
        result = await session.execute(select(Student).where(Student.id == student_id))
        student = result.scalar_one_or_none()
        
        if not student:
            return json.dumps({"info": "Aluno não encontrado."})

        # Se não tiver lição definida, retornamos uma genérica
        if not student.current_lesson:
            return json.dumps({
                "topic": "Introdução",
                "content": "O aluno ainda não escolheu um tópico. Pergunte o que ele quer aprender."
            })

        # Busca a lição
        # OBS: Ajuste aqui se 'current_lesson' for ID (UUID) ou Título no seu banco
        # Supondo que seja o ID:
        try:
            l_result = await session.execute(select(Lesson).where(Lesson.id == student.current_lesson))
            lesson = l_result.scalar_one_or_none()
            
            if lesson:
                return json.dumps({
                    "title": lesson.title,
                    "content": lesson.content[:1500] + "..." # Trunca para não gastar muitos tokens
                })
        except:
            pass
            
        return json.dumps({"info": "Lição definida mas não encontrada."})