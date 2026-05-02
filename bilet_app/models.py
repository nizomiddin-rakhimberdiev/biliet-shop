import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fa-star')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Event(models.Model):
    title       = models.CharField(max_length=200)
    category    = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    venue       = models.CharField(max_length=200)
    city        = models.CharField(max_length=100, default='Toshkent')
    event_date  = models.DateTimeField()
    description = models.TextField()
    image       = models.ImageField(upload_to='events/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.event_date > timezone.now()

    @property
    def min_price(self):
        types = self.ticket_types.filter(available_seats__gt=0)
        if types.exists():
            return types.order_by('price').first().price
        return None


class TicketType(models.Model):
    event           = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_types')
    name            = models.CharField(max_length=100)
    price           = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats     = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.event.title} — {self.name}'

    @property
    def is_available(self):
        return self.available_seats > 0

    @property
    def sold_percent(self):
        if self.total_seats == 0:
            return 0
        sold = self.total_seats - self.available_seats
        return int(sold / self.total_seats * 100)


class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Tasdiqlangan'),
        ('cancelled', 'Bekor qilindi'),
        ('used',      'Ishlatilgan'),
    ]

    user         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    ticket_type  = models.ForeignKey(TicketType, on_delete=models.CASCADE, related_name='bookings')
    quantity     = models.PositiveIntegerField(default=1)
    booking_code = models.CharField(max_length=16, unique=True, editable=False)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    phone        = models.CharField(max_length=20)
    created_at   = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        return self.ticket_type.price * self.quantity

    @property
    def event(self):
        return self.ticket_type.event

    def __str__(self):
        return f'{self.booking_code} — {self.user.username}'


class Profil(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username
