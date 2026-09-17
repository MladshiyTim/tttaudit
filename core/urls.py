from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("xizmatlar/", views.home, name="services"),
    path("xizmatlar/<slug:direction_slug>/", views.home, name="direction"),
    path("xizmatlar/<slug:direction_slug>/<slug:slug>/", views.home, name="service"),
    path("reestr/", views.home, name="registry"),
    path("hujjatlar/", views.home, name="credentials"),
    path("qonunchilik/", views.home, name="legislation"),
    path("yangiliklar/", views.home, name="news"),
    path("yangiliklar/<slug:slug>/", views.home, name="post"),
    path("tashkilot/", views.home, name="company"),
    path("tashkilot/mutaxassislar/", views.home, name="team"),
    path("tashkilot/asboblar/", views.home, name="instruments"),
    path("tashkilot/rekvizitlar/", views.home, name="requisites"),
    path("aloqa/", views.home, name="contact"),
    path("murojaat/", views.home, name="request"),
]
