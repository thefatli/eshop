from django.db.models.aggregates import Count
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermissiom
from .pagination import DefaultPagination
from .filters import ProductFilter
from .models import CartItem, Collection, Customer, Order, Product, OrderItem, ProductImage, Review, Cart
from .serializers import AddCartItemSerializer, CartSerializer, CollectionSerializer, CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer, ProductSerializer, ReviewSerializer, UpdateCartItemSerializer, UpdateOrderSerializer
from store import serializers
# Create your views here.

'''
最开始的view是：
from rest_framework.decorators import api_view
@api_view(['GET','POST']) 默认支持GET，支持POST则需添加
def product_list(request):
    if request.method == 'GET':
        queryset = Product.objects.all()
        serializers = ProductSerializer(queryset,many=True)
        return Response(serializers.data)
    elif request.method == 'POST':
        serializers = ProductSerializer(data=request.data)
        serializers.validated_data
        return Response('ok')

@api_view() 
def product_detail(request,id):
    product = get_object_or_404(Product, pk=id)
    serializers = ProductSerializer(product)
    return Response(serializers.data)

此时urls应该这样写：
path('xxx/<int:pk>/', views.product_detail, name='product_detail')

也有class:
from rest_framework,views import APIView
class ProductList(APIView):
    def get(self,request):
        queryset = Product.objects.all()
        serializers = ProductSerializer(queryset,many=True
        return Response(serializers.data)
    def post(self,request):
        serializers = ProductSerializer(data=request.data)
        serializers.validated_data
        return Response('ok')

urls同Viewset一样书写
'''

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request':self.request}
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error' : '因为涉及订单不予删除'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')
    ).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    #destroy的拓展一般包含删除前的操作&不得删除及时返回错误信息
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error':'因为内含一个及以上商品，该合集不得被删除'},status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self): # 若使用queryset,不能含有逻辑。重写这个方法则可以含有逻辑 
        return Review.objects.filter(product_id=self.kwargs['product_pk'])  # 这里之所以重写，是因为在queryset中无法访问self

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}    # 关键词传参一般是pk, 而不是id
    

class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__products').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemViewSet
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermissiom])   # detail=True -> 由带id的路由生成
    def history(self, request, pk): # 仅供展示
        return Response('ok')

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(
            user_id = request.user.id
        )
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer( # 因为创建Order是需要有不同的要求的，所以要调用Create...izer
            data=request.data,
            context={'user_id': self.request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order) #再重新对此（主要是其他的属性）进行序列化
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs['product_pk'])




