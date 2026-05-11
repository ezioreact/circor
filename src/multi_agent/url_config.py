from openai import OpenAI
import httpx
from src.configuration.env_key import EnvironKey

config = EnvironKey.setting()
gpu_server_url = config["local_model_base_url"]["base_url"]

url = f"http://{gpu_server_url}/v1"

try:
    client = OpenAI(
        base_url=url,
        api_key="new_secret_key",
        http_client=httpx.Client(timeout=5.0)  # 5 sec timeout
    )

    client.models.list()

    print("✅ Server is running")

except httpx.ConnectError:
    print("❌ Unable to connect to server")

except httpx.ReadTimeout:
    print("❌ Server timeout")

except Exception as e:
    print(f"❌ Error: {e}")