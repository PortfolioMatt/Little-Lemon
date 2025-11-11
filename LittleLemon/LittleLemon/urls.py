"""
URL configuration for LittleLemon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView #It needs API endpoints so it can accept user and pass

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('LittleLemonAPI.urls')),
    path('auth/', include('djoser.urls')),  # Djoser endpoints for user management
    path('auth/', include('djoser.urls.authtoken')),  # Djoser endpoints for token authentication
    #access to djoser with /auth/users/  or /auth/token/login/, etc
    #Handy Djoser endpoints:
    # - /auth/users/ (list users and can create new user)
    # - /auth/users/me/ (get current user)
    # - /auth/token/login/ (token login, creates a new token)
    # - /auth/token/logout/ (token logout)
    path('api/token/', TokenObtainPairView.as_view()), #Generates the Auth Token and a Refresh Token
    path('api/token/refresh/', TokenRefreshView.as_view()), #JWT Refreshes the Token
    path('api/token/blacklist/', TokenBlacklistView.as_view()), #Blacklists the Refresh Token, invalidates its use
]
