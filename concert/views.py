from django.shortcuts import render
# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from .models import Event, Ticket
from .serializers import EventSerializer, TicketSerializer
import logging

logger = logging.getLogger(__name__)

# -- API Endpoints --

class EventListCreateAPIView(generics.ListCreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class TicketListCreateAPIView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

@csrf_exempt
def google_sheet_update(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            logger.info("Received payload: %s", payload) 
        except Exception as e:
            logger.error("Invalid JSON: %s", e)
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        events_data = payload.get("events", [])
        tickets_data = payload.get("tickets", [])

        # Process event data
        for event_data in events_data:
            external_id = event_data.get("external_id")
            if not external_id:
                continue
            Event.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "title": event_data.get("title", ""),
                    "date": event_data.get("date"),
                    "location": event_data.get("location", ""),
                    "description": event_data.get("description", "")
                }
            )

        # Process tickets data
        for ticket_data in tickets_data:
            external_id = ticket_data.get("external_id")
            if not external_id:
                continue
            event_external_id = ticket_data.get("event")
            if not event_external_id:
                continue
            try:
                event = Event.objects.get(external_id=event_external_id)
            except Event.DoesNotExist:
                continue
            Ticket.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "event": event,
                    "price": ticket_data.get("price", 0),
                    "category": ticket_data.get("category", "")
                }
            )

        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)



# -- Standalone Frontend Web Page --

def homepage(request):
    return render(request, 'concert/index.html')