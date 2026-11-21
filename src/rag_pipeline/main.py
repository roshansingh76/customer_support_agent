
import argparse
import logging
from dataclasses import dataclass
from pathlib import Path


from rag_pipeline.chunking.main import ChunkingManager
from rag_pipeline.embeddings.main import EmbeddingManager
from rag_pipeline.ingestion.main import PdfLoaderManager
from rag_pipeline.vectordb.main import VectorStore


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF_DIRECTORY = PROJECT_ROOT / "datadocs"
DEFAULT_VECTOR_DIRECTORY = PROJECT_ROOT / "vector_store"


@dataclass(frozen=True)
class RAGConfig:
    pdf_directory: Path = DEFAULT_PDF_DIRECTORY
    vector_directory: Path = DEFAULT_VECTOR_DIRECTORY
    collection_name: str = "pdf_document"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    model_name: str = "all-MiniLM-L6-v2"


def build_rag_index(
    pdf_directory: str | Path = DEFAULT_PDF_DIRECTORY,
    vector_directory: str | Path = DEFAULT_VECTOR_DIRECTORY,
    collection_name: str = "pdf_document",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    model_name: str = "all-MiniLM-L6-v2",
) -> VectorStore:
    """Build or update the RAG vector index from PDF documents."""
    logging.info("Starting RAG index build")
    config = RAGConfig(
        pdf_directory=Path(pdf_directory),
        vector_directory=Path(vector_directory),
        collection_name=collection_name,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        model_name=model_name,
    )

    if config.chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")
    if not 0 <= config.chunk_overlap < config.chunk_size:
        raise ValueError("chunk_overlap must be non-negative and below chunk_size")

    documents = PdfLoaderManager(str(config.pdf_directory)).process_all_pdf()
    if not documents:
        return VectorStore(
            collection=config.collection_name,
            persist_directory=str(config.vector_directory),
        )

    chunks = ChunkingManager(
        documents,
        chunk_size=config.chunk_size,
        chunk_overlap=config.chunk_overlap,
    ).split_documents()
    if not chunks:
        raise RuntimeError("PDF documents were loaded but no text chunks were created")

    embeddings = EmbeddingManager(model_name=config.model_name).generate_embedding(
        [chunk.page_content for chunk in chunks],
        normalize_embeddings=True,
    )

    vector_store = VectorStore(
        collection=config.collection_name,
        persist_directory=str(config.vector_directory),
    )
    vector_store.add_documents(chunks, embeddings)
    logging.info(
        "RAG index ready with %d documents", vector_store.collection.count()
    )
    return vector_store


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the customer support RAG index")
    parser.add_argument("--pdf-directory", type=Path, default=DEFAULT_PDF_DIRECTORY)
    parser.add_argument("--vector-directory", type=Path, default=DEFAULT_VECTOR_DIRECTORY)
    parser.add_argument("--collection", default="pdf_document")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=200)
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    store = build_rag_index(
        pdf_directory=args.pdf_directory,
        vector_directory=args.vector_directory,
        collection_name=args.collection,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        model_name=args.model,
    )
    print(
        f"RAG index ready: {store.collection_name} "
        f"({store.collection.count()} documents)"
    )


if __name__ == "__main__":
    main()
