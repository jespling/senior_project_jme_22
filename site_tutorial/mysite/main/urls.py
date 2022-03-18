from django.urls import path
from . import views


app_name = 'main'  # here for namespacing of urls.

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("songs/", views.get_tracks, name="get_tracks"),
    path("songs/<str:track_id>", views.get_song_details, name="get_song_details"),
    path("chart/<str:chart_name>", views.get_chart, name="get_chart"),
    path("chart_track/<str:track_id>", views.get_chart_song_details, name="get_chart_song_details"),
    path("addToPlaylist/<str:track_id>", views.add_to_playlist, name="add_to_playlist"),
    path("register/", views.register, name="register"),
    path("update/", views.update_profile, name="update_profile"),
    path("logout/", views.logout_request, name="logout"),
    path("login/", views.login_request, name="login"),
]
