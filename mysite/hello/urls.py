from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            authentication_form=views.CareTrackAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("staff/", views.staff_dashboard, name="staff_dashboard"),
    path("inventory/", views.available_inventory, name="available_inventory"),
    path("requested/", views.requested_items, name="requested_items"),
    path("distributed/", views.distributed_items, name="distributed_items"),
]
