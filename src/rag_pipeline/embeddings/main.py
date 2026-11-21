import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingManager:

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not model_name or not model_name.strip():
            raise ValueError("model_name cannot be empty")

        self.model_name = model_name
        self.model: SentenceTransformer | None = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the configured sentence transformer model."""
        print(f"Loading embedding model: {self.model_name}")
        try:
            self.model = SentenceTransformer(self.model_name)
        except Exception as exc:
            raise RuntimeError(
                f"Error loading embedding model '{self.model_name}': {exc}"
            ) from exc

        dimension = self.model.get_embedding_dimension()
        print(
            f"Model loaded successfully. "
            f"Embedding dimension: {dimension}"
        )

    def generate_embedding(
        self,
        texts: list[str],
        *,
        normalize_embeddings: bool = False,
    ) -> np.ndarray:
        """Generate NumPy embeddings for a list of texts."""
        if self.model is None:
            raise RuntimeError("Embedding model is not loaded")
        if not texts:
            raise ValueError("texts cannot be empty")
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("texts must contain only non-empty strings")

        print(f"Generating embeddings for {len(texts)} texts...")
        embedding = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=normalize_embeddings,
        )
        print(f"Generated embedding with shape {embedding.shape}")

        return embedding