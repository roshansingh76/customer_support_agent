from pathlib import Path
from typing import Sequence
import hashlib

import chromadb
import numpy as np
from langchain_core.documents import Document


class VectorStore:

    def __init__(
        self,
        collection: str = "pdf_document",
        persist_directory: str = "../../../vector_store",
    ):
        self.collection_name = collection
        self.persist_directory = persist_directory
        self.client: chromadb.api.ClientAPI | None = None
        self.collection: chromadb.api.models.Collection.Collection | None = None
        self._initialize_store()

    def _initialize_store(self) -> None:
        """Initialize the ChromaDB persistent client and collection."""
        try:
            Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document embeddings for RAG"},
            )
            print(f"Vector store initialized. Collection: {self.collection_name}")
            print(f"Existing documents in collection: {self.collection.count()}")

        except Exception as exc:
            raise RuntimeError(
                f"Error initializing vector store '{self.collection_name}': {exc}"
            ) from exc

    def add_documents(
        self,
        documents: Sequence[Document],
        embeddings: np.ndarray,
    ) -> None:
        """Add documents and their embeddings to the vector store."""
        if self.collection is None:
            raise RuntimeError("Vector store collection is not initialized")
        if not documents:
            raise ValueError("documents cannot be empty")
        if not isinstance(embeddings, np.ndarray):
            raise TypeError("embeddings must be a NumPy array")
        if embeddings.ndim != 2:
            raise ValueError("embeddings must be a two-dimensional NumPy array")
        if len(documents) != len(embeddings):
            raise ValueError(
                "Number of documents must match number of embeddings"
            )
        if not np.isfinite(embeddings).all():
            raise ValueError("embeddings must contain only finite values")

        print(f"Adding {len(documents)} documents to vector store...")

        ids = []
        metadatas = []
        documents_text = []

        for index, (doc, embedding) in enumerate(zip(documents, embeddings)):
            if not isinstance(doc, Document):
                raise TypeError("documents must contain LangChain Document objects")

            metadata = dict(doc.metadata)
            metadata["doc_index"] = index
            metadata["content_length"] = len(doc.page_content)
            metadatas.append(metadata)
            documents_text.append(doc.page_content)

            identity = (
                f"{metadata.get('source', '')}|"
                f"{metadata.get('page', '')}|"
                f"{metadata.get('start_index', '')}|"
                f"{doc.page_content}"
            )
            ids.append(
                "doc_" + hashlib.sha256(identity.encode("utf-8")).hexdigest()
            )

        try:
            existing_ids = self.collection.get(include=[]).get("ids", [])
            legacy_ids = [
                record_id
                for record_id in existing_ids
                if not (
                    record_id.startswith("doc_")
                    and len(record_id) == 68
                    and all(
                        character in "0123456789abcdef"
                        for character in record_id[4:]
                    )
                )
            ]
            if legacy_ids:
                self.collection.delete(ids=legacy_ids)

            self.collection.upsert(
                ids=ids,
                embeddings=embeddings.tolist(),
                metadatas=metadatas,
                documents=documents_text,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Error adding documents to vector store: {exc}"
            ) from exc

        print(
            f"Successfully added {len(documents)} documents to vector store"
        )
        print(f"Total documents in collection: {self.collection.count()}")
