from django.urls import path
from django.urls import include

from . import views


urlpatterns = [
    path("<str:video_id>", views.CommentList.as_view()),  
]