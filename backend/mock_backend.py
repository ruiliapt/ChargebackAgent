import http.server
import socketserver
import json
from urllib.parse import urlparse
import datetime

class MockAPIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        path = urlparse(self.path).path
        print(f"Request: {path}")
        
        if path == '/api/disputes':
            # Generate comprehensive mock data
            disputes = []
            for i in range(1, 21):  # 20 cases for testing
                disputes.append({
                    "id": f"case_{i:03d}",
                    "caseNumber": f"CD2024{i:03d}",
                    "status": ["pending", "review", "completed"][i % 3],
                    "riskScore": 20 + (i * 4) % 80,
                    "aiRecommendation": ["approve", "reject", "review"][i % 3],
                    "aiConfidence": 60 + (i * 5) % 40,
                    "category": ["FRAUD_UNAUTHORIZED", "PROCESSING_ISSUES", "MERCHANT_MERCHANDISE"][i % 3],
                    "subcategory": f"Subcategory_{i % 5 + 1}",
                    "createdAt": f"2024-08-{20 - (i % 10):02d}T10:{i % 60:02d}:00Z",
                    "updatedAt": f"2024-08-20T1{i % 10}:{i % 60:02d}:00Z",
                    "priority": ["low", "medium", "high"][i % 3],
                    "humanDecision": None if i % 4 == 0 else ["approve", "reject", "investigate"][i % 3],
                    "transaction": {
                        "id": f"txn_{i:03d}",
                        "amount": 100 + (i * 25) % 500,
                        "currency": "USD",
                        "merchantName": f"Merchant {i}",
                        "transactionDate": f"2024-08-{15 + (i % 5):02d}T09:00:00Z",
                        "cardLast4": f"{1000 + i % 9999:04d}"
                    },
                    "customer": {
                        "id": f"cust_{i:03d}",
                        "name": f"Customer {i}",
                        "email": f"customer{i}@example.com",
                        "accountType": ["premium", "standard", "basic"][i % 3]
                    },
                    "disputeReason": f"Dispute reason {i}",
                    "disputeDescription": f"Description for case {i}"
                })
            
            response = {
                "success": True,
                "data": disputes,
                "total": len(disputes)
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif path.startswith('/api/analyze/') and path.endswith('/reanalyze'):
            # Mock re-analysis endpoint
            response = {
                "success": True,
                "riskScore": 45,
                "recommendation": "approve",
                "confidence": 85,
                "analysis": "Updated analysis with analyst feedback incorporated.",
                "keyFactors": ["Updated factor 1", "Updated factor 2"],
                "warningFlags": []
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            # Health check or other endpoints
            response = {"status": "ok", "message": "Mock backend running"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        # Handle POST requests (like re-analysis)
        self.do_GET()
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

PORT = 5002
print(f"Starting mock backend server on port {PORT}...")
with socketserver.TCPServer(("", PORT), MockAPIHandler) as httpd:
    print(f"Mock backend running at http://localhost:{PORT}")
    print("Available endpoints:")
    print("  GET  /api/disputes")
    print("  POST /api/analyze/<id>/reanalyze")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock backend...")
