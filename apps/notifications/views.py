from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Notification


@login_required(login_url="/conta/entrar/")
def list_notifications(request):
    notifications = request.user.notifications.select_related("booking").all()
    return render(request, "notifications/list.html", {
        "notifications": notifications,
    })


@login_required(login_url="/conta/entrar/")
@require_POST
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("notifications:list")


@login_required(login_url="/conta/entrar/")
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect("notifications:list")
