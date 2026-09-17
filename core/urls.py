from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("xizmatlar/", views.services, name="services"),
    path("xizmatlar/<slug:direction_slug>/", views.direction, name="direction"),
    path("xizmatlar/<slug:direction_slug>/<slug:slug>/", views.service, name="service"),
    path("reestr/", views.registry, name="registry"),
    path("hujjatlar/", views.credentials, name="credentials"),
    path("qonunchilik/", views.legislation, name="legislation"),
    path("yangiliklar/", views.news, name="news"),
    path("yangiliklar/<slug:slug>/", views.post, name="post"),
    path("tashkilot/", views.company, name="company"),
    path("tashkilot/mutaxassislar/", views.team, name="team"),
    path("tashkilot/asboblar/", views.instruments, name="instruments"),
    path("tashkilot/rekvizitlar/", views.requisites, name="requisites"),
    path("aloqa/", views.home, name="contact"),
    path("murojaat/", views.home, name="request"),
    path("api/compliance/", views.home, name="compliance_check"),
    path("api/energy-estimate/", views.home, name="energy_estimate"),
]
