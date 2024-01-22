from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login, name='login'),
    path('callback/', callback, name='callback'),
    path('user/<str:access_token>/', getUser, name='user'),
    path('top-artists/<str:access_token>/', getTopArtist, name='top-artists'),
    path('top-tracks/<str:access_token>/', getTopTracks, name='top-tracks'),
    path('play-current-track/<str:access_token>/<str:track_uri>/', playTrack, name='play-current-track'),
]