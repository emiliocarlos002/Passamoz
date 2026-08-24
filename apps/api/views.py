from django.http import JsonResponse
from django.views import View
from apps.trips.models import Trip


class HealthView(View):
    def get(self, request):
        return JsonResponse({"service": "passamoz-api", "status": "ok"})


class PublishedTripsView(View):
    def get(self, request):
        trips = (
            Trip.objects.filter(status=Trip.Status.PUBLISHED)
            .select_related("route", "transporter")
            .order_by("departure_at")
        )
        data = [
            {
                "id": trip.id,
                "operator": trip.transporter.name,
                "origin": trip.route.origin,
                "destination": trip.route.destination,
                "departure_at": trip.departure_at.isoformat(),
                "price": str(trip.price),
                "currency": trip.currency,
            }
            for trip in trips
        ]
        return JsonResponse({"results": data})
