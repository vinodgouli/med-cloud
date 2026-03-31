# utils.py
from cryptography.fernet import Fernet
from io import BytesIO
import boto3
from botocore.exceptions import ClientError
from cryptography.fernet import InvalidToken
from django.conf import settings

def generate_key():
    return Fernet.generate_key()  # 32-byte urlsafe base64

def encrypt_file(file_obj, key: bytes) -> bytes:
    """
    Encrypt file content using Fernet.
    file_obj: BytesIO or any file-like object, or raw bytes.
    """
    fernet = Fernet(key)
    # Ensure we read from start if it's a file-like
    if hasattr(file_obj, 'seek'):
        file_obj.seek(0)
    data = file_obj.read() if hasattr(file_obj, 'read') else file_obj
    return fernet.encrypt(data)

def decrypt_file(ciphertext: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(ciphertext)

# accounts/decryption_utils.py



def decrypt_bytes(encrypted_bytes, key):
    """
    Decrypt encrypted bytes using a Fernet key.
    
    :param encrypted_bytes: Bytes of the encrypted file
    :param key: Fernet key (bytes or str)
    :return: Decrypted bytes
    :raises InvalidToken: if decryption fails
    """
    if isinstance(key, str):
        key = key.encode()
    fernet = Fernet(key)
    try:
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        return decrypted_bytes
    except InvalidToken:
        raise InvalidToken("Decryption failed: wrong key or corrupted file.")


def upload_to_s3(encrypted_bytes: bytes, bucket_name: str, s3_key: str):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    s3.upload_fileobj(BytesIO(encrypted_bytes), bucket_name, s3_key)

def double_decrypt_bytes(encrypted_bytes, key):
    """
    Decrypts a file that has been encrypted twice with the same Fernet key.
    """
    if isinstance(key, str):
        key = key.encode()
    fernet = Fernet(key)
    
    try:
        # First decryption
        first_decrypt = fernet.decrypt(encrypted_bytes)
        # Second decryption
        second_decrypt = fernet.decrypt(first_decrypt)
        return second_decrypt
    except InvalidToken:
        raise InvalidToken("Decryption failed: file might be corrupted or wrong key.")

def download_from_s3(bucket_name, key):
    """
    Downloads a file from S3 and returns raw bytes.
    """
    s3 = boto3.client('s3')
    try:
        obj = s3.get_object(Bucket=bucket_name, Key=key)
        data = obj['Body'].read()  # ✅ This gives raw bytes
        return data
    except ClientError as e:
        raise Exception(f"S3 download error: {e}")

