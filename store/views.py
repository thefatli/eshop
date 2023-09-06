from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from store import serializers

from .models import Product
from .serializers import ProductSerializer
# Create your views here.

class ProductViewSet(ModelViewSet):
    queryset = Product.objetcs.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
