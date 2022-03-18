from django.shortcuts import render, redirect
from .models import UserStat, SongStat, TrackStat, ChartStat
from .forms import NewUserForm, ProfileForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, authenticate, login
from django.contrib import messages
import spotipy
import billboard
from spotipy.oauth2 import SpotifyOAuth
from django.contrib.auth.decorators import login_required
from django.db import transaction

def homepage(request):
    #billboard hot 100 display
    chart = billboard.ChartData('hot-100')
    chart_collection = {}

    #delete old pulls of hot 100
    ChartStat.objects.all().delete()

    for idx, c in enumerate(chart):
        chart_data = ChartStat(
                artist = c.artist,
                title = c.title,
                rank = idx+1
        )
        chart_data.save()
        chart_collection = ChartStat.objects.all()

    #current_user = request.user
    #if request.user.is_authenticated:
        #print(current_user.username)
        #print(current_user.select_related('profile'))
        #print(request.user.profile.spotify_username)

    return render(request = request,
                    template_name='main\home3.html',
                    context = {"ChartStats":ChartStat.objects.all})

def get_chart(request, chart_name):
    
    scope = 'user-library-read'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect="http://localhost:8888/callback/"
    myUsername = request.user.profile.spotify_username

    token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)

    sp = spotipy.Spotify(auth=token)
    chart = billboard.ChartData(chart_name)
    chart_collection = {}

    #delete old pulls of chart data
    ChartStat.objects.all().delete()


    for idx, c in enumerate(chart):
        #print(c.title.split(" ", 1)[0])
        shortened_artist = c.artist.split(" ", 1)[0]
        track = sp.search(q='artist:' + shortened_artist + ' track:' + c.title, type='track')
        if(track['tracks']['total'] == 0):
                track_id = 'none'
        else:
                track_id = track['tracks']['items'][0]['id']
        chart_data = ChartStat(
                artist = c.artist,
                title = c.title,
                rank = idx+1,
                track_id = track_id
        )
        chart_data.save()
        chart_collection = ChartStat.objects.all()

    return render(request = request,
                    template_name='main\chart.html',
                    context = {"ChartStats":ChartStat.objects.all,
                                "ChartName":chart.title})

def get_tracks(request):
    scope = 'user-library-read user-top-read user-read-recently-played'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect="http://localhost:8888/callback/"
    #myUsername="q3d6g52utggljlvcosztu20ai"
    myUsername = request.user.profile.spotify_username
    print(myUsername)

    token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)

    sp = spotipy.Spotify(auth=token)
    #results = sp.current_user_saved_tracks()
    #results = sp.current_user_top_tracks()
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')

    #delete old records if called previously
    SongStat.objects.all().delete()

    all_songs = {}
    for idx, item in enumerate(results['items']):
        #track = item['track']
        song_data = SongStat(
                artist = item['artists'][0]['name'],
                title = item['name'],
                artist_id = item['artists'][0]['id'],
                track_id = item['id'], 
                img_url = item['album']['images'][1]['url'],
        )
        song_data.save()
        all_songs = SongStat.objects.all()

    return render (request,
                    template_name='main\songs2.html',
                    context = {"SongStats":SongStat.objects.all})
        
def get_chart_song_details(request, track_id):
    scope = 'user-library-read'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect="http://localhost:8888/callback/"
    #myUsername="q3d6g52utggljlvcosztu20ai"
    myUsername = request.user.profile.spotify_username
    print(myUsername)

    token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    track = sp.track(track_id)

    #delete old track records if previously called
    TrackStat.objects.all().delete()

    track_info = {}
   
    track_data = TrackStat(
        artist = track['artists'][0]['name'],
        title = track['name'],
        img_url = track['album']['images'][0]['url'],
        release_date = track['album']['release_date'],
        duration = (track['duration_ms']/60000),
        snippet = track['preview_url']
    )
    track_data.save()
    track_info = TrackStat.objects.all()
    
    return render(request,
                template_name='main\song_info.html',
                context = {"TrackStats":TrackStat.objects.all})

def add_to_playlist(request, track_id):
    scope = 'user-library-read user-top-read user-read-recently-played playlist-modify-public'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect="http://localhost:8888/callback/"
    myUsername = request.user.profile.spotify_username
    print(myUsername, request.user.profile.playlist_id)

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    tracks = [track_id]
    #print(tracks)
    sp.user_playlist_add_tracks(myUsername, request.user.profile.playlist_id, tracks, position=None)

    return redirect(request.META['HTTP_REFERER'])

def get_song_details(request, track_id):
    scope = 'user-library-read user-top-read user-read-recently-played'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect="http://localhost:8888/callback/"
    #myUsername="q3d6g52utggljlvcosztu20ai"
    myUsername = request.user.profile.spotify_username
    print(myUsername)

    token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')#sp.current_user_saved_tracks()

    #delete old track records if previously called
    TrackStat.objects.all().delete()

    track_info = {}
   
    for idx, item in enumerate(results['items']):
        #track = item['track']

        if(item['id'] == track_id):
            track_data = TrackStat(
                    artist = item['artists'][0]['name'],
                    title = item['name'],
                    img_url = item['album']['images'][0]['url'],
                    release_date = item['album']['release_date'],
                    duration = (item['duration_ms']/60000),
                    snippet = item['preview_url']
            )
            track_data.save()
            track_info = TrackStat.objects.all()


    
    return render(request,
                template_name='main\song_info.html',
                context = {"TrackStats":TrackStat.objects.all})



def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created: {username}")
            login(request, user)

            return redirect("main:homepage")
        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

            return render(request = request,
                            template_name = "main/register.html",
                            context={"form":form})


    form = NewUserForm
    return render(request = request,
                    template_name = "main/register.html",
                    context={"form":form})

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        #user_form = NewUserForm(request.GET, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        #print(user_form.errors)
        print(profile_form.errors)
        if profile_form.is_valid():
            #user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile was successfully updated!')
            #create a spotify insights playlist for the user
            scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private'
            myClientId = "2344bd804b504053be8587dc0a2a6a83"
            mySecret = "98ea96fd09224098bacebb6e9756c4de"
            myRedirect="http://localhost:8888/callback/"
            myUsername= request.user.profile.spotify_username
            token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)
            sp = spotipy.Spotify(auth=token)
            results = sp.user_playlist_create(myUsername, "Spotify Insights", True, False, "My saved tracks from Spotify Insights")
            #get playlist id and save it to profile 
            playlist = sp.user_playlists(myUsername, limit=50, offset=0)
            p_id = None
            for idx, item in enumerate(playlist['items']):
                    if item['name'] == "Spotify Insights":
                                p_id = (item['id'])
            #assign playlist id to profile model
            obj = request.user.profile
            obj.playlist_id = p_id
            obj.save()
            #print(obj.playlist_id)
            
            return redirect('main:homepage')
        else:
            messages.error(request, f'Please correct the error below.')
    else:
        #user_form = NewUserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'main/profile.html', {'profile_form': profile_form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request = request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome to Spotify Insights, {username}!")
                return redirect('/')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")

    form = AuthenticationForm()
    return render(request = request,
                    template_name = "main/login.html",
                    context={"form":form})
