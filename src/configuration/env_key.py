from pathlib import Path
import yaml
from functools import lru_cache
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_PATH = PROJECT_ROOT / "configuration" / "model_config.yaml"

class EnvironKey:
    @staticmethod
    @lru_cache()
    def setting():   # lowercase name is best practice
        if not CONFIG_PATH.is_file():
            raise FileNotFoundError(f"Config file not found at: {CONFIG_PATH}")
        

        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)


# # CALL the function
# config = EnvironKey.setting()
# print(config["embedding"]["batch_size"])
