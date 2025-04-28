#!/usr/bin/env python3
import os
import requests
import concurrent.futures
from yt_dlp import YoutubeDL
import re

# Coloca aquí tu API Key de YouTube Data API
API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  #Reemplaza con tu clave real

def sanitize_filename(filename):
    """Elimina caracteres no válidos en nombres de archivos."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def search_youtube_videos(api_key, query, max_results=20):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = { "part": "snippet", "q": query, "type": "video",
            "maxResults": max_results, "key": api_key }
    r = requests.get(search_url, params=params); r.raise_for_status()
    data = r.json()
    videos = []
    for item in data.get("items", []):
        vid = item.get("id", {}).get("videoId")
        if not vid: continue
        videos.append({
            "video_id": vid,
            "title": item["snippet"]["title"],
            "url": f"https://www.youtube.com/watch?v={vid}"
        })
    return videos

def get_channel_videos(api_key, channel_url):
    channel_id = None; username = None
    if "/channel/" in channel_url:
        channel_id = channel_url.split("/channel/")[1].split("/")[0]
    elif "/user/" in channel_url:
        username = channel_url.split("/user/")[1].split("/")[0]
    else:
        print("URL de canal inválida."); return []

    if channel_id:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
    else:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&forUsername={username}&key={api_key}"
    resp = requests.get(url); resp.raise_for_status()
    items = resp.json().get("items")
    if not items:
        print("No se encontraron datos del canal."); return []
    uploads = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos = []
    playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {"part":"snippet","playlistId":uploads,"maxResults":50,"key":api_key}
    while True:
        r = requests.get(playlist_url, params=params); r.raise_for_status()
        pl = r.json()
        for item in pl.get("items", []):
            sn = item["snippet"]
            vid = sn["resourceId"]["videoId"]
            videos.append({"video_id": vid, "title": sn["title"], "url": f"https://www.youtube.com/watch?v={vid}"})
        if "nextPageToken" in pl:
            params["pageToken"] = pl["nextPageToken"]
        else:
            break
    return videos

def search_by_keywords(api_key, keywords, max_results_per_keyword=1):
    videos = []
    for kw in keywords:
        kw = kw.strip()
        if not kw: continue
        print(f"Buscando para: {kw}")
        res = search_youtube_videos(api_key, kw, max_results_per_keyword)
        if res:
            videos.append(res[0])
        else:
            print(f"No se encontró resultado para: {kw}")
    return videos

def download_video(video, output_dir, archive_path):
    """
    Descarga y convierte. Devuelve (title, True/False, error_msg_or_empty).
    """
    url = video["url"]
    os.makedirs(output_dir, exist_ok=True)
    opts = {
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
    }
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        return (video["title"], True, "")
    except Exception as e:
        return (video["title"], False, str(e))

def main():
    print("Seleccione una opción:")
    print("1. Descargar vídeos de un canal de YouTube")
    print("2. Descargar vídeos por palabras clave")
    print("3. Descargar vídeos por búsqueda (artista)")
    opcion = input("Opción (1,2,3): ").strip()

    threads = int(input("Número de descargas concurrentes (default 5): ") or 5)
    videos = []
    base = "downloads"
    dest_folder = ""
    archive = ""

    if opcion == "1":
        url = input("Enlace del canal: ").strip()
        videos = get_channel_videos(API_KEY, url)
        if not videos: return
        name = input("Nombre de carpeta para el canal: ").strip()
        dest_folder = os.path.join(base, sanitize_filename(name))
    elif opcion == "2":
        print("Introduce palabras clave (una por línea). Línea vacía para terminar):")
        lines = []
        while True:
            l = input().strip()
            if not l: break
            lines.append(l)
        if not lines: return
        videos = search_by_keywords(API_KEY, lines)
        name = input("Nombre de carpeta para estas descargas: ").strip()
        dest_folder = os.path.join(base, sanitize_filename(name))
    elif opcion == "3":
        artist = input("Nombre del artista: ").strip()
        maxr = int(input("Máx vídeos (default 20): ") or 20)
        videos = search_youtube_videos(API_KEY, artist, maxr)
        dest_folder = os.path.join(base, sanitize_filename(artist))
    else:
        print("Opción no válida."); return

    archive = os.path.join(dest_folder, "download_archive.txt")
    print(f"\nTotal vídeos: {len(videos)}. Iniciando descargas...\n")

    # Ejecutamos con concurrencia y recogemos resultados
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
        futures = [ex.submit(download_video, v, dest_folder, archive) for v in videos]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    # Filtrar éxitos y fallos
    successes = [r[0] for r in results if r[1]]
    failures  = [(r[0], r[2]) for r in results if not r[1]]

    # Generar el informe
    report_path = os.path.join(dest_folder, "download_report.txt")
    with open(report_path, "w", encoding="utf-8") as rpt:
        rpt.write("=== DESCARGAS EXITOSAS ===\n")
        for title in successes:
            rpt.write(f"{title}\n")
        rpt.write("\n=== ERRORES ===\n")
        for title, err in failures:
            rpt.write(f"{title}  --->  {err}\n")

    print("\nProceso completado.")
    print(f"Informe guardado en: {report_path}")

if __name__ == "__main__":
    main()
