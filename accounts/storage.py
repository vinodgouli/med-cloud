from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class EncryptedS3Storage(S3Boto3Storage):
    default_acl = None
    querystring_auth = True

    def get_object_parameters(self, name):
        base = super().get_object_parameters(name)
        base.update({
            "ServerSideEncryption": "aws:kms",
            "SSEKMSKeyId": settings.AWS_S3_KMS_KEY_ID,
        })
        return base
