from django.urls import path
from .views import UserViewSet, MeView

user_list = UserViewSet.as_view({
    "get": "list"
})

urlpatterns = [
    path("users/", user_list, name="users-list"),
    path("users/me/", MeView.as_view(), name="users-me"),
]