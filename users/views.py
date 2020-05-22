from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ReadUserSerializer, WriteUserSerializer
from .models import User

# API에서 우리는 URL이 필요한데, 우리가 누군지 알기 위해서 우리의 PROFILE이 필요함.
# 내 프로필과 유저 프로필을 분리한 이유는 유저 프로필은 유저의 아이디를 알아야 접근할 수 있는데
# 앱 상에서는 USER ID를 알 수 없다. 그래서 /me URL이 필요함. 아이디를 모르더라도 접근할 수 있도록.
# ?? 무슨소릴까.. 항상 앱 개발자처럼 생각해야 한다? 프론트 엔드처럼?? 프론트 엔드에서는 모른다는 얘긴가..


class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ReadUserSerializer(request.user).data)

    def put(self, request):
        serializer = WriteUserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
        return Response(ReadUserSerializer(user).data)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
