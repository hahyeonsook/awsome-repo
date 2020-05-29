from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserSerializer
from .models import User
from rooms.models import Room
from rooms.serializers import RoomSerializer

# API에서 우리는 URL이 필요한데, 우리가 누군지 알기 위해서 우리의 PROFILE이 필요함.
# 내 프로필과 유저 프로필을 분리한 이유는 유저 프로필은 유저의 아이디를 알아야 접근할 수 있는데
# 앱 상에서는 USER ID를 알 수 없다. 그래서 /me URL이 필요함. 아이디를 모르더라도 접근할 수 있도록.
# ?? 무슨소릴까.. 항상 앱 개발자처럼 생각해야 한다? 프론트 엔드처럼?? 프론트 엔드에서는 모른다는 얘긴가..


class UsersView(APIView):
    def post(self, request):
        serializer = UserSerializer(request.data)
        if serializer.is_valid():
            new_user = serializer.save()
            return Response(UserSerializer(new_user))
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DB의 state를 바꾸는 동작은 POST임.
# 2개 이상의 api 동작이 있을 때는 클래스가 좋음.
class FavsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = RoomSerializer.get(user.favs.all(), many=True)
        return Response(serializer)

    # favs를 create하는 게 아니라 update하는 것이므로 put
    def put(self, request):
        pk = request.data.get("pk", None)
        user = request.user
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


@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        return Response(UserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
