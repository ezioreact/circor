import os
from pathlib import Path
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from src.configuration.env_key import EnvironKey
from backend_logs import get_logger

config_= EnvironKey.setting()
logger = get_logger("initilaize Embedding Model")

"""singletine pattern to avoide multiple time class initialization and object creation"""
class EmbeddingService:
    """
    Singleton Embedding Service (no external changes required)

    __new__ => Object creator
    cls => cls itself
    """

    _instance = None
    _model = None

    @staticmethod
    @lru_cache(maxsize=1)
    def load_embed_model(model_name):
        return SentenceTransformer(model_name)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self, model_name: str = None):
        # جلوگیری re-init multiple times
        if hasattr(self, "_initialized") and self._initialized:
            return

        if model_name is None:
            model_name = config_["embedding"]["embedding_model"]

        # Load model ONLY once
        if EmbeddingService._model is None:
            EmbeddingService._model = self.load_embed_model(model_name)
            logger.info(
                f"initially Embedding Model `|{model_name}|` loaded ONLY ONCE! | batch={config_['embedding']['batch_size']}"
            )

        self.model = EmbeddingService._model
        self._initialized = True

    async def encoding(self, texts: list[str]):
        return self.model.encode(
            texts,
            batch_size=config_['embedding']['batch_size'],
            show_progress_bar=config_['embedding']['progress_bar'],
            normalize_embeddings=True
        )
