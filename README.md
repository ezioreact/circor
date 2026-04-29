## to start VLLM
vllm serve Qwen/Qwen3-VL-8B-Instruct \
  --host 0.0.0.0 \
  --port 8265 \
  --max-model-len 30906 \
  --gpu-memory-utilization 0.90


# GPU URL
 - shold change multi_agent/url_config.py & configuration/model_config.yaml


## Quick LLM test
import requests
url = "http://65.0.131.63:8000/v1/chat/completions"
payload = {
    "model": "/home/ubuntu/circor_qwen_model/model",
    "messages": [
        {"role": "user", "content": "Hello"}
    ]
}
response = requests.post(url, json=payload)
print(response.json())




curl http://198.53.64.194:21973/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-VL-8B-Instruct",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "give me the details explanation for LLm model."}
    ],
    "max_tokens": 50,
    "temperature": 0
  }'


  
