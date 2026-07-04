from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
from pytube import YouTube

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(url_parts.query)
        video_id = query_params.get('id', [None])[0]

        if not video_id:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": "Falta el id del video"}).encode())
            return

        try:
            # Conectamos con YouTube usando el ID directo
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            
            # Buscamos el stream progresivo (que tiene video y audio juntos en el mismo archivo)
            # Elegimos la resolucion de 360p o 720p que son las que ExoPlayer reproduce al toque
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()

            if not stream:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "No se encontro stream progresivo"}).encode())
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "url": stream.url}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())