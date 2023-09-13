from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.
'''
Django 为所有的model 都添加一个名为objects 的 Manager，
用于与数据库交互
'''

class TaggedItemManager(models.Manager):
    def get_tags_for(self, obj_type, obj_id):
        content_type = ContentType.objects.get_for_model(obj_type)
        return TaggedItem.objects.select_related('tag').filter(content_type=content_type, object_id=obj_id)
 
class Tag(models.Model):
    label = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.label

class TaggedItem(models.Model):

    '''
    重新定义Manager，因为如果要进行泛型确定：
    content_type = ContentType.objects.get_for_model(Product)
    queryset = TaggedItem.objects.select_related('tag').filter(content_type=content_type,object_id=1)
    那么能不能变成-》TaggedItem.objects.get_tags_for(Product,1)
    '''
    objects = TaggedItemManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    
    '''
    实际上是product = models.ForeignKey(Product),
    但是为了能够泛型表示，所以这样表示
    '''
    content_type = models.ForeignKey(ContentType,on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()