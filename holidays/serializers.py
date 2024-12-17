from rest_framework import serializers

class HolidaySerializer(serializers.Serializer):
    name = serializers.CharField()
    date = serializers.CharField()
    description = serializers.CharField()
