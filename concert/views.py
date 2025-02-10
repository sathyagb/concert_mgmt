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
            logger.info("Received payload: %s", json.dumps(payload, indent=2))
        except Exception as e:
            logger.error("Invalid JSON: %s", e)
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        # Expecting keys: 'sheet' and 'data'
        sheet_name = payload.get("sheet")
        record = payload.get("data")

        if not sheet_name or not record:
            logger.error("Missing sheet name or data in payload.")
            return JsonResponse({"error": "Missing sheet name or data"}, status=400)

        # Process based on which sheet was edited
        if sheet_name == "Events":
            # Expect record format: [external_id, title, date, location, description, ...]
            try:
                external_id = str(record[0])
                title = record[1]
                date = record[2]
                location = record[3]
                description = record[4]
            except IndexError:
                logger.error("Event record is missing expected fields.")
                return JsonResponse({"error": "Event record missing fields"}, status=400)

            event, created = Event.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "title": title,
                    "date": date,
                    "location": location,
                    "description": description
                }
            )
            logger.info("Updated Event: %s", event.external_id)

        elif sheet_name == "Tickets":
            # Expect record format: [external_id, event_external_id, price, category, ...]
            try:
                external_id = str(record[0])
                event_external_id = str(record[1])
                price = record[2]
                category = record[3].strip() if record[3] else ""
            except IndexError:
                logger.error("Ticket record is missing expected fields.")
                return JsonResponse({"error": "Ticket record missing fields"}, status=400)

            try:
                event = Event.objects.get(external_id=event_external_id)
            except Event.DoesNotExist:
                logger.warning("Event with external_id %s not found. Skipping ticket %s.",
                               event_external_id, external_id)
                return JsonResponse({"warning": "Event not found"}, status=200)

            ticket, created = Ticket.objects.update_or_create(
                external_id=external_id,
                defaults={"event": event, "price": price, "category": category}
            )
            logger.info("Updated Ticket: %s", ticket.external_id)

        else:
            logger.error("Unrecognized sheet name: %s", sheet_name)
            return JsonResponse({"error": "Unrecognized sheet name"}, status=400)

        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)
    
# -- Standalone Frontend Web Page --

def homepage(request):
    return render(request, 'concert/index.html')