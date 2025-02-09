from rest_framework import serializers
from .models import Event, Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['external_id', 'price', 'category']

class EventSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True,) #creating many to one relationship between tickets and event
    class Meta:
        model = Event
        fields = ['external_id', 'title', 'date', 'location', 'description', 'tickets']
