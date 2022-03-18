import spotipy
from spotipy.oauth2 import SpotifyOAuth

scope = 'user-library-read playlist-read-private playlist-modify-public playlist-modify-private'
myClientId = "2344bd804b504053be8587dc0a2a6a83"
mySecret = "98ea96fd09224098bacebb6e9756c4de"
myRedirect="http://localhost:8888/callback/"
myUsername="q3d6g52utggljlvcosztu20ai"

token = spotipy.prompt_for_user_token(myUsername,scope, myClientId, mySecret, myRedirect)

sp = spotipy.Spotify(auth=token)
results = sp.user_playlist_create(myUsername, "Spotify Insights", True, False, "test playlist creation through api")

#get playlist id
playlist = sp.user_playlists(myUsername, limit=50, offset=0)
for idx, item in enumerate(playlist['items']):
    if item['name'] == "Spotify Insights":
        print(item['id'])
#print(results['items'])
#print("break")
#for idx, item in enumerate(results['items']):
#    track = item['track']
#    print(track)
#    print("above is track info ")
#    print(idx, track['artists'][0]['name'], ' - ', track['name'])
