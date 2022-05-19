from django.shortcuts import render, redirect
from .models import UserStat, SongStat, TrackStat, ChartStat, ChartStatUser, Friend_Request, Profile
from .forms import NewUserForm, ProfileForm, FriendForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout, authenticate, login, get_user_model
from django.contrib import messages
import spotipy
import billboard
from spotipy.oauth2 import SpotifyOAuth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore
from scipy.spatial.distance import pdist, squareform

scaler = StandardScaler()

chart_df = pd.DataFrame()

scope = 'user-library-read'
myClientId = "2344bd804b504053be8587dc0a2a6a83"
mySecret = "98ea96fd09224098bacebb6e9756c4de"
myRedirect = "http://localhost:8888/callback/"

from django.db import transaction


def homepage(request):
    # billboard hot 100 display
    chart = billboard.ChartData('hot-100')
    chart_collection = {}

    # delete old pulls of hot 100
    ChartStat.objects.all().delete()

    for idx, c in enumerate(chart):
        chart_data = ChartStat(
            artist=c.artist,
            title=c.title,
            rank=idx + 1
        )
        chart_data.save()
        chart_collection = ChartStat.objects.all()

    # current_user = request.user
    # if request.user.is_authenticated:
    # print(current_user.username)
    # print(current_user.select_related('profile'))
    # print(request.user.profile.spotify_username)

    #print(Profile.objects.all())
    #print(Friend_Request.objects.all())

    # get friends list
    friends = []
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user.id)
        #print("user_profile: ", user_profile)
        friends = user_profile.friends.all()
        #print("friends: ", friends)

    return render(request=request,
                  template_name='main\home3.html',
                  context={"ChartStats": ChartStat.objects.all,
                           "allusers": Profile.objects.all,
                           "all_friend_requests": Friend_Request.objects.all,
                           "friends": friends})


@login_required
def send_friend_request(request):
    to_user_get = "not logged in"

    if request.method == "POST":
        friend_request_form = FriendForm(request.POST)
        #print("friend_form: ", friend_request_form)
        #print("to_user", request.POST.get("users"))
        #print("from_user", request.POST.get("senderId"))

        if friend_request_form.is_valid():
            to_user_get = friend_request_form.cleaned_data['user']
    else:
        friend_request_form = FriendForm()

    #print("to_user_get: ", to_user_get)

    #all_users = Users.objects.all()
    #User = get_user_model()
    #users = User.objects.all()
    #for user in users:
        #print(user.username)


    #print("type of post request data to user: ", type(request.POST.get("users")))

    #print("UserID: ", userID)
    from_user = request.user
    from_user_profile = Profile.objects.get(user=from_user)
    #print("type of post request data from user: ", type(from_user_profile))
    #print("from_user_profile: ", from_user_profile)
    #print("from user: ", from_user)


    #to_user = Profile.objects.get(id=userID)
    User = get_user_model()
    to_user_user = User.objects.get(username=request.POST.get("users"))
    #print
    #print("to_user_User: ", type(to_user_user))
    to_user_profile = Profile.objects.get(user=to_user_user)
    #rint("to_user_profile: ", to_user_profile)
    #print("to_user_profile type: ", type(to_user_profile))

    #print("to user: ", to_user)
    #print("to user id: ", to_user.id)
    #print("from user id: ", from_user.id)
    friend_request, created = Friend_Request.objects.get_or_create(from_user=from_user_profile, to_user=to_user_profile)
    if created:
        messages.success(request, f"Friend Request Sent!")
        return redirect("main:friends")
        # return HttpResponse('friend request sent')
    else:
        messages.error(request, f"Friend Request Already Sent!")
        return redirect("main:friends")
        # return HttpResponse('friend request was already sent')


@login_required
def accept_friend_request(request, requestID):
    friend_request = Friend_Request.objects.get(id=requestID)
    #print("request.user: ", request.user)
    #print("friend_request.to_user: ", friend_request.to_user.user)
    if friend_request.to_user.user == request.user:
        friend_request.to_user.friends.add(friend_request.from_user)
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.delete()
        messages.success(request, f"Friend Request Accepted!")
        return redirect("main:friends")
    else:
        messages.error(request, f"Friend request not accepted")
        return redirect("main:friends")


def get_chart(request, chart_name):
    scope = 'user-library-read'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect = "http://localhost:8888/callback/"
    myUsername = request.user.profile.spotify_username

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)

    sp = spotipy.Spotify(auth=token)
    chart = billboard.ChartData(chart_name)
    chart_collection = {}

    # delete old pulls of chart data
    ChartStat.objects.all().delete()

    temp_df = pd.DataFrame((), columns=['id', 'title', 'all_artists', 'popularity', 'danceability', 'energy', 'key',
                                        'loudness', 'mode', 'acousticness', 'instrumentalness', 'liveness', 'valence',
                                        'tempo', 'duration_ms', 'time_signature'])

    # print("df: ", df)

    for idx, c in enumerate(chart):
        # print(c.title.split(" ", 1)[0])
        shortened_artist = c.artist.split(" ", 1)[0]
        track = sp.search(q='artist:' + shortened_artist + ' track:' + c.title, type='track')
        # df = pd.read_json(track['tracks']['items'][0])
        # print("artist: ", shortened_artist)
        # print(track['tracks']['items'][0])
        # print(getTopTracks(track['tracks'][0], sp))
        # print("Track Info:", track['tracks'])
        # print("\n")
        if (track['tracks']['total'] == 0):
            track_id = 'none'
        else:
            track_id = track['tracks']['items'][0]['id']
            # get chart details & audio features df
            df = get_chart_features(track_id, track, sp)
            temp_df = temp_df.append(df, ignore_index=True)
        chart_data = ChartStat(
            artist=c.artist,
            title=c.title,
            rank=idx + 1,
            track_id=track_id
        )
        chart_data.save()
        chart_collection = ChartStat.objects.all()

        # print("Chart DF: ", df)
        global chart_df
        chart_df = temp_df

    return render(request=request,
                  template_name='main\chart.html',
                  context={"ChartStats": ChartStat.objects.all,
                           "ChartName": chart.title})


def get_chart_features(track_id, result, sp):
    tracks_id = []
    tracks_titles = []
    tracks_artists = []
    tracks_popularity = []
    print("track id: ", track_id)
    # print(result, "\n")
    data = result['tracks']['items'][0]
    tracks_id = track_id
    tracks_titles = data['name']
    tracks_artists = data['artists'][0]['name']
    tracks_popularity = data['popularity']
    # print(data, "\n")
    features = sp.audio_features(track_id)
    features_df = pd.DataFrame(data=features, columns=features[0].keys())
    features_df['title'] = tracks_titles
    features_df['all_artists'] = tracks_artists
    features_df['popularity'] = tracks_popularity
    features_df = features_df[
        ['id', 'title', 'all_artists', 'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode',
         'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']]
    # print(features_df, "\n")
    return features_df


def get_user_chart(request):
    # chart = billboard.ChartData(chart_name)
    # print("User DF: ", user_df)
    global chart_df

    # delete old pulls of chart data
    ChartStatUser.objects.all().delete()

    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect = "http://localhost:8888/callback/"
    myUsername = request.user.profile.spotify_username
    scope = 'user-top-read user-read-recently-played'

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')

    # access chartStat objects and put into dataframe
    chart_collection = ChartStat.objects.all()
    # df_chart = pd.DataFrame.from_records(ChartStat.objects.all().values())

    top_tracks_df = getTopTracks(results, sp)
    # print(df)

    # grab top artist string
    artist = top_tracks_df.iloc[0]['all_artists']
    print("Artist: ", artist)
    print("user: ", top_tracks_df)
    print("chart: ", chart_df)

    # convert artist to 0 or 1
    top_tracks_df['artist'] = 0
    chart_df['artist'] = 0
    print('t tracks befoer artist assignment', top_tracks_df)
    print('char tracks before artist assignment', chart_df)
    for index, row in top_tracks_df.iterrows():
        if artist == row['all_artists']:
            top_tracks_df.at[index, 'artist'] = 0
        else:
            top_tracks_df.at[index, 'artist'] = 1

    for index, row in chart_df.iterrows():
        if artist == row['all_artists']:
            print('artist match')
            chart_df.at[index, 'artist'] = 0
        else:
            chart_df.at[index, 'artist'] = 1

    # Drop non-numerical columns
    data_user = top_tracks_df.drop(['id', 'all_artists', 'title'], axis=1)
    data_chart = chart_df.drop(['id', 'all_artists', 'title'], axis=1)
    print("data_user: ", data_user)
    print("data_chart: ", data_chart)

    # scale data before z-score
    data_user_scaled = scaler.fit_transform(data_user)
    df_user_scaled = pd.DataFrame(data_user_scaled,
                                  columns=['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode',
                                           'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                                           'duration_ms', 'time_signature', 'artist'])
    data_chart_scaled = scaler.fit_transform(data_chart)
    df_chart_scaled = pd.DataFrame(data_chart_scaled,
                                   columns=['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode',
                                            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
                                            'duration_ms', 'time_signature', 'artist'])
    # print(df_scaled)
    # print(df_scaled.describe())

    # Calculate z-score for dataframe
    df_user_zscore = df_user_scaled.apply(zscore)
    df_chart_zscore = df_chart_scaled.apply(zscore)
    # print(df_zscore)
    # print(df_zscore.values)

    # fill out dataframe with single song for comparison calculation
    df_try = df_user_zscore.loc[0]
    new_df = pd.DataFrame([df_try] * len(df_chart_zscore.index),
                          columns=['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'acousticness',
                                   'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature',
                                   'artist'])
    print("new_df: ", new_df)

    # euclidean distance between 1 song (comparator) and the list of songs
    dists = Euclidean_Dist(new_df, df_chart_zscore)
    print("dists", dists)

    # append distances to original df for rendering
    chart_df['dist'] = dists.tolist()

    # sort rows/songs by distance ascending
    result_df = chart_df.sort_values(by='dist')
    print(result_df)

    df = result_df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        shortened_artist = row['all_artists']  # c.artist.split(" ", 1)[0]
        track = sp.search(q='artist:' + shortened_artist + ' track:' + row['title'], type='track')
        track_id = row['id']  # track['tracks']['items'][0]['id']
        user_chart_data = ChartStatUser(
            artist=row['all_artists'],
            title=row['title'],
            rank=index + 1,
            track_id=row['id']
        )
        user_chart_data.save()
        user_chart_collection = ChartStatUser.objects.all()

    return render(request=request,
                  template_name='main\\user_chart.html',
                  context={"ChartStats": ChartStatUser.objects.all()})


def Euclidean_Dist(df1, df2, cols=['popularity', 'danceability', 'energy', 'key', 'loudness', 'mode', 'acousticness',
                                   'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature',
                                   'artist']):
    print("df1: ", df1)
    print("df2: ", df2)
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)


def getTopTracks(results, sp):
    # results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    results = tracks
    tracks_id = []
    tracks_titles = []
    tracks_artists = []
    tracks_popularity = []
    for i in range(len(results)):
        if i == 0:
            tracks_id = results[i]['id']
            tracks_titles = results[i]['name']
            tracks_popularity = results[i]['popularity']
            artist_list = []
            for artist in results[i]['artists']:
                artist_list = artist['name']
            tracks_artists = artist_list
            features = sp.audio_features(tracks_id)
            features_df = pd.DataFrame(data=features, columns=features[0].keys())
            features_df['title'] = tracks_titles
            features_df['all_artists'] = tracks_artists
            features_df['popularity'] = tracks_popularity
            features_df = features_df[
                ['id', 'title', 'all_artists', 'popularity', 'danceability', 'energy', 'key', 'loudness', 'mode',
                 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature']]
            continue
        else:
            try:
                tracks_id = results[i]['id']
                tracks_titles = results[i]['name']
                tracks_popularity = results[i]['popularity']
                artist_list = []
                for artist in results[i]['artists']:
                    artist_list = artist['name']
                tracks_artists = artist_list
                features = sp.audio_features(tracks_id)
                new_row = {'id': [tracks_id],
                           'title': [tracks_titles],
                           'all_artists': [tracks_artists],
                           'popularity': [tracks_popularity],
                           'danceability': [features[0]['danceability']],
                           'energy': [features[0]['energy']],
                           'key': [features[0]['key']],
                           'loudness': [features[0]['loudness']],
                           'mode': [features[0]['mode']],
                           'acousticness': [features[0]['acousticness']],
                           'instrumentalness': [features[0]['instrumentalness']],
                           'liveness': [features[0]['liveness']],
                           'valence': [features[0]['valence']],
                           'tempo': [features[0]['tempo']],
                           'duration_ms': [features[0]['duration_ms']],
                           'time_signature': [features[0]['time_signature']]}

                dfs = [features_df, pd.DataFrame(new_row)]
                features_df = pd.concat(dfs, ignore_index=True)
            except:
                continue
    # print("returning")
    return features_df


def get_tracks(request):
    scope = 'user-library-read user-top-read user-read-recently-played'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect = "http://localhost:8888/callback/"
    # myUsername="q3d6g52utggljlvcosztu20ai"
    myUsername = request.user.profile.spotify_username
    print(myUsername)

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)

    sp = spotipy.Spotify(auth=token)
    # results = sp.current_user_saved_tracks()
    # results = sp.current_user_top_tracks()
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')

    # delete old records if called previously
    SongStat.objects.all().delete()

    all_songs = {}
    for idx, item in enumerate(results['items']):
        # track = item['track']
        song_data = SongStat(
            artist=item['artists'][0]['name'],
            title=item['name'],
            artist_id=item['artists'][0]['id'],
            track_id=item['id'],
            img_url=item['album']['images'][1]['url'],
        )
        song_data.save()
        all_songs = SongStat.objects.all()

    return render(request,
                  template_name='main\songs2.html',
                  context={"SongStats": SongStat.objects.all})


def get_chart_song_details(request, track_id):
    scope = 'user-library-read'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect = "http://localhost:8888/callback/"
    # myUsername="q3d6g52utggljlvcosztu20ai"
    myUsername = request.user.profile.spotify_username
    print(myUsername)

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    track = sp.track(track_id)

    # delete old track records if previously called
    TrackStat.objects.all().delete()

    track_info = {}

    track_data = TrackStat(
        artist=track['artists'][0]['name'],
        title=track['name'],
        img_url=track['album']['images'][0]['url'],
        release_date=track['album']['release_date'],
        duration=(track['duration_ms'] / 60000),
        snippet=track['preview_url']
    )
    track_data.save()
    track_info = TrackStat.objects.all()

    return render(request,
                  template_name='main\song_info.html',
                  context={"TrackStats": TrackStat.objects.all,
                           "ChartId": track_id})


def rate_song(request, track_title):
    # get track from TrackStat and update with user input value
    track = TrackStat.objects.get(title=track_title)#.update(rating=request.POST.get("rating"))
    track.rating = request.POST.get("rating")
    track.save()
    print("track: ", track.rating)

    return render(request,
           template_name='main\song_info.html',
           context={"TrackStats": TrackStat.objects.all})


def add_to_playlist(request, track_id):
    scope = 'user-library-read user-top-read user-read-recently-played playlist-modify-public'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect = "http://localhost:8888/callback/"
    myUsername = request.user.profile.spotify_username
    print(myUsername, request.user.profile.playlist_id)

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    tracks = [track_id]
    # print(tracks)
    sp.user_playlist_add_tracks(myUsername, request.user.profile.playlist_id, tracks, position=None)

    return redirect(request.META['HTTP_REFERER'])


def get_song_details(request, track_id):
    scope = 'user-library-read user-top-read user-read-recently-played'
    myClientId = "2344bd804b504053be8587dc0a2a6a83"
    mySecret = "98ea96fd09224098bacebb6e9756c4de"
    myRedirect = "http://localhost:8888/callback/"
    # myUsername="q3d6g52utggljlvcosztu20ai"
    myUsername = request.user.profile.spotify_username
    print(myUsername)

    token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')  # sp.current_user_saved_tracks()

    # delete old track records if previously called
    TrackStat.objects.all().delete()

    track_info = {}

    for idx, item in enumerate(results['items']):
        # track = item['track']

        if (item['id'] == track_id):
            track_data = TrackStat(
                artist=item['artists'][0]['name'],
                title=item['name'],
                img_url=item['album']['images'][0]['url'],
                release_date=item['album']['release_date'],
                duration=(item['duration_ms'] / 60000),
                snippet=item['preview_url']
            )
            track_data.save()
            track_info = TrackStat.objects.all()

    return render(request,
                  template_name='main\song_info.html',
                  context={"TrackStats": TrackStat.objects.all})


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

            return render(request=request,
                          template_name="main/register.html",
                          context={"form": form})

    form = NewUserForm
    return render(request=request,
                  template_name="main/register.html",
                  context={"form": form})


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        # user_form = NewUserForm(request.GET, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        # print(user_form.errors)
        print(profile_form.errors)
        if profile_form.is_valid():
            # user_form.save()
            profile_form.save()
            messages.success(request, f'Your profile was successfully updated!')
            # create a spotify insights playlist for the user
            scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private'
            myClientId = "2344bd804b504053be8587dc0a2a6a83"
            mySecret = "98ea96fd09224098bacebb6e9756c4de"
            myRedirect = "http://localhost:8888/callback/"
            myUsername = request.user.profile.spotify_username
            token = spotipy.prompt_for_user_token(myUsername, scope, myClientId, mySecret, myRedirect)
            sp = spotipy.Spotify(auth=token)
            results = sp.user_playlist_create(myUsername, "Spotify Insights", True, False,
                                              "My saved tracks from Spotify Insights")
            # get playlist id and save it to profile
            playlist = sp.user_playlists(myUsername, limit=50, offset=0)
            p_id = None
            for idx, item in enumerate(playlist['items']):
                if item['name'] == "Spotify Insights":
                    p_id = (item['id'])
            # assign playlist id to profile model
            obj = request.user.profile
            obj.playlist_id = p_id
            obj.save()
            # print(obj.playlist_id)

            return redirect('main:homepage')
        else:
            messages.error(request, f'Please correct the error below.')
    else:
        # user_form = NewUserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'main/profile.html', {'profile_form': profile_form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
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
    return render(request=request,
                  template_name="main/login.html",
                  context={"form": form})


def friends(request):
    # get friends list
    friend_list = []
    if request.user.is_authenticated:
        user_profile = Profile.objects.get(user=request.user.id)
        #print("user_profile: ", user_profile)
        friend_list = user_profile.friends.all()
        #print("friends: ", friends)

    return render(request=request,
                  template_name="main/friends.html",
                  context={"allusers": Profile.objects.all,
                           "all_friend_requests": Friend_Request.objects.all,
                           "friends": friend_list})
