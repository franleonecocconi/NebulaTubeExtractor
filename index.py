from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import urllib.request

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
            # Usamos un endpoint de scraping alternativo que salta el bloqueo de bot
            api_url = f"https://api.cobalt.tools/api/json"
            
            # Configuramos la peticion con los datos del video que queremos
            data = json.dumps({
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "videoQuality": "360", # Calidad baja e ideal para el ExoPlayer de tu reloj
                "downloadMode": "video"
            }).encode('utf-8')
            
            req = urllib.request.Request(
                api_url, 
                data=data, 
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                # Cobalt nos devuelve la URL directa en el campo 'url'
                stream_url = res_data.get('url')
                
                if not stream_url:
                    raise Exception("No se pudo obtener la URL directa del json de respuesta")

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True, "url": stream_url}).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())