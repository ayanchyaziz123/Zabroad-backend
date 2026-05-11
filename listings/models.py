from django.db import models
from django.contrib.auth.models import User
from zabroad_backend.validators import validate_image_size, validate_image_type


class Listing(models.Model):
    TYPE_JOB         = 'job'
    TYPE_HOUSING     = 'housing'
    TYPE_MARKETPLACE = 'marketplace'
    TYPE_EVENT       = 'event'

    TYPE_CHOICES = [
        (TYPE_JOB,         'Job'),
        (TYPE_HOUSING,     'Housing'),
        (TYPE_MARKETPLACE, 'Marketplace'),
        (TYPE_EVENT,       'Event'),
    ]
    PLAN_CHOICES = [
        ('free',     'Free'),
        ('standard', 'Standard'),
        ('premium',  'Premium'),
    ]

    posted_by    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    listing_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    title        = models.CharField(max_length=200)
    description  = models.TextField()
    location     = models.CharField(max_length=200, blank=True)
    category     = models.CharField(max_length=50, blank=True)
    plan         = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    home_country = models.CharField(max_length=100, blank=True, db_index=True)
    country_flag = models.CharField(max_length=10, blank=True)
    latitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    image        = models.ImageField(upload_to='listings/', null=True, blank=True, validators=[validate_image_size, validate_image_type])
    is_active    = models.BooleanField(default=True, db_index=True)
    is_boosted   = models.BooleanField(default=False, db_index=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes  = [
            models.Index(fields=['listing_type', 'is_active', '-created_at']),
            models.Index(fields=['home_country', 'listing_type', 'is_active']),
        ]

    def __str__(self):
        return f'[{self.listing_type}] {self.title}'


class JobDetail(models.Model):
    listing     = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='job')
    company     = models.CharField(max_length=200)
    posted_from = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.listing.title} @ {self.company}'


class HousingDetail(models.Model):
    listing     = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='housing')
    price       = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency    = models.CharField(max_length=3, default='USD')
    posted_from = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'{self.listing.title} — {self.price}'


class MarketplaceDetail(models.Model):
    listing  = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='marketplace')
    price    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')

    def __str__(self):
        return f'{self.listing.title} — {self.price}'


class EventDetail(models.Model):
    listing  = models.OneToOneField(Listing, on_delete=models.CASCADE, related_name='event_detail')
    date     = models.DateTimeField()
    is_free  = models.BooleanField(default=True)
    price    = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    link     = models.URLField(blank=True, default='')

    class Meta:
        ordering = ['date']

    @property
    def rsvp_count(self):
        # Use .annotate(rsvp_count=Count('rsvps')) in list views to avoid N+1
        return self.rsvps.count()

    def __str__(self):
        return f'{self.listing.title} — {self.date.strftime("%b %d")}'


class EventRSVP(models.Model):
    event      = models.ForeignKey(EventDetail, on_delete=models.CASCADE, related_name='rsvps')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listing_rsvps')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'user'], name='unique_event_rsvp')
        ]

    def __str__(self):
        return f'{self.user.username} → {self.event}'


class SavedListing(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_listings')
    listing    = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'listing'], name='unique_saved_listing')
        ]

    def __str__(self):
        return f'{self.user.username} saved {self.listing}'
