# core/urls.py for signup and login.

from django.urls import path
from .views import (UserSignupView, UserLoginView, UserSearchView, SendFriendRequestView, 
                    AcceptFriendRequestView, RejectFriendRequestView, BlockUserView, 
                    FriendsListView, PendingFriendRequestsView, UserActivityListView)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),  # Search endpoint

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # For obtaining access and refresh tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # For refreshing access tokens

    path('send-friend-request/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('accept-friend-request/<int:pk>/', AcceptFriendRequestView.as_view(), name='accept-friend-request'),
    path('reject-friend-request/<int:pk>/', RejectFriendRequestView.as_view(), name='reject-friend-request'),
    path('block-user/', BlockUserView.as_view(), name='block-user'),

    path('friends/', FriendsListView.as_view(), name='friends-list'),  # Add friends list endpoint
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-friend-requests'),  # Add pending friend requests endpoint

    path('activities/', UserActivityListView.as_view(), name='user-activities'),  # Add user activities endpoint
]

