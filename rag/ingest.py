import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from shared.config import config
from shared.logger import get_logger

logger = get_logger("ingest")

def create_mock_data():
    os.makedirs(config.DOCS_DIR, exist_ok=True)
    file_path = os.path.join(config.DOCS_DIR, "finance_ai_guide.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Artificial Intelligence in Finance.\\n")
            f.write("AI algorithms are increasingly used in algorithmic trading, where decisions are made in milliseconds.\\n")
            f.write("Machine learning models analyze historical market data to predict future stock prices.\\n")
            f.write("Risk management is another area transformed by AI, identifying potential loan defaults with high accuracy.\\n")
            f.write("Data science teams use deep learning to detect fraudulent transactions globally.\\n")

def ingest_docs():
    logger.info("Starting document ingestion...")
    create_mock_data()
    
    loader = DirectoryLoader(config.DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    
    if not documents:
        logger.warning("No documents found to ingest.")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL)
    
    logger.info(f"Ingesting {len(chunks)} chunks into ChromaDB at {config.CHROMA_DB_DIR}")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=config.CHROMA_DB_DIR
    )
    vectorstore.persist()
    logger.info("Ingestion complete.")

if __name__ == "__main__":
    ingest_docs()
