
# src/s3/uploader.py

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from backend_logs import get_logger
logger = get_logger("uploade_to_s3.py")
load_dotenv()
import asyncio

# Initialize client once to reuse connections
s3_client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("USER_KEY"),
    aws_secret_access_key=os.getenv("SECRET")
)

async def uploade_to_s3(collection, local_file_path: str, s3_key: str = None):
    try:
        bucket_name = os.getenv("BUCKET_NAME")
        if not s3_key:
            # Fixed double slash
            s3_key = f"ai-extracted-table-image/{collection}_{os.path.basename(local_file_path)}"

        # Run the synchronous boto3 call in a separate thread to keep the loop moving
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, 
            lambda: s3_client.upload_file(str(local_file_path), bucket_name, s3_key)
        )

        base_url = os.getenv("BASE_URL")
        return {
            "status": "uploaded",
            "url": f"https://{base_url}/{s3_key}"
        }

    except Exception as E:
        logger.error(f"S3 upload FAILED: {str(E)}")
        return {"status": "failed", "error": str(E)}