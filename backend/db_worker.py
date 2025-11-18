# db_worker.py
import asyncio
from logger import log_info, log_error
from db import AsyncSessionLocal
from models import Student
from sqlalchemy import select

student_sync_queue = asyncio.Queue()


def queue_student_sync(google_payload: dict):
    student_sync_queue.put_nowait(google_payload)
    log_info(f"Sincronização agendada para {google_payload.get('email')}")


async def student_sync_worker():
    log_info("DB Worker iniciado.")

    while True:
        google_payload = await student_sync_queue.get()
        email = google_payload.get("email")
        google_id = google_payload.get("sub")
        name = google_payload.get("name", "Usuário")

        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Student).where(Student.id == google_id)
                )
                student = result.scalar_one_or_none()

                if student:
                    log_info(f"Usuário já existia no banco: {email}")
                else:
                    new_student = Student(
                        id=google_id,
                        email=email,
                        name=name,
                    )
                    session.add(new_student)
                    await session.commit()
                    log_info(f"Novo usuário criado no banco: {email}")

        except Exception as e:
            log_error(f"Erro ao sincronizar usuário {email}: {e}")

        student_sync_queue.task_done()
