from langchain_ollama import OllamaEmbeddings, OllamaLLM

# Константы llm & embeddings
OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "bge-m3"
LLM_MODEL = "qwen2.5:3b"  # qwen2.5:14b

EMBEDDINGS = OllamaEmbeddings(
    model=EMBEDDING_MODEL,
    base_url=OLLAMA_BASE_URL
)

LLM = OllamaLLM(
    model=LLM_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0.1,
    num_ctx=4096
)

# Путь к папке с документами для базы знаний раг
DIR_PATH = "docs/hr_legal"

# Константы векторной базы данных
PERSIST_DIR = "./chroma_db"
COLLECTION = "hr_legal_knowledge_base"

# Константы сплиттера чанков
CHUNK_SIZE = 1024
CHUNK_OVERLAP = 128
SEPARATORS = ["\n\n", "\n", ". ", " "]

# Количество релевантных документов в ретривере
RETRIEVER_SEARCH_K = 3


