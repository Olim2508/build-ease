"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from .yasg import urlpatterns as swagger_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", login_required(RedirectView.as_view(pattern_name="admin:index"))),
    path("api-auth/", include("rest_framework.urls")),
    path('api/v1/', include([
        path('auth/', include(('auth_app.urls', 'auth_app'), namespace='auth')),
        path('chats/', include(('chats.urls', 'chats'), namespace='chats')),
        path('main/', include(('main.urls', 'main'), namespace='main')),
    ]))
]

urlpatterns += swagger_url


if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
