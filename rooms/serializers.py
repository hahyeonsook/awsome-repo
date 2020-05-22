from rest_framework import serializers
from users.serializers import UserSerializer
from .models import Room


class ReadRoomSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = Room
        exclude = ("modified",)


class WriteRoomSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=140)
    address = serializers.CharField(max_length=140)
    price = serializers.IntegerField()
    beds = serializers.IntegerField(default=1)
    lat = serializers.DecimalField(max_digits=10, decimal_places=6)
    lng = serializers.DecimalField(max_digits=10, decimal_places=6)
    bedrooms = serializers.IntegerField(default=1)
    bathrooms = serializers.IntegerField(default=1)
    check_in = serializers.TimeField(default="00:00:00")
    check_out = serializers.TimeField(default="00:00:00")
    instant_book = serializers.BooleanField(default=False)

    def create(self, validated_data):
        return Room.objects.create(**validated_data)

    def validate(self, data):
        # update
        if self.instance:
            check_in = data.get("check_in", self.instance.check_in)
            check_out = data.get("check_out", self.instance.check_out)
        # create
        else:
            check_in = data.get("check_in")
            check_out = data.get("check_out")
            if check_in == check_out:
                raise serializers.ValidationError("Not enough time between changes")
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", self.instance.name)
        instance.address = validated_data.get("address", self.instance.address)
        instance.price = validated_data.get("price", self.instance.price)
        instance.beds = validated_data.get("beds", self.instance.beds)
        instance.lat = validated_data.get("lat", self.instance.lat)
        instance.lng = validated_data.get("lng", self.instance.lng)
        instance.bedrooms = validated_data.get("bedrooms", self.instance.bedrooms)
        instance.bathrooms = validated_data.get("bathrooms", self.instance.bathrooms)
        instance.check_in = validated_data.get("check_in", self.instance.check_in)
        instance.check_out = validated_data.get("check_out", self.instance.check_out)
        instance.instant_book = validated_data.get(
            "instant_book", self.instance.instant_book
        )
        instance.save()
        return instance
