
# 🎵 YouTube MP3 Downloader CLI — Search, Extract, Download 💽

A powerful and flexible command-line tool to **search and download audio from YouTube** using keywords, artists, or full channel URLs.  
Perfect for building your own music collection, podcast archive, or offline content hub.

---

## 🚀 Features

- 🔍 Search videos using keywords, artists or YouTube channels
- 📥 Download best audio and convert to MP3 via `yt-dlp`
- 🧠 Uses YouTube Data API to retrieve relevant results
- 📁 Automatically creates named folders for each artist/channel
- 🛑 Avoids duplicates using `download_archive.txt`
- ⚡ Parallel downloads with multithreading support

---

## 💡 How to Use

### 1. Install dependencies

```bash
pip install yt-dlp requests
```

Also, [FFmpeg](https://ffmpeg.org/) must be installed and available in your PATH (or hardcoded in script).

### 2. Get a YouTube Data API Key

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a project, enable **YouTube Data API v3**, and get your key
- Replace the placeholder `API_KEY` in the script

### 3. Run the script

```bash
python youtube_mp3_downloader.py
```

Choose one of three modes:

1. Download by full channel URL (extracts every video)
2. Bulk download using keywords (one per line)
3. Quick search by artist

---

## 📁 Output structure

All downloads are stored under `downloads/` in their respective folder:

```
downloads/
├── Eminem/
│   ├── Not Afraid.mp3
│   └── Rap God.mp3
├── Stromae/
│   └── Alors on danse.mp3
└── ...
```

---

## ⚠️ API Quota Warning

YouTube Data API has a daily quota. If searches stop working, wait or switch API keys.

---

## ✨ Credits

Developed with ❤️ by [@andersanzo](https://github.com/andersanzo)  
Inspired by the need to build smarter music tools for devs 🎧

---

> “Why stream when you can own your library?”

---

# 🎵 Descargador de MP3 desde YouTube — Búscalo, Guárdalo, Disfrútalo 💽

Una herramienta de línea de comandos flexible y potente para **buscar y descargar audio de YouTube** usando palabras clave, nombres de artistas o canales completos.  
Ideal para crear tu colección musical, biblioteca de podcasts o guardar contenido offline.

---

## 🚀 Características

- 🔍 Búsqueda por palabras clave, artista o canal
- 📥 Descarga y convierte vídeos a MP3 con `yt-dlp` + `ffmpeg`
- 🧠 Usa la API de YouTube para obtener resultados precisos
- 📁 Crea carpetas organizadas por artista automáticamente
- 🛑 Evita duplicados con `download_archive.txt`
- ⚡ Soporta descargas paralelas (multithreading)

---

## 💡 Cómo usarlo

### 1. Instala las dependencias

```bash
pip install yt-dlp requests
```

También necesitas tener [FFmpeg](https://ffmpeg.org/) instalado (y opcionalmente fijar su ruta en el script).

### 2. Consigue una API Key de YouTube

- Ve a [Google Cloud Console](https://console.cloud.google.com/)
- Crea un proyecto, activa **YouTube Data API v3** y copia tu clave
- Sustituye `API_KEY` en el script por tu clave

### 3. Ejecuta el script

```bash
python youtube_mp3_downloader.py
```

Y elige una opción:

1. Descargar vídeos desde un canal completo
2. Buscar múltiples canciones (una palabra clave por línea)
3. Búsqueda rápida por artista

---

## 📁 Estructura de salida

Todo se guarda dentro de `downloads/` ordenado por carpeta:

```
downloads/
├── Eminem/
│   ├── Not Afraid.mp3
│   └── Rap God.mp3
├── Stromae/
│   └── Alors on danse.mp3
└── ...
```

---

## ⚠️ Límite de la API

La API de YouTube tiene un límite diario de uso. Si falla, cambia de clave o espera 24h.

---

## ✨ Créditos

Desarrollado con ❤️ por [@andersanzo](https://github.com/andersanzo)  
Inspirado por la necesidad de herramientas musicales inteligentes para devs 🎧

---

> “¿Para qué hacer streaming si puedes tener tu propia biblioteca?”
