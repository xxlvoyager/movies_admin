from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movie_admin.api.urls')),
    path('', include('api.urls')),
]
