from django.urls import path
from .views import (
    HomeView, PassengerLoginView, PassengerLogoutView, PassengerPasswordChangeDoneView,
    PassengerPasswordChangeView, PassengerPasswordResetCompleteView, PassengerPasswordResetConfirmView,
    PassengerPasswordResetDoneView, PassengerPasswordResetView, PassengerRegisterView, account_settings,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("conta/cadastrar/", PassengerRegisterView.as_view(), name="register"),
    path("conta/entrar/", PassengerLoginView.as_view(), name="login"),
    path("conta/sair/", PassengerLogoutView.as_view(), name="logout"),
    path("conta/definicoes/", account_settings, name="account-settings"),
    path("conta/definicoes/senha/", PassengerPasswordChangeView.as_view(), name="password_change"),
    path("conta/definicoes/senha/concluido/", PassengerPasswordChangeDoneView.as_view(), name="password_change_done"),
    path("conta/recuperar/", PassengerPasswordResetView.as_view(), name="password_reset"),
    path("conta/recuperar/enviado/", PassengerPasswordResetDoneView.as_view(), name="password_reset_done"),
    path("conta/recuperar/<uidb64>/<token>/", PassengerPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("conta/recuperar/concluido/", PassengerPasswordResetCompleteView.as_view(), name="password_reset_complete"),
]
