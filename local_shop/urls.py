from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.ShopListCreateView.as_view(),        name='shop_list'),
    path('my/',                                 views.MyShopView.as_view(),                name='my_shops'),
    path('<int:pk>/',                           views.ShopDetailView.as_view(),            name='shop_detail'),
    path('<int:shop_pk>/products/',             views.ShopProductListCreateView.as_view(), name='shop_products'),
    path('<int:shop_pk>/products/<int:pk>/',    views.ShopProductDetailView.as_view(),     name='shop_product_detail'),
]
