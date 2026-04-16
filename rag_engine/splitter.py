from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS

_text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=SEPARATORS
)


def split_text_to_docs(text_data: dict) -> list[Document]:
    """Разбивает file_content на чанки Document с метаданными file_name.

    Returns:
        Document или пустой список, если контент пустой или отсутствует.
    """
    content = text_data.get("file_content", "").strip()
    if not content:
        return []

    return _text_splitter.create_documents(
        texts=[content],
        metadatas=[{"file_name": text_data.get("file_name", "unknown")}]
    )
