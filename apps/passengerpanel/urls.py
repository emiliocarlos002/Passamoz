from django.urls import path

from .views import (
    create_booking,
    dashboard,
    my_trips,
    payments,
    favorites,
    toggle_favorite,
    promotions,
    help_page,
    about_page,
    my_tickets,
    payment,
    search_trips,
    submit_payment,
    ticket_detail,
    ticket_pdf,
    trip_detail,
)

app_name = "passengerpanel"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("minhas-viagens/", my_trips, name="my-trips"),
    path("pagamentos/", payments, name="payments"),
    path("favoritos/", favorites, name="favorites"),
    path("favoritos/<int:pk>/alternar/", toggle_favorite, name="toggle-favorite"),
    path("promocoes/", promotions, name="promotions"),
    path("ajuda/", help_page, name="help"),
    path("sobre/", about_page, name="about"),
    path("pesquisar/", search_trips, name="search"),
    path("viagem/<int:pk>/", trip_detail, name="trip-detail"),
    path("viagem/<int:pk>/reservar/", create_booking, name="create-booking"),
    path("pagamento/<uuid:reference>/", payment, name="payment"),
    path("pagamento/<uuid:reference>/enviar/", submit_payment, name="submit-payment"),
    path("bilhetes/", my_tickets, name="my-tickets"),
    path("bilhete/<uuid:reference>/", ticket_detail, name="ticket-detail"),
    path("bilhete/<uuid:reference>/pdf/", ticket_pdf, name="ticket-pdf"),
]
