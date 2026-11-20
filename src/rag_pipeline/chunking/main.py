from collections.abc import Sequence

from langchain_text_splitters import RecursiveCharacterTextSplitter


class ChunkingManager:

    def __init__(
        self,
        documents: Sequence,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        *,
        over_lap: int | None = None,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")

        if over_lap is not None:
            chunk_overlap = over_lap

        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.documents = documents
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.over_lap = chunk_overlap

    def split_documents(self):
        """Split documents into smaller chunks for RAG retrieval."""
        if not self.documents:
            print("Split 0 documents into 0 chunks")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            keep_separator=False,
            strip_whitespace=True,
        )

        split_documents = text_splitter.split_documents(self.documents)
        print(
            f"Split {len(self.documents)} documents into "
            f"{len(split_documents)} chunks"
        )

        if split_documents:
            sample = split_documents[0]
            print("\nSample chunk")
            print(f"Content: {sample.page_content[:200]}...")
            print(f"Metadata: {sample.metadata}")

        return split_documents