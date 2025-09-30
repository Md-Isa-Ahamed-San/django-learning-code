from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"), #takes user credential and returns access and refresh token
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"), #takes refresh token and returns new access token ONLY
] 
