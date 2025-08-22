#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import random

class FastHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        if self.path == '/api/disputes':
            # Generate 200 cases quickly
            cases = []
            now = datetime.now()
            
            for i in range(200):
                case_date = now - timedelta(days=i % 30)
                cases.append({
                    "id": f"case_{i+1}",
                    "caseNumber": f"CD2024{i+1:03d}",
                    "status": ["pending", "review", "completed"][i % 3],
                    "riskScore": 20 + (i * 3) % 75,
                    "aiRecommendation": ["approve", "reject", "review"][i % 3],
                    "aiConfidence": 70 + (i % 30),
                    "category": ["FRAUD_UNAUTHORIZED", "PROCESSING_ISSUES", "MERCHANT_MERCHANDISE"][i % 3],
                    "subcategory": f"Sub Category {i % 5 + 1}",
                    "createdAt": case_date.isoformat(),
                    "updatedAt": case_date.isoformat(),
                    "priority": ["low", "medium", "high", "critical"][i % 4],
                    "transaction": {
                        "amount": 50 + (i * 13) % 950,
                        "currency": "USD",
                        "merchantName": f"Merchant Store {i % 25 + 1}",
                        "transactionDate": case_date.isoformat()
                    },
                    "customer": {
                        "name": f"Customer {i+1}",
                        "email": f"customer{i+1}@test.com"
                    },
                    "disputeReason": f"Dispute reason {i+1}"
                })
            
            response = json.dumps(cases)
            self.wfile.write(response.encode())
            
        elif self.path == '/api/categories/summary':
            summary = {"FRAUD_UNAUTHORIZED": 67, "PROCESSING_ISSUES": 67, "MERCHANT_MERCHANDISE": 66}
            self.wfile.write(json.dumps(summary).encode())
            
        else:
            self.wfile.write(b'{"status": "ok"}')
    
    def do_POST(self):
        self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 5002), FastHandler)
    print("🚀 FAST Backend with 200 cases running on http://localhost:5002")
    server.serve_forever()
