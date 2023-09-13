
from django.db import transaction
from decimal import Decimal
from rest_framework import serializers

from .signals import order_created
from .models import CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage, Review, Cart

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']  # 如果不显式给予id,id自动生成/获取 
    '''
    在序列化过程中可不给出id，因为可从pk中获得
    反序列化过程中，则需给出对象的所有必须属性，id是会自动获取的
    '''
    # products_count的获取在view中获取
    products_count = serializers.IntegerField(read_only=True)
    

class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data): # 因为有外键所以需要重新进行 $ django不自动建立反向关系
        product_id = self.context['product_id'] # 在views中获取
        return ProductImage.object.create(product_id=product_id, **validated_data)
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection','images']

    price_with_tax = serializers.SerializerMethodField(
        method_name = 'calculate_tax'   # 因为不属于传统的命名方式
    )

    def calculate_tax(self, product:Product):
        return product.unit_price * Decimal(1.1) #統一兩邊類型


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'data', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id'] # 在view中传入
        return Review.objects.create(product_id=product_id, **validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name= 'get_total_price'  #实际上是不需要的，get_field名默认为method name
    )

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    
class CartSerializer(serializers.ModelSerializer):  #因为设置有unqiue_together,涉及到的字段（如果想进行转换）需要显示说明
    id = serializers.UUIDField(read_only=True) #也可以在Meta中表示read-only
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart: Cart):
        return sum([item.quantity * item.unit_price for item in cart.items.all()])
     
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


# 根据具体需求对其进行定制 POST时会携带product_id
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField() 

    # value为传入的product_id
    def validated_product_id(self, value): 
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('此商品并不存在')
        return value

    # 此时的save需对数据进行加减，并非简单地进行保存
    def save(self, **kwargs):
        cart_id = self.context['cart_id']

        '''
        若序列化器继承的是serializer.Modelserializer,
        那么serializer.data返回的是包含了序列化器中定义的所有的字段加上数据库定义的所有字段
        validated_data获取的是serializer序列化验证之后的数据, 
        数据类型为dict,对应的key是serializer中定义的字段名,
        对于高级的视图函数(CreateAPIView,RetrieveAPIView….)即是serializer.data
        '''
        product_id = self.validated_data['product_id']
        quantity =self.validated_data['quantity']

        try:
            cart_item=CartItem.objects.get(
                cart_id=cart_id, product_id=product_id
            )
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:   # 如果不存在
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity'] # POST需要对product_id的json转换为dict id会自动生成

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user_id','phone', 'birth_date', 'membership']

class OrderItemSerializer(serializers.ModelSerializer):
    product =SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id','product', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):    # 需要自己一个个写field, 但是因为需要关联很多类，需要重写function 所以用Serializer
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                '未找到此购物车'
            )
        if CartItem.objects.filter(cart_id=cart_id).count() == 0: # 不存在Cartitem
            raise serializers.ValidationError(
                '该购物车为空'
            )
        return cart_id
    
    def save(self, **kwargs):
        with transaction.atomic():  # 在進行一堆SQL工作時，若在操作一半出錯，这个能使操作回滚
            cart_id = self.validated_data['cart_id']
            customer = Customer.objects.get(
                user_id=self.context['user_id']
            )
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            
            #也可用循环直接创建 
            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.unit_price,
                    quantity = item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

 
            Cart.objects.filter(pk=cart_id).delete()

            # 如果成功创建就在终端打印order信息，反之则抛回错误
            order_created.send_robust(self.__class__, order=order)
            '''
            send()与send_robust()的不同之处在于当接收者函数抛出异常时如何处理一场。
            send()不会捕捉任何异常，它允许错误增加。因此当有错误时，不是所有的接收者都会得到信号的通知。
            send_robust()捕捉所有的错误（这里指由python的Exception类派生出来的错误），
            并且保证所有的接收者函数都能接到这个信号的通知。           
            如果一个错误出现，这个错误实例就会被包含在元组对里被返回给抛出这个错误的接收者。
            '''
           
            return order

        