"""
Embeddings module: Load and manage SBERT model for semantic scoring.
"""
# pyright: reportMissingImports=false, reportMissingModuleSource=false

import asyncio
from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingsManager:
    """Manage sentence embeddings using SBERT"""
    
    _model = None
    _lock = asyncio.Lock()
    
    @classmethod
    async def get_model(cls):
        """Get or load SBERT model (lazy loading)"""
        if cls._model is None:
            # Use asyncio lock to prevent multiple parallel loads
            async with cls._lock:
                if cls._model is None:
                    # Load in thread pool to avoid blocking
                    loop = asyncio.get_event_loop()
                    cls._model = await loop.run_in_executor(
                        None,
                        lambda: SentenceTransformer("all-MiniLM-L6-v2")
                    )
        return cls._model
    
    @classmethod
    async def encode_single(cls, text: str) -> np.ndarray:
        """Encode a single text to embedding"""
        model = await cls.get_model()
        # Truncate to avoid too long sequences
        text_truncated = text[:1024]
        embedding = model.encode(text_truncated, convert_to_numpy=True)
        return embedding
    
    @classmethod
    async def encode_batch(cls, texts: list) -> np.ndarray:
        """Encode multiple texts to embeddings"""
        model = await cls.get_model()
        # Truncate all texts
        texts_truncated = [t[:1024] for t in texts]
        embeddings = model.encode(texts_truncated, batch_size=32, convert_to_numpy=True)
        return embeddings
    
    @classmethod
    def encode_sync(cls, text: str) -> np.ndarray:
        """Synchronous encoding (for use in sync contexts like Celery)"""
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        
        text_truncated = text[:1024]
        embedding = cls._model.encode(text_truncated, convert_to_numpy=True)
        return embedding
    
    @classmethod
    def encode_batch_sync(cls, texts: list) -> np.ndarray:
        """Synchronous batch encoding"""
        if cls._model is None:
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        
        texts_truncated = [t[:1024] for t in texts]
        embeddings = cls._model.encode(texts_truncated, batch_size=32, convert_to_numpy=True)
        return embeddings
