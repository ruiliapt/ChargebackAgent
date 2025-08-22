import http.server
import socketserver
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta
import random

class BackendHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        path = urlparse(self.path).path
        
        if path == '/api/disputes':
            disputes = []
            now = datetime.now()
            categories = ["FRAUD_UNAUTHORIZED", "PROCESSING_ISSUES", "MERCHANT_MERCHANDISE"]
            
            for i in range(1, 201):  # 200 cases
                created_date = now - timedelta(days=i % 30)  # Spread over last 30 days
                
                disputes.append({
                    "id": f"case_{i:03d}",
                    "caseNumber": f"CD2024{i:03d}",
                    "status": ["pending", "review", "completed"][i % 3],
                    "riskScore": 20 + (i * 3) % 80,
                    "aiRecommendation": ["approve", "reject", "review"][i % 3],
                    "aiConfidence": 60 + (i * 2) % 40,
                    "category": categories[i % 3],
                    "subcategory": f"Sub_{i % 5}",
                    "createdAt": created_date.isoformat() + "Z",
                    "updatedAt": created_date.isoformat() + "Z",
                    "priority": ["low", "medium", "high"][i % 3],
                    "humanDecision": None if i % 4 == 0 else ["approve", "reject"][i % 2],
                    "transaction": {
                        "id": f"txn_{i:03d}",
                        "amount": 100 + (i * 10) % 500,
                        "currency": "USD",
                        "merchantName": f"Store {i % 20}",
                        "transactionDate": created_date.isoformat() + "Z",
                        "cardLast4": str(1000 + i % 9000)
                    },
                    "customer": {
                        "id": f"cust_{i:03d}",
                        "name": f"Customer {i}",
                        "email": f"c{i}@test.com",
                        "accountType": ["premium", "standard"][i % 2]
                    },
                    "disputeReason": f"Reason {i}",
                    "disputeDescription": f"Description {i}"
                })
            
            self.wfile.write(json.dumps(disputes).encode())
            
        elif path == '/api/categories/summary':
            self.wfile.write(json.dumps({"FRAUD_UNAUTHORIZED": 67, "PROCESSING_ISSUES": 67, "MERCHANT_MERCHANDISE": 66}).encode())
        else:
            self.wfile.write(json.dumps({"status": "ok"}).encode())
    
    def do_POST(self):
        self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

with socketserver.TCPServer(("", 5002), BackendHandler) as httpd:
    print("✅ Backend with 200 cases running on port 5002")
    httpd.serve_forever()
