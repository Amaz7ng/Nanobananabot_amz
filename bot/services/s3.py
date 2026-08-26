import uuid
from io import BytesIO
from miniopy_async import Minio
from bot.config import config

s3_client = Minio(
    endpoint=config.MINIO_ENDPOINT,
    access_key=config.MINIO_ROOT_USER,
    secret_key=config.MINIO_ROOT_PASSWORD,
    secure=False
)

BUCKET_NAME = "images"

async def upload_photo_to_minio(photo_bytes: BytesIO) -> str:
    found = await s3_client.bucket_exists(BUCKET_NAME)
    if not found:
        await s3_client.make_bucket(BUCKET_NAME)
        policy = f'''{{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Effect": "Allow",
                    "Principal": {{"AWS": ["*"]}},
                    "Action": ["s3:GetObject"],
                    "Resource": ["arn:aws:s3:::{BUCKET_NAME}/*"]
                }}
            ]
        }}'''
        await s3_client.set_bucket_policy(BUCKET_NAME, policy)

    file_name = f"{uuid.uuid4()}.jpg"
    
    photo_bytes.seek(0)
    file_length = photo_bytes.getbuffer().nbytes
    
    await s3_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=file_name,
        data=photo_bytes,
        length=file_length,
        content_type="image/jpeg"
    )

    public_url = f"http://{config.MINIO_PUBLIC_DOMAIN}/{BUCKET_NAME}/{file_name}"
    return public_url