# to handle user signup and login.
from django.contrib.auth.models import User
from rest_framework import serializers

from .models import FriendRequest, Block

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()



# to include a serializer for user search:

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Include fields to be displayed in search results


# serializers for handling friend requests and blocking.

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'status']
        read_only_fields = ['from_user', 'timestamp', 'status']

    def validate_to_user(self, value):
        # Prevent users from sending friend requests to themselves
        if self.context['request'].user == value:
            raise serializers.ValidationError("You cannot send a friend request to yourself.")
        return value

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'blocker', 'blocked', 'timestamp']
        read_only_fields = ['blocker', 'timestamp']


# to Add Serializer for UserActivity
from .models import UserActivity

class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'user', 'activity_type', 'description', 'timestamp']
        read_only_fields = ['user', 'activity_type', 'description', 'timestamp']
