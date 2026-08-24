from django.urls import path

from .views import (
    booking_list,
    dashboard,
    payment_account_toggle,
    payment_confirm,
    payment_reject,
    payment_accounts,
    route_create,
    route_delete,
    route_edit,
    route_list,
    subscription_list,
    trip_cancel,
    trip_create,
    trip_edit,
    trip_list,
    vehicle_create,
    vehicle_delete,
    vehicle_edit,
    vehicle_list,
)

app_name = "operatorpanel"

urlpatterns = [
    path("", dashboard, name="operator-dashboard"),
    path("rotas/", route_list, name="operator-route-list"),
    path("rotas/nova/", route_create, name="operator-route-create"),
    path("rotas/<int:pk>/editar/", route_edit, name="operator-route-edit"),
    path("rotas/<int:pk>/desativar/", route_delete, name="operator-route-delete"),
    path("viaturas/", vehicle_list, name="operator-vehicle-list"),
    path("viaturas/nova/", vehicle_create, name="operator-vehicle-create"),
    path("viaturas/<int:pk>/editar/", vehicle_edit, name="operator-vehicle-edit"),
    path("viaturas/<int:pk>/desativar/", vehicle_delete, name="operator-vehicle-delete"),
    path("viagens/", trip_list, name="operator-trip-list"),
    path("viagens/nova/", trip_create, name="operator-trip-create"),
    path("viagens/<int:pk>/editar/", trip_edit, name="operator-trip-edit"),
    path("viagens/<int:pk>/cancelar/", trip_cancel, name="operator-trip-cancel"),
    path("reservas/", booking_list, name="operator-booking-list"),
    path("pagamentos/", payment_accounts, name="operator-payment-accounts"),
    path("pagamentos/<int:pk>/alternar/", payment_account_toggle, name="operator-payment-account-toggle"),
    path("pagamentos/transacao/<int:pk>/confirmar/", payment_confirm, name="operator-payment-confirm"),
    path("pagamentos/transacao/<int:pk>/rejeitar/", payment_reject, name="operator-payment-reject"),
    path("mensalidades/", subscription_list, name="operator-subscriptions"),
]
