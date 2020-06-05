import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rooms.models import Room
from rooms.serializers import RoomSerializer
from .serializers import UserSerializer
from .models import User
from .permissions import IsSelf


# API에서 우리는 URL이 필요한데, 우리가 누군지 알기 위해서 우리의 PROFILE이 필요함.
# 내 프로필과 유저 프로필을 분리한 이유는 유저 프로필은 유저의 아이디를 알아야 접근할 수 있는데
# 앱 상에서는 USER ID를 알 수 없다. 그래서 /me URL이 필요함. 아이디를 모르더라도 접근할 수 있도록.
# ?? 무슨소릴까.. 항상 앱 개발자처럼 생각해야 한다? 프론트 엔드처럼?? 프론트 엔드에서는 모른다는 얘긴가..


class UserViewSet(ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):

        if self.action == "list":
            permission_classes = [permissions.IsAdminUser]
        elif (
            self.action == "create"
            or self.action == "retrieve"
            or self.action == "favs"
        ):
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsSelf]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["post"])
    def login(request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if user is not None:
            # 절대 절대! 민감한 정보를 jwt에 담아서는 안됨.
            # jwt.io에서 누구나 암호를 풀 수 있다면 이걸 왜 사용하는 거지?
            # 서버는 token을 받으면 볼 수 있는데, 서버는 token에 어떠한 변경사항이 하나라도 있었는지를 판단함.
            # 우리가 신경쓰는 부분은 그 누구도 우리 token을 건들지 않았다는 것을 확인하는 것임.
            encoded_jwt = jwt.encode(
                {"pk": "user.pk"}, settings.SECRET_KEY, algorithm="HS256"
            )
            return Response(data={"token": encoded_jwt})
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # detail=True이면 자동으로 pk를 보내줌
        @action(detail=True)
        def favs(self, request, pk):
            user = self.get_object()
            serializer = RoomSerializer(user.favs.all(), many=True).data
            return Response(serializer)

        @favs.mapping.put
        def toggle_favs(self, request, pk):
            user = self.get_object()

            if pk is not None:
                try:
                    room = Room.objects.get(pk=pk)
                    if room in user.favs.all():
                        user.favs.remove(room)
                    else:
                        user.favs.add(room)
                    # Response를 하지 않고 진행하면 실행이 잘 됐어도 마지막 400을 return함
                    return Response()
                except Room.DoesNotExist:
                    pass
            return Response(status=status.HTTP_400_BAD_REQUEST)


# DB의 state를 바꾸는 동작은 POST임.
# 2개 이상의 api 동작이 있을 때는 클래스가 좋음.
# class FavsView
