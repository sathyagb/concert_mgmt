from django.urls import path
from .views import (
    homepage,
    EventListCreateAPIView,
    TicketListCreateAPIView,
    google_sheet_update,
)

urlpatterns = [
    path('', homepage, name='homepage'),
    path('api/events/', EventListCreateAPIView.as_view(), name='api_events'),
    path('api/tickets/', TicketListCreateAPIView.as_view(), name='api_tickets'),
    path('api/google_sheet_update/', google_sheet_update, name='google_sheet_update'),
]

