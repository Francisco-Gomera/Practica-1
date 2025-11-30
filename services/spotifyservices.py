import requests
from base64 import b64encode
import httpx

CLIENT_ID = "2c99aaddc61c4d0788c7ab682eb67602"
CLIENT_SECRET = "6bc31478eaa5448f9e4bcc9b5562df9e"


def get_spotify_token_sync():
    import requests # Usamos requests aquí solo para el token inicial por simplicidad
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

async def search_spotify_song(client: httpx.AsyncClient, token: str, song_name: str, artist_name: str):
    """
    Busca una canción específica usando nombre + artista.
    """
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    
    # TRUCO PRO: Usamos la sintaxis avanzada de Spotify 'track:X artist:Y'
    # Esto asegura que si buscas "Amigo" de "Roberto Carlos", no te salga "Amigo" de "Romeo Santos".
    query = f"track:{song_name} artist:{artist_name}"
    
    try:
        response = await client.get(url, headers=headers, params={"q": query, "type": "track", "limit": 1}, timeout=10.0)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("tracks", {}).get("items", [])
            
            if items:
                item = items[0] # Tomamos el primer (y mejor) resultado
                return {
                    "busqueda_original": f"{song_name} - {artist_name}",
                    "encontrado": True,
                    "titulo": item["name"],
                    "artista": ", ".join([a["name"] for a in item["artists"]]),
                    "album": item["album"]["name"],
                    "imagen": item["album"]["images"][0]["url"] if item["album"]["images"] else None,
                    "preview_url": item.get("preview_url"),
                    "spotify_url": item["external_urls"]["spotify"],
                    "track_id": item.get("id")
                }
    except Exception as e:
        print(f"Error buscando {song_name}: {e}")
    
    # Si falla o no encuentra nada, retornamos un objeto indicando el fallo
    return {
        "busqueda_original": f"{song_name} - {artist_name}",
        "encontrado": False,
        "error": "No encontrada en Spotify"
    }

