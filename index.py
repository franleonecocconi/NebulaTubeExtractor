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
            # Usamos una de las instancias oficiales y mas estables de Invidious
            api_url = f"https://invidious.perennialte.ch/api/v1/videos/{video_id}"
            
            req = urllib.request.Request(
                api_url, 
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                
                # Buscamos en la lista de formatos los streams de video que vienen listos con audio
                format_streams = res_data.get('formatStreams', [])
                
                if not format_streams:
                    raise Exception("No se encontraron streams directos disponibles")
                
                # Agarramos el primer stream que suele ser el de calidad justa (360p o similar) ideal para el reloj
                stream_url = format_streams[0].get('url')

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