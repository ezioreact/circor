
# src/s3/uploader.py

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from backend_logs import get_logger

logger = get_logger("uploade_to_s3.py")

load_dotenv()

def get_s3_client():
    return boto3.client(
        "s3",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("USER_KEY"),
        aws_secret_access_key=os.getenv("SECRET")
    )

async def s3_uploader(local_file_path: str, s3_key: str = None):
    try:
        bucket_name = os.getenv("BUCKET_NAME")

        # Default key
        if not s3_key:
            s3_key = f"ai-bom-response/{os.path.basename(local_file_path)}"

        s3_client = get_s3_client()

        #Upload
        s3_client.upload_file(
            Filename=local_file_path,
            Bucket=bucket_name,
            Key=s3_key
        )

        #VERIFY upload
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
        except ClientError as e:
            logger.error(f"S3 verification failed: {str(e)}")
            return {
                "status": "failed",
                "error": "Upload verification failed"
            }

        #Build URL
        base_url = os.getenv("BASE_URL")
        public_url = f"https://{base_url}/{s3_key}"

        logger.info(f"Successfully uploaded to S3: {public_url}")

        return {
            "status": "uploaded",
            "url": public_url
        }

    except Exception as E:
        logger.error(f"S3 upload FAILED! ERROR: {str(E)}")
        return {
            "status": "failed",
            "error": str(E)
        }
