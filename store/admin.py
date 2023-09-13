from urllib.parse import urlencode
from django.contrib import admin,messages
from django.db.models.aggregates import Count
from django.db.models.query import QuerySet
from django.utils.html import format_html, urlencode
from django.urls import reverse

from . import models
# Register your models here.

class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory' # 分类器的名称
    parameter_name = 'inventory' # 所要操作的属性

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low'),  # <10在admin页面显示的是Low
        ]

    def queryset(self, request, queryset:QuerySet):
        if self.value() == '<10': # 如果点击Low
            return queryset.filter(inventory__lt=10)


'''
InlineModelAdmin类的作用在于，可以在Model A页面上编辑Model B表的字段，
这只需要A和B存在外键关系
'''
class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    readonly_fields = ['thumbnail']

    # 设置thumbnail的格式
    def thumbnail(self, instance):
        if instance.image.name != '':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
        return ''    

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    autocomplete_fields = ['collection']    # 自动补全，针对外键设置, 该外键必须设置有search_fields
    prepopulated_fields = {
        'slug': ['title']
    }
    actions = ['clear_inventory']
    inlines = [ProductImageInline]
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']

    def collection_title(self, product):
        return product.collection.title
    
    # 自己添加的列
    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0) # 返回更新的数量
        self.message_user(
            request,
            f'{updated_count} 个产品已更新',
            messages.ERROR
        )
    class Meta:
        css = {
            'all': ['store/styles.css']
        }

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ['featured_product']
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering='products_count') # 按照这个属性进行排序
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            })
        )
        return format_html('<a href="{}">{} Products</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders']
    list_editable = ['membership']
    list_per_page =10
    list_select_related = ['user']
    ordering = ['user__first_name', 'user__last_name']
    search_fields = ['first_name__istartwith', 'last_name__istartwith']
  
    @admin.display(ordering='orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist') # admin: app名_model名_page名
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
        }))
        return format_html('<a href="{}">{} Orders</a>', url, customer.orders_count) # 将转向那个url页面

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count=Count('order')
        )

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0   # 控制表单集在初始表格之外显示的额外表单数量，默认为 3 个

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']  