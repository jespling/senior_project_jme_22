import pandas as pd
import spotipy

#scope = 'user-library-read'
scope = 'user-top-read user-read-recently-played'
myClientId = "2344bd804b504053be8587dc0a2a6a83"
mySecret = "98ea96fd09224098bacebb6e9756c4de"
myRedirect="http://localhost:8888/callback/"
myUsername="q3d6g52utggljlvcosztu20ai"

token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)

sp = spotipy.Spotify(auth=token)
#results = sp.current_user_saved_tracks()
results = sp.current_user_recently_played(limit=50, after=None, before=None)

top_tracks = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
print(top_tracks)



# Function to extract MetaData from a playlist thats longer than 100 songs
def get_recently_played_100_songs():
    #results = sp.user_playlist_tracks(username,playlist_id)
    results = sp.current_user_recently_played(limit=50, after=None, before=None)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    results = tracks    

    playlist_tracks_id = []
    playlist_tracks_titles = []
    playlist_tracks_artists = []
    playlist_tracks_first_artists = []
    playlist_tracks_first_release_date = []
    playlist_tracks_popularity = []

    for i in range(len(results)):
        #print(i) # Counter
        if i == 0:
            playlist_tracks_id = results[i]['track']['id']
            playlist_tracks_titles = results[i]['track']['name']
            playlist_tracks_first_release_date = results[i]['track']['album']['release_date']
            playlist_tracks_popularity = results[i]['track']['popularity']

            artist_list = []
            for artist in results[i]['track']['artists']:
                artist_list= artist['name']
            playlist_tracks_artists = artist_list

            features = sp.audio_features(playlist_tracks_id)
            features_df = pd.DataFrame(data=features, columns=features[0].keys())
            features_df['title'] = playlist_tracks_titles
            features_df['all_artists'] = playlist_tracks_artists
            features_df['popularity'] = playlist_tracks_popularity
            features_df['release_date'] = playlist_tracks_first_release_date
            features_df = features_df[['id', 'title', 'all_artists', 'popularity', 'release_date',
                                       'danceability', 'energy', 'key', 'loudness',
                                       'mode', 'acousticness', 'instrumentalness',
                                       'liveness', 'valence', 'tempo',
                                       'duration_ms', 'time_signature']]
            continue
        else:
            try:
                playlist_tracks_id = results[i]['track']['id']
                playlist_tracks_titles = results[i]['track']['name']
                playlist_tracks_first_release_date = results[i]['track']['album']['release_date']
                playlist_tracks_popularity = results[i]['track']['popularity']
                artist_list = []
                for artist in results[i]['track']['artists']:
                    artist_list= artist['name']
                playlist_tracks_artists = artist_list
                features = sp.audio_features(playlist_tracks_id)
                new_row = {'id':[playlist_tracks_id],
               'title':[playlist_tracks_titles],
               'all_artists':[playlist_tracks_artists],
               'popularity':[playlist_tracks_popularity],
               'release_date':[playlist_tracks_first_release_date],
               'danceability':[features[0]['danceability']],
               'energy':[features[0]['energy']],
               'key':[features[0]['key']],
               'loudness':[features[0]['loudness']],
               'mode':[features[0]['mode']],
               'acousticness':[features[0]['acousticness']],
               'instrumentalness':[features[0]['instrumentalness']],
               'liveness':[features[0]['liveness']],
               'valence':[features[0]['valence']],
               'tempo':[features[0]['tempo']],
               'duration_ms':[features[0]['duration_ms']],
               'time_signature':[features[0]['time_signature']]
               }

                dfs = [features_df, pd.DataFrame(new_row)]
                features_df = pd.concat(dfs, ignore_index = True)
            except:
                continue
                
    return features_df
    
#out = get_playlist_tracks_more_than_100_songs('q3d6g52utggljlvcosztu20ai', 'https://open.spotify.com/playlist/37i9dQZF1E39eFzOq7iP55?si=680e1c2eae4c4159')
out = get_recently_played_100_songs()
print(out)
