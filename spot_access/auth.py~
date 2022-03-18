import spotipy
import spotipy.util as util

cid ="2344bd804b504053be8587dc0a2a6a83" 
secret = "cca219eb8957456fb15e23496ca1cb28"
username = "q3d6g52utggljlvcosztu20ai"

scope = 'user-library-read playlist-read-private'
token = util.prompt_for_user_token(username,scope,client_id=cid,client_secret=secret,redirect_uri='http://localhost:8888/callback/')

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

#cache_token = token.get_access_token()

#sp = spotipy.Spotify(token)
currentfaves = sp.current_user_top_tracks(limit=20, offset=0, time_range='medium_term')

print(currentfaves)
