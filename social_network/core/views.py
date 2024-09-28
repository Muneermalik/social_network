from django.shortcuts import render

# to handle user signup and login using DRF.

# core/views.py
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSignupSerializer, UserLoginSerializer

from rest_framework.permissions import AllowAny

class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer

    permission_classes = [AllowAny]  # This allows anyone to access the signup endpoint

class UserLoginView(APIView):

    permission_classes = [AllowAny]  # This allows anyone to access the login endpoint

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


# to Create the User Search View:

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .serializers import UserSerializer

class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            # Search for users by email or username (case-insensitive)
            return User.objects.filter(
                email__icontains=query
            ) | User.objects.filter(
                username__icontains=query
            )
        return super().get_queryset()



# views for sending, accepting, rejecting, and blocking users.

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import FriendRequest, Block
from .serializers import FriendRequestSerializer, BlockSerializer

class SendFriendRequestView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Set the from_user field to the authenticated user
        serializer.save(from_user=self.request.user)

class AcceptFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.filter(status='sent')
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.to_user == request.user:
            instance.status = 'accepted'
            instance.save()
            return Response(FriendRequestSerializer(instance).data)
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

class RejectFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.filter(status='sent')
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.to_user == request.user:
            instance.status = 'rejected'
            instance.save()
            return Response(FriendRequestSerializer(instance).data)
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

class BlockUserView(generics.CreateAPIView):
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(blocker=self.request.user)




# to Add Views for Friends List and Pending Friend Requests

from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import FriendRequest
from .serializers import FriendRequestSerializer, UserSerializer, UserActivitySerializer

class FriendsListView(generics.ListAPIView):
    """
    List all friends of the authenticated user.
    A friend is someone who has accepted a friend request sent by the user or to whom the user has sent and accepted.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get users who accepted friend requests sent by the current user
        friends_sent = FriendRequest.objects.filter(
            from_user=user, status='accepted'
        ).values_list('to_user', flat=True)

        # Get users who sent friend requests accepted by the current user
        friends_received = FriendRequest.objects.filter(
            to_user=user, status='accepted'
        ).values_list('from_user', flat=True)

        # Combine both friend lists
        return User.objects.filter(id__in=list(friends_sent) + list(friends_received))

class PendingFriendRequestsView(generics.ListAPIView):
    """
    List all pending friend requests received by the authenticated user.
    """
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get all friend requests received by the user with 'sent' status
        return FriendRequest.objects.filter(to_user=user, status='sent')



# Modify the SendFriendRequestView, AcceptFriendRequestView, and RejectFriendRequestView to log activities when actions are performed.
from .models import FriendRequest, Block, UserActivity  # Import UserActivity model

class SendFriendRequestView(generics.CreateAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        friend_request = serializer.save(from_user=self.request.user)
        # Log activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='friend_request_sent',
            description=f"Sent a friend request to {friend_request.to_user.username}"
        )

class AcceptFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.filter(status='sent')
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.to_user == request.user:
            instance.status = 'accepted'
            instance.save()
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='friend_request_accepted',
                description=f"Accepted a friend request from {instance.from_user.username}"
            )
            return Response(FriendRequestSerializer(instance).data)
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

class RejectFriendRequestView(generics.UpdateAPIView):
    queryset = FriendRequest.objects.filter(status='sent')
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.to_user == request.user:
            instance.status = 'rejected'
            instance.save()
            # Log activity
            UserActivity.objects.create(
                user=request.user,
                activity_type='friend_request_rejected',
                description=f"Rejected a friend request from {instance.from_user.username}"
            )
            return Response(FriendRequestSerializer(instance).data)
        return Response({'detail': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
    

# to Create a View to Retrieve User Activities
class UserActivityListView(generics.ListAPIView):
    """
    List all activities of the authenticated user.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserActivity.objects.filter(user=user).order_by('-timestamp')  # Most recent first


# Cache Frequently Accessed Data:For example, cache the friends list to reduce database load for repeated requests:
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class FriendsListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        friends_sent = FriendRequest.objects.filter(
            from_user=user, status='accepted'
        ).values_list('to_user', flat=True)
        friends_received = FriendRequest.objects.filter(
            to_user=user, status='accepted'
        ).values_list('from_user', flat=True)
        return User.objects.filter(id__in=list(friends_sent) + list(friends_received))


# Use Query Optimization Techniques:
#Use select_related and prefetch_related to reduce the number of database queries.
#For example, when fetching friend requests:

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Use select_related to optimize foreign key lookups
        return FriendRequest.objects.filter(to_user=user, status='sent').select_related('from_user')




# Apply Rate Limiting to Login and Friend Request Endpoints:To Update the views with rate limiting decorators to prevent brute force and spam attacks.
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))  # Limit to 5 requests per minute
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
