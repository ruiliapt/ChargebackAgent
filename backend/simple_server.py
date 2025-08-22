import http.server
import socketserver
import json
from urllib.parse import urlparse

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # Add CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if parsed.path == '/api/disputes':
            # Mock dispute data
            mock_data = {
                "success": True,
                "data": [
                    {
                        "id": "case_001",
                        "caseNumber": "CD2024001",
                        "status": "pending",
                        "riskScore": 75,
                        "category": "FRAUD_UNAUTHORIZED",
                        "subcategory": "Card Not Present",
                        "createdAt": "2024-08-20T10:00:00Z"
                    }
                ]
            }
            self.wfile.write(json.dumps(mock_data).encode())
        else:
            self.wfile.write(json.dumps({"status": "ok"}).encode())

PORT = 5002
with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
    print(f"Server running on port {PORT}")
    httpd.serve_forever()
