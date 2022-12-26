from django.urls import path

from movie_admin.api.v1 import views

urlpatterns = [

    path('movies/', views.Movies.as_view()),
    path('movies/<uuid>/', views.MovieDetail.as_view()),
]
