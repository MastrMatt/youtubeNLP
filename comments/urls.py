from django.urls import path
from django.urls import include

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("<str:video_id>", views.comments_analysis_view, name="comments_analysis_view"),
]
