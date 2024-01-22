from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.shortcuts import redirect
import base64
import requests
import random
import string

CLIENT_ID = 'b3f9cc08e5344aeea4a871c7cc2a596c'
CLIENT_SECRET = 'fb387fc33b9b47e3a05d5bf9f854073c'
REDIRECT_URI = 'http://localhost:3000'
SPOTIFY_API_URL = 'https://api.spotify.com/v1/me'
SPOTIFY_TOP_ARTISTS_URL = 'https://api.spotify.com/v1/me/top/artists'
SPOTIFY_TOP_TRACKS_URL = 'https://api.spotify.com/v1/me/top/tracks'
SPOTIFY_PLAYBACK_URL = 'https://api.spotify.com/v1/me/player/play'

def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

@csrf_exempt
def login(request):
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email user-top-read user-modify-playback-state'
    
    authorize_url = f'https://accounts.spotify.com/authorize/?' \
                    f'response_type=code&client_id={CLIENT_ID}&' \
                    f'scope={scope}&redirect_uri={REDIRECT_URI}&state={state}'
    
    return HttpResponseRedirect(authorize_url)

@csrf_exempt
def callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if state is None:
        return JsonResponse({'error': 'state_mismatch'})
    else:
        auth_options = {
            'url': 'https://accounts.spotify.com/api/token',
            'data': {
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'grant_type': 'authorization_code'
            },
            'headers': {
                'Authorization': 'Basic ' + base64.b64encode(
                    f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode(),
            }
        }
        
        response = requests.post(auth_options['url'], data=auth_options['data'],
                                 headers=auth_options['headers'])
        token_data = response.json()
        access_token = token_data.get('access_token')
        
        # Store the access_token in localStorage (frontend)
        
        return JsonResponse({'access_token': access_token})

@csrf_exempt
def getUser(request, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        response = requests.get(SPOTIFY_API_URL, headers=headers)
        user_data = response.json()
        return JsonResponse(user_data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def getTopArtist(request, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    params = {
        'limit': 6  # Set the limit to fetch top 6 artists
    }

    try:
        response = requests.get(SPOTIFY_TOP_ARTISTS_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        top_artists_data = response.json()
        return JsonResponse(top_artists_data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def getTopTracks(request, access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    params = {
        'limit': 6
    }

    try:
        response = requests.get(SPOTIFY_TOP_TRACKS_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        top_tracks_data = response.json()
        return JsonResponse(top_tracks_data)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def playTrack(request, access_token, track_uri):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'uris': [track_uri],
        'position_ms': 0,
    }

    try:
        response = requests.put(SPOTIFY_PLAYBACK_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return JsonResponse({'message': 'Track playback started'})
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)