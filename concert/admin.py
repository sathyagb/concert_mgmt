from django.contrib import admin

# Register your models here.
from .models import Event, Ticket

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location', 'description')
    search_fields = ('title',)

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('event', 'category', 'price')
    search_fields = ('category',)
