from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from zabroad_backend.geo import apply_location_sort
from .models import LocalShop, ShopProduct
from .serializers import LocalShopSerializer, ShopProductSerializer


class IsShopOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, _view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        shop = obj if isinstance(obj, LocalShop) else obj.shop
        return shop.owner == request.user


class ShopListCreateView(generics.ListCreateAPIView):
    serializer_class   = LocalShopSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs     = LocalShop.objects.filter(is_active=True).select_related('owner').prefetch_related('products')
        params = self.request.query_params

        shop_type = params.get('type', '').strip()
        if shop_type and shop_type != 'all':
            qs = qs.filter(shop_type=shop_type)

        search = params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(shop_name__icontains=search) |
                Q(description__icontains=search) |
                Q(city__icontains=search) |
                Q(address__icontains=search)
            ).distinct()

        city = params.get('city', '').strip()
        if city:
            qs = qs.filter(Q(city__icontains=city))

        return apply_location_sort(qs, self.request)

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ShopDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = LocalShopSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShopOwnerOrReadOnly]
    queryset           = LocalShop.objects.filter(is_active=True).select_related('owner')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied()
        instance.is_active = False
        instance.save()


class MyShopView(generics.ListAPIView):
    serializer_class   = LocalShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LocalShop.objects.filter(owner=self.request.user, is_active=True).prefetch_related('products')

    def get_serializer_context(self):
        return {'request': self.request}


class ShopProductListCreateView(generics.ListCreateAPIView):
    serializer_class   = ShopProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_shop(self):
        return generics.get_object_or_404(LocalShop, pk=self.kwargs['shop_pk'], is_active=True)

    def get_queryset(self):
        return ShopProduct.objects.filter(
            shop_id=self.kwargs['shop_pk'],
            is_available=True,
        ).select_related('shop')

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        shop = self.get_shop()
        if shop.owner != self.request.user:
            raise PermissionDenied('Only the shop owner can add products.')
        serializer.save(shop=shop)


class ShopProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ShopProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsShopOwnerOrReadOnly]

    def get_queryset(self):
        return ShopProduct.objects.filter(shop_id=self.kwargs['shop_pk']).select_related('shop__owner')

    def get_serializer_context(self):
        return {'request': self.request}
