## Basic Instruction
    1. Before runing the code please make sure Vast.ai[GPU] is running and your 
        local vllm is up in our system [cmd]
    2. Please replace the vast.ai[GPU] ip:port into the url_config.py

## Vast.ai [GPU]
    """ please run this script into """
    1. ssh -p 36465 root@116.100.160.186

    2. vllm serve Qwen/Qwen3-VL-8B-Instruct \
    --host 0.0.0.0 \
    --port 8265 \
    --max-model-len 20906 \
    --gpu-memory-utilization 0.90


# Initial opening 
    - rag_llm_connector.py [file]
        - asynd def start_proccess [function]


# multi_agent [folder] from src.
    - dev_final_Extraction.py [file]
    