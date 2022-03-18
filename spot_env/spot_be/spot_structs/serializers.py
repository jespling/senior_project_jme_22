from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('pk', 'user', 'email')

#next start mocking up a playlist/track serializer to convert track data

