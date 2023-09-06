from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from store.models import Customer

# 需在apps.py那里引入，否则不会handler
# 在User每次创建完，就创建Customer
@receiver(post_save, sender=settings.AUTH_USER_MODEL)   
def create_customer_for_new_user(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance']) # instance指实例