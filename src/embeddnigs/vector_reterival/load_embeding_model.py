from pathlib import Path
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from src.configuration.env_key import EnvironKey


config_= EnvironKey.setting()


class EmbeddingService:
    """
    Docstring for EmbeddingService
    ## example:
        Obj = EmbeddingService()
        response = Obj.encoding(texts=['a','b'])
        print(response)"""

    @staticmethod
    @lru_cache(maxsize=1)
    def load_embed_model(model_name):
        return SentenceTransformer(model_name)

    def __init__(self, model_name:str = None):
        if model_name is None:
           model_name = config_["embedding"]["embedding_model"]
        
        self.model = self.load_embed_model(model_name)


    # @staticmethod
    async def encoding(self, texts : list[str]):
        return self.model.encode(texts, 
                                 batch_size=config_['embedding']['batch_size'],
                                 show_progress_bar=config_['embedding']['progress_bar'])

