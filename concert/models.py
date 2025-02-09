from django.db import models

# Create your models here.
class Event(models.Model):
    # external_id links this event with a row in Google Sheets
    external_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    # external_id links this ticket with a row in Google Sheets
    external_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    event = models.ForeignKey(Event, related_name='tickets', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category} ticket for {self.event.title}"