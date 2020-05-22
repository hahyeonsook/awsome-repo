from django.urls import path
from . import views

app_name = "users"

# 기능을 만들기 전에 url 먼저 짬.
# 모델별 기능? 작동을 먼저짬 GET, POST 등
urlpatterns = [
    path("me/", views.MeView.as_view()),
    path("<int:pk>/", views.user_detail),
]
