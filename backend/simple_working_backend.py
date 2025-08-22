import http.server
import socketserver
import json
from urllib.parse import urlparse

class WorkingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        path = urlparse(self.path).path
        print(f"API Request: {path}")
        
        if path == '/api/disputes':
            # Simple working data
            disputes = [
                {
                    "id": "case_001",
                    "caseNumber": "CD2024001",
                    "status": "pending",
                    "riskScore": 75,
                    "aiRecommendation": "reject",
                    "aiConfidence": 85,
                    "category": "FRAUD_UNAUTHORIZED",
                    "subcategory": "Card Fraud",
                    "createdAt": "2024-08-20T10:00:00Z",
                    "updatedAt": "2024-08-20T10:00:00Z",
                    "priority": "high",
                    "humanDecision": None,
                    "transaction": {
                        "id": "txn_001",
                        "amount": 250,
                        "currency": "USD",
                        "merchantName": "Test Merchant",
                        "transactionDate": "2024-08-19T09:00:00Z",
                        "cardLast4": "1234"
                    },
                    "customer": {
                        "id": "cust_001",
                        "name": "John Doe",
                        "email": "john@example.com",
                        "accountType": "premium"
                    },
                    "disputeReason": "Unauthorized transaction",
                    "disputeDescription": "Customer claims card was stolen"
                },
                {
                    "id": "case_002", 
                    "caseNumber": "CD2024002",
                    "status": "review",
                    "riskScore": 45,
                    "aiRecommendation": "approve", 
                    "aiConfidence": 90,
                    "category": "MERCHANT_MERCHANDISE",
                    "subcategory": "Product Issue",
                    "createdAt": "2024-08-20T11:00:00Z",
                    "updatedAt": "2024-08-20T11:00:00Z", 
                    "priority": "medium",
                    "humanDecision": None,
                    "transaction": {
                        "id": "txn_002",
                        "amount": 150,
                        "currency": "USD",
                        "merchantName": "Store ABC",
                        "transactionDate": "2024-08-18T14:00:00Z",
                        "cardLast4": "5678"
                    },
                    "customer": {
                        "id": "cust_002",
                        "name": "Jane Smith", 
                        "email": "jane@example.com",
                        "accountType": "standard"
                    },
                    "disputeReason": "Product not received",
                    "disputeDescription": "Item never delivered"
                }
            ]
            
            print(f"Returning {len(disputes)} disputes")
            self.wfile.write(json.dumps(disputes).encode())
            
        elif path == '/api/categories/summary':
            response = {"FRAUD_UNAUTHORIZED": 1, "PROCESSING_ISSUES": 0, "MERCHANT_MERCHANDISE": 1}
            self.wfile.write(json.dumps(response).encode())
            
        else:
            response = {"status": "ok"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

PORT = 5002
print(f"Starting simple working backend on port {PORT}...")
with socketserver.TCPServer(("", PORT), WorkingHandler) as httpd:
    print("✅ Backend ready!")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Backend stopped")
