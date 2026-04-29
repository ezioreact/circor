# src/s3/downloader.py
from pathlib import Path
import os
import boto3
from urllib.parse import urlparse, unquote
from typing import Optional,Dict
from dotenv import load_dotenv
from backend_logs import get_logger
import asyncio

load_dotenv()
logger = get_logger()


def get_s3_client():
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("USER_KEY"),
        aws_secret_access_key=os.getenv("SECRET")
    )

async def s3_downloader(pdf_s3_url: Optional[str] = None,
                        xlsx_s3_url: Optional[str] = None) -> Dict:

    s3 = get_s3_client()

    base_dir = Path(__file__).resolve().parent
    local_dir = base_dir / "client_documents"
    local_dir.mkdir(parents=True, exist_ok=True)

    def download_from_url_sync(s3_url: str):
        parsed = urlparse(s3_url)
        bucket_name = parsed.netloc.split('.')[0]
        s3_key = unquote(parsed.path.lstrip("/")).replace("+", " ")

        filename = os.path.basename(s3_key)
        local_path = local_dir / filename

        try:
            s3.download_file(bucket_name, s3_key, str(local_path))
            return local_path.as_posix()
        except Exception as e:
            logger.error(f"S3 download error: {str(e)}")
            return None

    async def download_from_url(s3_url: Optional[str]):
        if not s3_url:
            return None

        # run blocking code in thread (IMPORTANT)
        return await asyncio.to_thread(download_from_url_sync, s3_url)

    # Run in parallel
    pdf_task = download_from_url(pdf_s3_url)
    xlsx_task = download_from_url(xlsx_s3_url)

    pdf_path, xlsx_path = await asyncio.gather(pdf_task, xlsx_task)


    print("Pdf path: ",pdf_path)
    print("Xlsx: ",xlsx_path)

    return {
        "pdf": pdf_path,
        "xlsx": xlsx_path
    }

import re
async def s3_file_name(name: str):
    name = name.rsplit(".", 1)[0]
    name = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    name = re.sub(r"^[^a-zA-Z0-9]+", "", name)
    name = re.sub(r"[^a-zA-Z0-9]+$", "", name)
    return name


# region_name=os.getenv("AWS_REGION"),
# aws_access_key_id=os.getenv("USER_KEY"),
# aws_secret_access_key=os.getenv("SECRET")

# print("region_name: ",region_name)
# print(aws_access_key_id)
# print(aws_secret_access_key)
# import asyncio
# print(asyncio.run(s3_downloader(pdf_s3_url="https://boomai-bucket.s3.ap-south-1.amazonaws.com/1774089074149-RFQ1.pdf",xlsx_s3_url="https://boomai-bucket.s3.ap-south-1.amazonaws.com/aravindh/circor_2_att6.xlsx")))

