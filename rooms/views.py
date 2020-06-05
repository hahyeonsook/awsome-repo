from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from .models import Room
from .serializers import RoomSerializer


class OwnPagination(PageNumberPagination):
    page_size = 20


class RoomsView(APIView):
    def get(self, request):
        paginator = OwnPagination()
        rooms = Room.objects.all()
        results = paginator.paginate_queryset(rooms, request)
        serializer = RoomSerializer(results, many=True, context={"request": request})
        # 아래처럼 해주는 이유는 Response()를 해줘도 paginator가 작동하지만
        # prev_page, next_page와 같은 기능을 사용할 수 없기 때문에 get_paginated_response()를 사용함.
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            room = serializer.save(user=request.user)
            room_serializer = RoomSerializer(room).data
            return Response(data=room_serializer, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def room_search(request):
    max_price = request.GET.get("max_price", None)
    min_price = request.GET.get("min_price", None)
    beds = request.GET.get("beds", None)
    bedrooms = request.GET.get("bedrooms", None)
    bathromms = request.GET.get("bathrooms", None)
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)
    filter_kwargs = {}

    if max_price is not None:
        filter_kwargs["price_lte"] = max_price
    if min_price is not None:
        filter_kwargs["price_gte"] = min_price
    if beds is not None:
        filter_kwargs["beds_gte"] = beds
    if bedrooms is not None:
        filter_kwargs["bedrooms_gte"] = bedrooms
    if bathromms is not None:
        filter_kwargs["bathrooms_gte"] = bathromms

    paginator = OwnPagination()

    if lat is not None and lng is not None:
        filter_kwargs["lat__gte"] = float(lat) - 0.005
        filter_kwargs["lat__lte"] = float(lat) + 0.005
        filter_kwargs["lng__gte"] = float(lng) - 0.005
        filter_kwargs["lng__lte"] = float(lng) + 0.005

    try:
        rooms = Room.objects.filter(**filter_kwargs)
    except ValueError:
        rooms = Room.objects.all()

    results = paginator.paginate_queryset(rooms, request)
    serialzer = RoomSerializer(results, many=True)
    return paginator.get_paginated_response(serializer.data)


class RoomView(APIView):
    def get_room_or_none(self, pk):
        try:
            room = Room.objects.get(pk=pk)
            return room
        except Room.DoesNotExist:
            return None

    def get(self, request, pk):
        room = self.get_room_or_none(pk)
        if room is not None:
            serializer = RoomSerializer(room).data
            return Response(serializer)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        room = self.get_room_or_none(pk)
        if room is not None:
            if room.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = RoomSerializer(room, request.data, partial=True)
            if serializer.is_valid():
                room = serializer.save()
                return Response(RoomSerializer(room).data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response()
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        room = self.get_room_or_none(pk)
        if room.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        if room is not None:
            room.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
