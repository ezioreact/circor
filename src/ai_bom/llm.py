from openai import OpenAI
import json
from src.ai_bom.prompts import instruction
from backend_logs import get_logger
from src.configuration.env_key import EnvironKey

config = EnvironKey.setting()
logger = get_logger("llm.py")


client = OpenAI(
    base_url=f"http://{config['local_model_base_url']['base_url']}/v1",
    api_key="mys ecrete"  # Local models usually don't require a real key
)


async def clean_json_string(raw_str):
    if "{" in raw_str:
        raw_str = raw_str[raw_str.find("{"):raw_str.rfind("}")+1]
    cleaned = raw_str.replace('\n', '\\n').replace('\r', '\\r')
    return cleaned

def estimate_tokens(text: str):
    return len(text) // 4  # rough estimate

MAX_CHARS = 2000  # safe for ~2k tokens model

def truncate_chunk(chunk):
    chunk_str = json.dumps(chunk)
    # print("Before truncate:",len(chunk_str))
    return chunk_str[:MAX_CHARS]

async def large_languge_model_infer(key: str, chunk: str):

    def is_token_error(error_msg: str):
        return "maximum input length" in error_msg or "input tokens" in error_msg

    def normalize_chunk(chunk):
        if chunk is None:
            return []
        elif isinstance(chunk, str):
            return [chunk]
        elif not isinstance(chunk, list):
            return list(chunk)
        return chunk

    def reduce_chunk(chunk, level):
        if level == 1:
            return chunk[:3]
        elif level == 2:
            return [str(c)[:500] for c in chunk[:3]]
        elif level == 3:
            return [str(c)[:300] for c in chunk[:2]]
        else:
            return [str(c)[:200] for c in chunk[:1]]
    # normalize once
    original_chunk = normalize_chunk(chunk)

    for attempt in range(4):
        try:
            current_chunk = original_chunk if attempt == 0 else reduce_chunk(original_chunk, attempt)

            #safe serialization
            if isinstance(current_chunk, str):
                chunk_str = current_chunk
            else:
                chunk_str = json.dumps(current_chunk)

            logger.info(f"[Attempt {attempt}] Chunk size: {len(chunk_str)} chars")

            response = client.chat.completions.create(
                model="Qwen/Qwen3-VL-8B-Instruct",
                messages=[
                    {"role": "system", "content": instruction.system_instruction},
                    {"role": "user", "content": instruction.user_context.format(Key=key, chunk=chunk_str)}
                ],
                temperature=0,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content
            # print("Chunk: ",chunk_str)
            # print("Raw content: ",raw_content)
            try:
                data = json.loads(raw_content)
            except:
                cleaned = await clean_json_string(raw_content)
                data =  json.loads(cleaned)

            if str(data.get("answer", "")).strip().lower() in ["notfound", "not found", "n/a", "", "none", "null"," "]:
                data["answer"] = "This information was not identified in the provided document section and may be available in the relevant datasheet or annexure."
                data["status"] = "Partial"
                data["page_number"] = ""
            return data


        except Exception as e:
            error_msg = str(e)

            if is_token_error(error_msg):
                logger.warning(f"[Attempt {attempt}] Token overflow chunk size {len(chunk_str)} => reducing context...")
                continue
            else:
                logger.error(f"Extraction failed: {error_msg} chunk Size:{len(chunk_str)}")
                break

    return {
        "key": key,
        "answer": None,
        "error": "LLM_FAILED_AFTER_RETRIES"
    }