from django.urls import path,include
from . import views

urlpatterns = [
    # path('products/',views.product_list),
    path('products/',views.ProductListAPIView.as_view()),
    path('products/info',views.product_info),
    # path('products/<int:pk>',views.product_detail), #!this syntax is for FBV
    # path('products/<int:pk>',views.ProductDetailAPIView.as_view()), #generally here it expects pk by default but if you want to use other name you can use lookup_field attribute in the view
    path('products/<int:product_id>',views.ProductDetailAPIView.as_view()),
    # path('orders/',views.order_list),
    path('orders/',views.OrderListAPIView.as_view()),
    path('user-orders/',views.UserOrderListAPIView.as_view(),name="user-orders"),
   path('silk/', include('silk.urls'))
]
