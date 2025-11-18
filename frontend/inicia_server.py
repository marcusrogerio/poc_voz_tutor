import http.server
import socketserver

PORT = 8001

class SimpleCORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        return super().end_headers()


with socketserver.ThreadingTCPServer(("", PORT), SimpleCORSRequestHandler) as httpd:
    print(f"Frontend rodando em: http://localhost:{PORT}")
    print("Pressione CTRL+C para parar.")
    httpd.serve_forever()
