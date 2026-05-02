"""
Shared location-based sorting utility.

Priority:
  1. Real GPS coords (lat/lng) → squared Euclidean distance (SQLite-safe, same ordering as true distance)
  2. City text (near_city) → Case/When relevance score
  3. Neither → default ordering

All views call `apply_location_sort(qs, request, default_order)`.
"""
from django.db.models import Case, When, Value, IntegerField, FloatField
from django.db.models.expressions import RawSQL
from rest_framework.exceptions import ValidationError

_DIST_SQL = """
    CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL
    THEN (CAST(latitude  AS REAL) - %s) * (CAST(latitude  AS REAL) - %s)
       + (CAST(longitude AS REAL) - %s) * (CAST(longitude AS REAL) - %s)
    ELSE 999999.0 END
"""


def _parse_coords(request):
    """Return (lat, lng) floats from query params, or (None, None)."""
    raw_lat = request.query_params.get('lat')
    raw_lng = request.query_params.get('lng')
    if raw_lat is None or raw_lng is None:
        return None, None
    try:
        lat = float(raw_lat)
        lng = float(raw_lng)
    except (ValueError, TypeError):
        raise ValidationError({'detail': 'lat and lng must be numeric.'})
    if not (-90 <= lat <= 90):
        raise ValidationError({'detail': 'lat must be between -90 and 90.'})
    if not (-180 <= lng <= 180):
        raise ValidationError({'detail': 'lng must be between -180 and 180.'})
    return lat, lng


def apply_location_sort(qs, request, default_order=('-created_at',), extra_order=()):
    """
    Sort a queryset by proximity.

    `extra_order` lets callers inject additional sort fields after distance
    (e.g. ('-plan',) for healthcare which sorts by plan tier too).
    """
    lat, lng = _parse_coords(request)
    near_city = request.query_params.get('near_city', '').strip()

    if lat is not None:
        annotated = qs.annotate(
            distance=RawSQL(_DIST_SQL, (lat, lat, lng, lng), output_field=FloatField())
        )
        return annotated.order_by('distance', *extra_order, '-created_at')

    if near_city:
        city_prefix = near_city.split(',')[0].strip()
        annotated = qs.annotate(
            loc_score=Case(
                When(location__iexact=near_city,        then=Value(3)),
                When(location__istartswith=city_prefix, then=Value(2)),
                When(location__icontains=city_prefix,   then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        )
        return annotated.order_by('-loc_score', *extra_order, '-created_at')

    return qs.order_by(*default_order)
