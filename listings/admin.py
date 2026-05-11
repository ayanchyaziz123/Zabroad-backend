from django.contrib import admin
from .models import Listing, JobDetail, HousingDetail, MarketplaceDetail, EventDetail, EventRSVP, SavedListing


class JobDetailInline(admin.StackedInline):
    model = JobDetail
    extra = 0


class HousingDetailInline(admin.StackedInline):
    model = HousingDetail
    extra = 0


class MarketplaceDetailInline(admin.StackedInline):
    model = MarketplaceDetail
    extra = 0


class EventDetailInline(admin.StackedInline):
    model = EventDetail
    extra = 0


_INLINE_MAP = {
    'job':         JobDetailInline,
    'housing':     HousingDetailInline,
    'marketplace': MarketplaceDetailInline,
    'event':       EventDetailInline,
}


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display  = ('title', 'listing_type', 'posted_by', 'home_country', 'plan', 'is_boosted', 'is_active', 'created_at')
    list_filter   = ('listing_type', 'plan', 'is_boosted', 'is_active', 'home_country')
    search_fields = ('title', 'description', 'location', 'posted_by__username')

    def get_inlines(self, request, obj=None):
        if obj and obj.listing_type in _INLINE_MAP:
            return [_INLINE_MAP[obj.listing_type]]
        return []


@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ('event', 'user', 'created_at')


@admin.register(SavedListing)
class SavedListingAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
