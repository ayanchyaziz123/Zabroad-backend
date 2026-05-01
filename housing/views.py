from django.db.models import Case, When, Value, IntegerField
from rest_framework import generics, permissions
from .models import HousingListing
from .serializers import HousingListingSerializer


def apply_near_city(qs, near_city):
    if not near_city:
        return qs.order_by('-created_at')
    city_prefix = near_city.split(',')[0].strip()
    return qs.annotate(
        loc_score=Case(
            When(location__iexact=near_city,        then=Value(3)),
            When(location__istartswith=city_prefix, then=Value(2)),
            When(location__icontains=city_prefix,   then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).order_by('-loc_score', '-created_at')


class HousingListCreateView(generics.ListCreateAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs        = HousingListing.objects.filter(is_active=True).select_related('posted_by')
        country   = self.request.query_params.get('community')
        near_city = self.request.query_params.get('near_city', '').strip()
        if country:
            qs = qs.filter(home_country__iexact=country)
        return apply_near_city(qs, near_city)

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class HousingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = HousingListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset           = HousingListing.objects.filter(is_active=True)
