import spotipy
from spotipy.oauth2 import SpotifyOAuth

#set SPOTIPY_CLIENT_ID='2344bd804b504053be8587dc0a2a6a83'
#set SPOTIPY_CLIENT_SECRET='cca219eb8957456fb15e23496ca1cb28'

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_saved_tracks()
for idx, item in enumerate(results['items']):
    track = item['track']
    print(idx, track['artists'][0]['name'], " - ", track['name'])
