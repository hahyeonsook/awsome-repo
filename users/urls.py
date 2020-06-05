from rest_framework.routers import BaseRouter
from . import views

app_name = "users"

router = BaseRouter()
router.register("", views.UserViewSet)

urlpatterns = router.urls

# 기능을 만들기 전에 url 먼저 짬.
# 모델별 기능? 작동을 먼저짬 GET, POST 등
# View의 순서와 url 순서가 일치해야 함.
