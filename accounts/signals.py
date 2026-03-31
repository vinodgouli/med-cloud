from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, EncryptionKey
from Crypto.Random import get_random_bytes

@receiver(post_save, sender=User)
def create_encryption_key(sender, instance, created, **kwargs):
    if created and instance.role == 'patient':
        EncryptionKey.objects.create(user=instance, key=get_random_bytes(32))
