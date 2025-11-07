from flask import Flask, render_template, request
import requests

app = Flask(__name__)

GENIUS_TOKEN = "TSXOya8akTDuIGu3KYKC7jThKjh2EpQkfbr8OB712B9IJSxtMM3CD7s6hBvrohp7"  # Pon aquí tu token

@app.route("/", methods=["GET"])
def home():
    song = request.args.get("song", "").strip()
    artist = request.args.get("artist", "").strip()
    album = request.args.get("album", "").strip()
    results = None
    error = None

    if song and artist:
        genius_data = {"found": False, "error": None, "title": None, "url": None, "image": None}
        try:
            headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
            q = f"{song} {artist}"
            r = requests.get("https://api.genius.com/search", params={"q": q}, headers=headers, timeout=10)
            r.raise_for_status()
            hits = r.json().get("response", {}).get("hits", [])
            if hits:
                first = hits[0]["result"]
                genius_data.update({
                    "found": True,
                    "title": first["full_title"],
                    "url": first["url"],
                    "image": first.get("song_art_image_url")
                })
        except Exception as e:
            genius_data["error"] = str(e)

        lrclib_data = {"found": False, "lyrics": None, "syncedLyrics": None, "error": None}
        try:
            params = {"track_name": song, "artist_name": artist}
            if album:
                params["album_name"] = album
            r = requests.get("https://lrclib.net/api/get", params=params, timeout=10)
            r.raise_for_status()
            lrclib_data_json = r.json()
            if lrclib_data_json.get("plainLyrics"):
                lrclib_data.update({
                    "found": True,
                    "lyrics": lrclib_data_json.get("plainLyrics"),
                    "syncedLyrics": lrclib_data_json.get("syncedLyrics")
                })
            else:
                lrclib_data["error"] = "No lyrics found"
        except Exception as e:
            lrclib_data["error"] = str(e)

        results = {"genius": genius_data, "lrclib": lrclib_data}

    return render_template("index.html", song=song, artist=artist, album=album, results=results, error=error)

if __name__ == "__main__":
    app.run()
