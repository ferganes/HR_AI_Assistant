from langchain_chroma import Chroma
from config import DIR_PATH
from database_manager import database_manager
from docs_reader.reader import FolderReader
from rag_engine import splitter
from utils import current_time


def get_existing_uniq_docs(db: Chroma) -> set[str]:
    """
    Функция возвращает set уникальных имен файлов из метаданных имеющихся в базе документов

    Args: db: Chroma
    Return: set(str)
    """

    existing_docs = db.get()
    uniq_docs = set()

    if existing_docs and 'metadatas' in existing_docs:
        for metadata in existing_docs['metadatas']:
            if metadata and 'file_name' in metadata:
                uniq_docs.add(metadata['file_name'])

    return uniq_docs


def start(db_conn, interval=900):

    print(f"\n[{current_time.get_current_time()}] Запускаю обход папки в фоне...")

    folder_reader = FolderReader(DIR_PATH)

    # Получаем список файлов папке
    files_list = folder_reader.get_file_list()

    # Получаем файлы уже загруженных в базу
    existing_uniq_docs = get_existing_uniq_docs(db_conn)
    print(f"\n[{current_time.get_current_time()}] Уникальных документов в базе: {len(existing_uniq_docs)}...")

    # Находим новые файлы
    new_files = [
        file_name for file_name in files_list
        if file_name not in existing_uniq_docs
    ]

    print(f'\n--> Документов в базе {len(existing_uniq_docs)}, новых документов {len(new_files)}...')

    if new_files:

        chunks = []

        for file in new_files:
            file_data = folder_reader.read_file(file)

            if file_data:
                chunk = splitter.split_text_to_docs(file_data)
                chunks.extend(chunk)

        print(f'Всего чанков {len(chunks)}')

        print(f"\n[{current_time.get_current_time()}] Обновление базы, добавляю {len(chunks)} на основе {len(new_files)}...")
        database_manager.update_database(db_conn, chunks)