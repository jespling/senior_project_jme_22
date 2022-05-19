import pandas as pd
import numpy as np
import spotipy
from sklearn.preprocessing import StandardScaler
from scipy.stats import zscore
from scipy.spatial.distance import pdist, squareform

scaler = StandardScaler()

#scope = 'user-library-read'
scope = 'user-top-read user-read-recently-played'
myClientId = "2344bd804b504053be8587dc0a2a6a83"
mySecret = "98ea96fd09224098bacebb6e9756c4de"
myRedirect="http://localhost:8888/callback/"
myUsername="q3d6g52utggljlvcosztu20ai"

token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)
sp = spotipy.Spotify(auth=token)
#results = sp.current_user_saved_tracks()
#results = sp.current_user_recently_played(limit=50, after=None, before=None)

results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
#print(top_tracks)


# Function to extract MetaData from a playlist thats longer than 100 songs
def get_top_tracks():
    results = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')
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
                artist_list= artist['name']
            tracks_artists = artist_list

            features = sp.audio_features(tracks_id)
            features_df = pd.DataFrame(data=features, columns=features[0].keys())
            features_df['title'] = tracks_titles
            features_df['all_artists'] = tracks_artists
            features_df['popularity'] = tracks_popularity
            features_df = features_df[['id', 'title', 'all_artists', 'popularity',
                                       'danceability', 'energy', 'key', 'loudness',
                                       'mode', 'acousticness', 'instrumentalness',
                                       'liveness', 'valence', 'tempo',
                                       'duration_ms', 'time_signature']]
            continue
        else:
            try:
                tracks_id = results[i]['id']
                tracks_titles = results[i]['name']
                tracks_popularity = results[i]['popularity']
                artist_list = []
                for artist in results[i]['artists']:
                    artist_list= artist['name']
                tracks_artists = artist_list
                features = sp.audio_features(tracks_id)
                new_row = {'id':[tracks_id],
               'title':[tracks_titles],
               'all_artists':[tracks_artists],
               'popularity':[tracks_popularity],
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

                features_df.to_csv('categories')
            except:
                continue
                
    return features_df
    
#out = get_playlist_tracks_more_than_100_songs('q3d6g52utggljlvcosztu20ai', 'https://open.spotify.com/playlist/37i9dQZF1E39eFzOq7iP55?si=680e1c2eae4c4159')
df = get_top_tracks()

#describe original DF

print(df)
print(df.describe())

#Drop non-numerical columns
data = df.drop(['id', 'title', 'all_artists',], axis=1)
print(data)

#scale data before z-score
data_scaled = scaler.fit_transform(data)
df_scaled = pd.DataFrame(data_scaled, columns = ['popularity','danceability', 'energy', 'key', 'loudness','mode', 'acousticness', 'instrumentalness','liveness', 'valence', 'tempo','duration_ms', 'time_signature'])
print(df_scaled)
print(df_scaled.describe())

#Calculate z-score for dataframe
df_zscore = df_scaled.apply(zscore)
print(df_zscore)
#print(df_zscore.values)

#fill out dataframe with single song for comparison calculation
df_try = df_zscore.loc[0]
new_df = pd.DataFrame([df_try]*60, columns = ['popularity','danceability', 'energy', 'key', 'loudness','mode', 'acousticness', 'instrumentalness','liveness', 'valence', 'tempo','duration_ms', 'time_signature'])
print(new_df)

#euclidean distance between 1 song (comparator) and the list of songs
def Euclidean_Dist(df1, df2, cols= ['popularity','danceability', 'energy', 'key', 'loudness','mode', 'acousticness', 'instrumentalness','liveness', 'valence', 'tempo','duration_ms', 'time_signature']):
    return np.linalg.norm(df1[cols].values - df2[cols].values, axis=1)

dists = Euclidean_Dist(new_df, df_zscore)
print(dists) 

#append distances to original df for rendering
df['dist'] = dists.tolist()

#sort rows/songs by distance ascending
result_df = df.sort_values(by = 'dist')

print(result_df)

