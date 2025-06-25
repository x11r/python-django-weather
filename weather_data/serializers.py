from rest_framework import serializers
from .models import Daily

class ArticleSerializer(serializers.ModelSerializer):
    class Mta:
        model = Daily
        fields = '__all__'
