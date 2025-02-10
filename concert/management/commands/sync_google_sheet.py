import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.core.management.base import BaseCommand
from concert.models import Event, Ticket
from datetime import datetime
from concert_mgmt import settings


class Command(BaseCommand):
    help = "Sync data from Google Sheets to the CMS"

    def handle(self, *args, **options):
        # Using Django's BASE_DIR
        credentials_path = os.path.join(settings.BASE_DIR, 'credentials', 'concert_mgmt.json')
        self.stdout.write(self.style.NOTICE(f"Looking for credentials at: {credentials_path}"))

        if not os.path.exists(credentials_path):
            self.stdout.write(self.style.ERROR(f"Credentials file not found at {credentials_path}"))
            return
        
        # Defining the scope and authorize the client.
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading credentials file: {e}"))
            return
        
        client = gspread.authorize(creds)
        
        # Open the spreadsheet by name.
        try:
            spreadsheet = client.open("ConcertData")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Could not open spreadsheet: {e}"))
            return

        # --- Sync Events ---
        try:
            events_sheet = spreadsheet.worksheet("Events")
        except Exception as e:
            self.stdout.write(self.style.ERROR("Events worksheet not found."))
            return

        events_records = events_sheet.get_all_records()
        for record in events_records:
            external_id = str(record.get("external_id"))
            if not external_id:
                continue
            date_str = record.get("date")
            try:
                # Expect date in ISO format, e.g., "2025-03-01T20:00:00"
                date_obj = datetime.fromisoformat(date_str)
            except Exception as e:
                date_obj = None

            Event.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "title": record.get("title", ""),
                    "description": record.get("description", ""),
                    "date": date_obj,
                    "location": record.get("location", "")
                }
            )
        self.stdout.write(self.style.SUCCESS("Events synced successfully."))

        # --- Sync Tickets ---
        try:
            tickets_sheet = spreadsheet.worksheet("Tickets")
        except Exception as e:
            self.stdout.write(self.style.ERROR("Tickets worksheet not found."))
            return

        tickets_records = tickets_sheet.get_all_records()
        for record in tickets_records:
            external_id = str(record.get("external_id"))
            if not external_id:
                continue
            event_external_id = str(record.get("event"))
            try:
                event = Event.objects.get(external_id=event_external_id)
            except Event.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Event with external_id {event_external_id} not found. Skipping ticket {external_id}."))
                continue

            Ticket.objects.update_or_create(
                external_id=external_id,
                defaults={
                    "event": event,
                    "price": record.get("price", 0),
                    "category": record.get("category", "")
                }
            )
        self.stdout.write(self.style.SUCCESS("Tickets synced successfully."))
