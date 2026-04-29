gpu_server_url = "175.155.64.237:19590" #"222.235.180.221:40406"


from openai import OpenAI
url = f"http://{gpu_server_url}/v1"

client = OpenAI(
    base_url=url,
    api_key="new_secret_key"
)
