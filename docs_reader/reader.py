from pathlib import Path
from typing import List, Union, Dict, Optional
import docx
import PyPDF2
from langchain_chroma import Chroma


class FolderReader:
    """
    Класс для чтения документов различных форматов (txt, docx, pdf) из указанной директории.
    """

    def __init__(
            self,
            dir_path: Union[str, Path],
            allowed_extensions: Optional[set] = None,
            txt_encodings: Optional[List[str]] = None
    ):
        """
        Инициализация ридера документов.

        :param dir_path: Путь к директории с файлами
        :param allowed_extensions: Разрешенные расширения файлов (по умолчанию: txt, docx, pdf)
        :param txt_encodings: Список кодировок для попытки чтения txt файлов
        """
        self.dir_path = Path(dir_path)
        self.allowed_extensions = allowed_extensions or {'txt', 'docx', 'pdf'}
        self.txt_encodings = txt_encodings or ['utf-8', 'cp1251', 'latin-1']

    def _read_txt(self, file_path: Path) -> str:
        """Приватный метод чтения .txt файла с подбором кодировки."""
        for encoding in self.txt_encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise Exception(
            f"Не удалось прочитать файл {file_path.name} "
            f"с доступными кодировками: {self.txt_encodings}"
        )

    def _read_docx(self, file_path: Path | str) -> str:
        """Приватный метод чтения .docx файла."""
        doc = docx.Document(file_path)
        return '\n'.join(paragraph.text for paragraph in doc.paragraphs)

    def _read_pdf(self, file_path: Path) -> str:
        """Приватный метод чтения .pdf файла."""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text

    def get_file_list(self) -> List[str]:
        """
        Получает список имен файлов с разрешенными расширениями в указанной папке.

        :returns: Список строк с именами файлов (включая расширения)
        """
        if not self.dir_path.exists():
            return []

        files = []
        for p in self.dir_path.iterdir():
            if p.is_file():
                ext = p.suffix[1:].lower()
                if ext in self.allowed_extensions:
                    files.append(p.name)
        return files

    def read_file(self, file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Читает содержимое одного файла в зависимости от его расширения.

        :param file_path: Имя файла или путь к файлу (str или Path)
        :returns: Словарь {'file_name': имя_файла, 'file_content': содержимое_файла}
        """
        # Объединяем BASE_DIR с именем файла
        full_path = self.dir_path / file_path
        file_name = full_path.name
        file_extension = full_path.suffix[1:].lower()

        readers = {
            'txt': self._read_txt,
            'docx': self._read_docx,
            'pdf': self._read_pdf
        }

        file_content = readers[file_extension](full_path)

        return {
            'file_name': file_name,
            'file_content': file_content
        }
