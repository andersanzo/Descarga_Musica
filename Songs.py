#!/usr/bin/env python3
import os
import requests
import concurrent.futures
from yt_dlp import YoutubeDL
import re

# Coloca aquí tu API Key de YouTube Data API
API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # Reemplaza con tu clave real

def sanitize_filename(filename):
    """Elimina caracteres no válidos en nombres de archivos."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def search_youtube_videos(api_key, query, max_results=20):
    """
    Utiliza la API de YouTube para buscar vídeos relacionados con la consulta.
    Devuelve una lista de diccionarios con video_id, título y URL.
    """
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": api_key
    }
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    data = response.json()
    videos = []
    for item in data.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        if not video_id:
            print(f"Se omite un item sin videoId: {item}")
            continue
        title = item["snippet"]["title"]
        videos.append({
            "video_id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })
    return videos

def get_channel_videos(api_key, channel_url):
    """
    A partir de un enlace de canal de YouTube, obtiene todos los vídeos del canal.
    Se admite enlace con /channel/ o /user/.
    """
    channel_id = None
    username = None

    if "/channel/" in channel_url:
        try:
            channel_id = channel_url.split("/channel/")[1].split("/")[0]
        except IndexError:
            pass
    elif "/user/" in channel_url:
        try:
            username = channel_url.split("/user/")[1].split("/")[0]
        except IndexError:
            pass
    else:
        print("El enlace del canal no contiene '/channel/' ni '/user/'. Intenta con otro enlace.")
        return []

    # Obtener los detalles del canal para extraer el ID de la lista de subidas (uploads)
    if channel_id:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
    else:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={username}&key={api_key}"

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("items"):
        print("No se encontraron datos del canal.")
        return []
    content_details = data["items"][0].get("contentDetails", {})
    uploads_playlist = content_details.get("relatedPlaylists", {}).get("uploads")
    if not uploads_playlist:
        print("No se encontró la lista de subidas del canal.")
        return []

    # Ahora, obtener todos los vídeos de la playlist de subidas
    videos = []
    playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        "part": "snippet",
        "playlistId": uploads_playlist,
        "maxResults": 50,
        "key": api_key
    }
    while True:
        resp = requests.get(playlist_url, params=params)
        resp.raise_for_status()
        pl_data = resp.json()
        for item in pl_data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = snippet.get("resourceId", {}).get("videoId")
            title = snippet.get("title")
            if video_id:
                videos.append({
                    "video_id": video_id,
                    "title": title,
                    "url": f"https://www.youtube.com/watch?v={video_id}"
                })
        next_page = pl_data.get("nextPageToken")
        if next_page:
            params["pageToken"] = next_page
        else:
            break
    return videos

def search_by_keywords(api_key, keywords, max_results_per_keyword=1):
    """
    Para cada línea de palabras clave (no vacía) se realiza una búsqueda
    y se obtiene el primer resultado.
    """
    videos = []
    for keyword in keywords:
        keyword = keyword.strip()
        if not keyword:
            continue
        print(f"Buscando para: {keyword}")
        try:
            results = search_youtube_videos(api_key, keyword, max_results=max_results_per_keyword)
            if results:
                videos.append(results[0])
            else:
                print(f"No se encontró resultado para: {keyword}")
        except Exception as e:
            print(f"Error buscando para '{keyword}': {e}")
    return videos

def download_video(video, output_dir, archive_path):
    """
    Descarga y convierte un vídeo a MP3 usando yt-dlp.
    Utiliza un archivo de descarga para evitar duplicados.
    """
    url = video["url"]
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'download_archive': archive_path,
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    # Si decides forzar la ubicación, descomenta la siguiente línea:
    'ffmpeg_location': r'C:\Users\Ander Sanzo\Desktop\ffmpeg-7.1.1-full_build\bin'
}


    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"Descargando: {video['title']}")
            ydl.download([url])
    except Exception as e:
        print(f"Error al descargar '{video['title']}': {e}")

def main():
    print("Seleccione una opción:")
    print("1. Descargar vídeos de un canal de YouTube")
    print("2. Descargar vídeos por palabras clave (bloque de texto)")
    print("3. Descargar vídeos por búsqueda (por artista, etc.)")
    opcion = input("Ingrese el número de opción (1, 2 o 3): ").strip()

    # No se solicita la ruta de FFmpeg porque se asume que ya está en el PATH.
    threads_input = input("Número de descargas concurrentes (default 5): ").strip()
    threads = int(threads_input) if threads_input else 5

    videos = []
    output_base = "downloads"
    artist_folder = ""
    archive_path = ""
    
    if opcion == "1":
        channel_url = input("Ingrese el enlace del canal de YouTube: ").strip()
        print(f"\nObteniendo vídeos del canal: {channel_url}")
        videos = get_channel_videos(API_KEY, channel_url)
        if not videos:
            print("No se encontraron vídeos para el canal.")
            return
        # Se solicita un nombre para la carpeta donde se guardarán los vídeos
        channel_name = input("Ingrese un nombre para la carpeta del canal (por ejemplo, el nombre del canal): ").strip()
        artist_folder = os.path.join(output_base, sanitize_filename(channel_name))
        archive_path = os.path.join(artist_folder, "download_archive.txt")
        
    elif opcion == "2":
        print("Ingrese el bloque de texto con palabras clave (una por línea). Cuando finalice, ingrese una línea vacía:")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        if not lines:
            print("No se ingresaron palabras clave.")
            return
        videos = search_by_keywords(API_KEY, lines, max_results_per_keyword=1)
        folder_name = input("Ingrese un nombre para la carpeta (por ejemplo, el artista o colección): ").strip()
        artist_folder = os.path.join(output_base, sanitize_filename(folder_name))
        archive_path = os.path.join(artist_folder, "download_archive.txt")
        
    elif opcion == "3":
        artist = input("Ingrese el nombre del artista: ").strip()
        max_results_input = input("Número máximo de vídeos a descargar (default 20): ").strip()
        max_results = int(max_results_input) if max_results_input else 20
        print(f"\nBuscando vídeos en YouTube para: {artist}")
        try:
            videos = search_youtube_videos(API_KEY, artist, max_results)
        except Exception as e:
            print("Error en la búsqueda de vídeos:", e)
            return
        if not videos:
            print("No se encontraron vídeos para el artista.")
            return
        artist_folder = os.path.join(output_base, sanitize_filename(artist))
        archive_path = os.path.join(artist_folder, "download_archive.txt")
    else:
        print("Opción no válida.")
        return

    print(f"\nSe utilizarán {len(videos)} vídeos. Iniciando descargas...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(download_video, video, artist_folder, archive_path)
            for video in videos
        ]
        for future in concurrent.futures.as_completed(futures):
            pass

    print("\nProceso de descarga completado.")

if __name__ == "__main__":
    main()
