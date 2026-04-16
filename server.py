from config import *
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
from typing import Optional
import uvicorn

from docs_reader import worker
from utils.current_time import get_current_time
import database_manager.database_manager as database_manager
import rag_engine.rag as rag_engine


# Pydantic модели
class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str
    source: Optional[str] = None
    file_path: Optional[str] = None


# Инициализация FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Глобальное состояние
rag_engine_instance = None


def check_ollama() -> bool:
    """Проверяет доступность Ollama"""
    try:
        response = requests.get("http://localhost:11434", timeout=5)
        if response.status_code == 200:
            print(f"OK | Ollama работает (LLM: {LLM_MODEL}, Embedding: {EMBEDDING_MODEL})")
            return True
        return False
    except requests.RequestException:
        print("X | Ollama недоступна")
        return False


def init_database():
    """Инициализирует базу данных"""
    if not database_manager.check_database_exists():
        database_manager.create_database()


def create_db_connections():
    """Создаёт подключения к БД для RAG и документ-ридера."""
    rag_conn = database_manager.connect_database()
    if rag_conn:
        print(f'[{get_current_time()}] Подключение к БД для RAG создано')

    reader_conn = database_manager.connect_database()
    if reader_conn:
        print(f'[{get_current_time()}] Подключение к БД для ридера документов создано')
        worker.start(reader_conn, 900)

    return rag_conn, reader_conn


def extract_source_metadata(result: dict) -> tuple[str | None, str | None]:
    """Извлекает метаданные источника из результата RAG."""
    context = result.get('context', [])
    if not context:
        return None, None

    first_doc = context[0]
    file_name = first_doc.metadata.get('file_name', 'unknown')
    file_path = f"/{DIR_PATH}/{file_name}"

    return file_name, file_path


@app.on_event("startup")
async def startup():
    global rag_engine_instance

    if not check_ollama():
        return

    # Удаление БД
    database_manager.drop_database()

    init_database()

    rag_conn, reader_conn = create_db_connections()
    rag_engine_instance = rag_engine.start_rag(rag_conn)


@app.post("/api/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):

    result = rag_engine_instance.invoke({"input": request.question})

    source, file_path = extract_source_metadata(result)

    return AnswerResponse(
        answer=result['answer'],
        source=source,
        file_path=file_path
    )


@app.get("/", response_class=HTMLResponse)
async def get_chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)