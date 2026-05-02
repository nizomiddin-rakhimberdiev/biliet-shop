from django.contrib import admin
from .models import Category, Event, TicketType, Booking, Profil


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'icon')
    search_fields = ('name',)


class TicketTypeInline(admin.TabularInline):
    model  = TicketType
    extra  = 3
    fields = ('name', 'price', 'total_seats', 'available_seats')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display   = ('id', 'title', 'category', 'venue', 'event_date', 'is_active')
    list_filter    = ('category', 'is_active', 'city')
    search_fields  = ('title', 'venue', 'city')
    list_editable  = ('is_active',)
    inlines        = [TicketTypeInline]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display  = ('id', 'event', 'name', 'price', 'total_seats', 'available_seats')
    list_filter   = ('event',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display   = ('booking_code', 'user', 'ticket_type', 'quantity', 'total_price', 'status', 'created_at')
    list_filter    = ('status', 'created_at')
    search_fields  = ('booking_code', 'user__username', 'phone')
    readonly_fields = ('booking_code',)

    @admin.display(description='Jami narx')
    def total_price(self, obj):
        return f"{obj.total_price} so'm"


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display  = ('id', 'user')
    search_fields = ('user__username',)
