from django.db.models import Max
from django.shortcuts import (
    get_object_or_404,  # shortcut to fetch an object or return 404 automatically
)
from rest_framework.decorators import (
    api_view,  # decorator for function-based views (FBV) in DRF
)
from rest_framework.response import (
    Response,  # DRF's Response (better than Django's HttpResponse for APIs)
)

from api.models import Order, Product  # import Product model
from api.serializers import (  # import serializer for Product model
    OrderSerializer,
    ProductSerializer,
    ProductInfoSerializer
)
from rest_framework import generics
# -------------------------------
# FUNCTION BASED VIEWS (FBV)
# -------------------------------

#!function based view for product list
# @api_view(["GET"])
# # @api_view ensures:
# # 1. Only listed HTTP methods are allowed (here, only GET).
# # 2. It converts the request into a DRF Request object (not plain Django HttpRequest).
# # 3. This enables features like .data, .query_params, authentication, parsers, etc.
# def product_list(request):
#     # ORM query → fetch all products from DB
#     products = Product.objects.all()

#     # Serialize data → convert queryset (Python objects) to JSON
#     # "many=True" because we’re serializing multiple products
#     serializer = ProductSerializer(products, many=True)

#     # DRF Response → automatically renders JSON + adds correct content-type headers
#     return Response(serializer.data)


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    # queryset = Product.objects.filter(stock__gt=0)  # only products in stock. this is for only generic view
    serializer_class = ProductSerializer
    

class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = 'product_id'  # default is 'pk', change if URL uses different name


# @api_view(["GET"])
# def product_detail(request, pk):
#     # get_object_or_404 → tries to fetch object by pk, if not found returns 404 response automatically
#     product = get_object_or_404(Product, pk=pk)

#     # Serialize single product (no need for many=True since it's just one object)
#     serializer = ProductSerializer(product)

#     return Response(serializer.data)


# @api_view(["GET"])
# def order_list(request):
#     # orders = Order.objects.all()
#     # orders = Order.objects.prefetch_related("items")
#     orders = Order.objects.prefetch_related("items", "items__product")
#     serializer = OrderSerializer(orders, many=True)
#     return Response(serializer.data)

class OrderListAPIView(generics.ListAPIView):
    # queryset = Order.objects.all()
    queryset = Order.objects.prefetch_related("items__product")
    # queryset = Product.objects.filter(stock__gt=0)  # only products in stock. this is for only generic view
    serializer_class = OrderSerializer

# Without optimization (19 queries total):
# [Orders] ---- 1 query
#    ├── [Items for Order1] ---- 1 query
#    ├── [Items for Order2] ---- 1 query
#    ├── [Items for Order3] ---- 1 query
#         ├── [Product for Item1] ---- 1 query
#         ├── [Product for Item2] ---- 1 query
#         ...
#         ├── [Product for Item6] ---- 1 query
# + User lookups + extras → 19

# With prefetch_related("items") (8 queries):
# [Orders] ---- 1 query
# [All Items] ---- 1 query
#    ├── [Product for Item1] ---- 1 query
#    ├── [Product for Item2] ---- 1 query
#    ...
#    ├── [Product for Item6] ---- 1 query
# = 8

# With prefetch_related("items__product") (3 queries):
# [Orders] ---- 1 query
# [All Items] ---- 1 query
# [All Products] ---- 1 query
# = 3 🎯

class UserOrderListAPIView(generics.ListAPIView):
    # queryset = Order.objects.all()
    queryset = Order.objects.prefetch_related("items__product")
    # queryset = Product.objects.filter(stock__gt=0)  # only products in stock. this is for only generic view
    serializer_class = OrderSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user = self.request.user)

@api_view(['GET'])
def product_info(request):
    products = Product.objects.all()
    serializer = ProductInfoSerializer({
        'products': products,
        'count': len(products),
        'max_price': products.aggregate(max_price = Max("price"))["max_price"]

    })
    return Response(serializer.data)


# -------------------------------
# NOTES & BEST PRACTICES
# -------------------------------
# 1. FBV (Function Based Views) are quick & simple, great for learning or small endpoints.
# 2. But for bigger projects, Class Based Views (CBV) are preferred because:
#    - They’re more organized (each HTTP method can be a separate method like get(), post(), put(), delete()).
#    - Easier to reuse and extend.
#    - Built-in mixins and generic views save boilerplate code.
#
# 3. DRF Request & Response vs Django HttpRequest/HttpResponse:
#    - DRF Request: adds .data (parsed JSON), .query_params, authentication info, etc.
#    - DRF Response: handles JSON/XML rendering + content negotiation automatically.
#
# 4. Serializer: Converts Django ORM models to JSON (for API response)
#    and JSON back to ORM models (for creating/updating).
#
# 5. For CRUD:
#    - GET: list/retrieve
#    - POST: create
#    - PUT/PATCH: update
#    - DELETE: delete
#
# 6. For production-level APIs, always add:
#    - Permissions (IsAuthenticated, IsAdminUser, etc.)
#    - Pagination for list endpoints
#    - Filtering & search
#    - Error handling / validation
