#!/usr/bin/env python3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
import random

class ProperHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        if self.path == '/api/disputes':
            cases = []
            now = datetime.now()
            
            # Category distribution: More Fraud (100), then Merchandise (60), Processing (40)
            categories = ["FRAUD_UNAUTHORIZED"] * 100 + ["MERCHANT_MERCHANDISE"] * 60 + ["PROCESSING_ISSUES"] * 40
            random.shuffle(categories)
            
            for i in range(200):
                case_date = now - timedelta(days=i % 90)  # Last 90 days
                category = categories[i]
                
                # Legitimacy fields based on category
                if category == "FRAUD_UNAUTHORIZED":
                    # 40% have non-zero legitimacy (complex fraud scenarios)
                    has_legitimacy = i % 10 < 4
                    same_card = random.randint(1, 8) if has_legitimacy else 0
                    same_address = random.randint(1, 6) if has_legitimacy else 0
                    same_ip = random.randint(1, 12) if has_legitimacy else 0
                    same_device = random.randint(1, 5) if has_legitimacy else 0
                elif category in ["MERCHANT_MERCHANDISE", "PROCESSING_ISSUES"]:
                    # 100% have legitimacy fields (loyal customers)
                    same_card = random.randint(3, 25)
                    same_address = random.randint(2, 15)
                    same_ip = random.randint(5, 40)
                    same_device = random.randint(1, 8)
                else:
                    same_card = same_address = same_ip = same_device = 0
                
                # Create logical merchant-category-items combinations
                merchant_data = [
                    # Electronics
                    {"merchant": "TechStore Pro", "category": "Electronics", "items": ["Gaming Laptop", "Wireless Headphones", "Smart Watch", "Bluetooth Speaker", "Smartphone"]},
                    {"merchant": "Electronics Plus", "category": "Electronics", "items": ["Gaming Console", "Tablet", "Smart TV", "Camera", "Drone"]},
                    {"merchant": "Gaming Central", "category": "Electronics", "items": ["Gaming Mouse", "Gaming Keyboard", "VR Headset", "Gaming Chair", "Monitor"]},
                    
                    # Fashion
                    {"merchant": "Fashion Hub", "category": "Fashion", "items": ["Designer Jacket", "Running Shoes", "Luxury Handbag", "Sunglasses", "Watch"]},
                    {"merchant": "Style Boutique", "category": "Fashion", "items": ["Evening Dress", "Leather Boots", "Silk Scarf", "Belt", "Jewelry"]},
                    
                    # Digital
                    {"merchant": "Digital Downloads", "category": "Digital", "items": ["Software License", "E-book", "Digital Game", "Online Course", "Music Album"]},
                    {"merchant": "CloudSoft", "category": "Digital", "items": ["SaaS Subscription", "Digital Magazine", "App Premium", "Online Training", "Digital Art"]},
                    
                    # Sports
                    {"merchant": "Sports Gear Co", "category": "Sports", "items": ["Basketball", "Tennis Racket", "Yoga Mat", "Protein Powder", "Fitness Tracker"]},
                    {"merchant": "Athletic Pro", "category": "Sports", "items": ["Running Shoes", "Gym Equipment", "Sports Jersey", "Exercise Bike", "Dumbbells"]},
                    
                    # Home
                    {"merchant": "Home & Garden", "category": "Home", "items": ["Kitchen Appliance", "Garden Tools", "Home Decor", "Furniture", "Bedding Set"]},
                    {"merchant": "Living Spaces", "category": "Home", "items": ["Dining Table", "Sofa", "Lamp", "Rug", "Picture Frame"]},
                    
                    # Books
                    {"merchant": "Book World", "category": "Books", "items": ["Novel", "Textbook", "Cookbook", "Biography", "Travel Guide"]},
                    
                    # Food
                    {"merchant": "Gourmet Foods", "category": "Food", "items": ["Organic Coffee", "Artisan Chocolate", "Specialty Tea", "Gourmet Cheese", "Wine"]},
                ]
                
                # Pick a random merchant-category-item combination
                merchant_combo = random.choice(merchant_data)
                merchant_name = merchant_combo["merchant"]
                merchant_category = merchant_combo["category"]
                item_name = random.choice(merchant_combo["items"])
                
                # Digital goods logic
                digital_goods = "Y" if merchant_category == "Digital" else random.choice(["Y", "N"])
                
                # Customer details with logical constraints
                previous_disputes = random.randint(0, 8)
                dispute_customer_won = random.randint(0, previous_disputes) if previous_disputes > 0 else 0
                
                # Shipping logic with proper dependencies
                if digital_goods == "Y":
                    # Digital goods are "shipped" and "delivered" immediately (electronically)
                    item_shipped = "Y"
                    item_delivered = "Y"
                    # Digital delivery happens immediately after purchase
                    item_shipped_date = (case_date + timedelta(minutes=random.randint(1, 30))).isoformat()  # Within 30 minutes
                    item_delivered_date = (case_date + timedelta(minutes=random.randint(1, 30))).isoformat()  # Instant delivery
                elif category == "MERCHANT_MERCHANDISE":
                    # Merchandise issues: Customer MUST have received the item to complain about it
                    item_shipped = "Y"
                    item_delivered = "Y"
                    # Physical shipping and delivery timeline
                    shipped_days = random.randint(1, 3)
                    delivered_days = shipped_days + random.randint(2, 7)
                    item_shipped_date = (case_date + timedelta(days=shipped_days)).isoformat()
                    item_delivered_date = (case_date + timedelta(days=delivered_days)).isoformat()
                else:
                    # Other physical goods (fraud, processing issues) - normal shipping logic
                    item_shipped = random.choice(["Y", "N"])
                    if item_shipped == "Y":
                        item_shipped_date = (case_date + timedelta(days=random.randint(1, 3))).isoformat()
                        # If shipped, it might be delivered
                        item_delivered = random.choice(["Y", "N"])
                        if item_delivered == "Y":
                            # Delivered date must be after shipped date
                            shipped_days = random.randint(1, 3)
                            delivered_days = shipped_days + random.randint(2, 7)
                            item_delivered_date = (case_date + timedelta(days=delivered_days)).isoformat()
                        else:
                            item_delivered_date = None
                    else:
                        # Not shipped = definitely not delivered
                        item_delivered = "N"
                        item_shipped_date = None
                        item_delivered_date = None

                # Human decisions based on category
                if category == "PROCESSING_ISSUES":
                    human_decisions = ["approve", "reject", "investigate", "send_to_merchant"]
                else:
                    human_decisions = ["approve", "reject", "investigate"]
                
                # Subcategories
                if category == "FRAUD_UNAUTHORIZED":
                    subcategories = ["Account Takeover", "Card Not Present", "Identity Theft", "Stolen Card", "Friendly Fraud"]
                elif category == "MERCHANT_MERCHANDISE":
                    subcategories = ["Product Quality", "Product Description", "Defective Item", "Wrong Item", "Missing Parts"]
                else:  # PROCESSING_ISSUES
                    subcategories = ["Payment Processing", "Billing Error", "Duplicate Charge", "Authorization Issue", "Settlement Delay"]
                
                cases.append({
                    "id": f"case_{i+1:03d}",
                    "caseNumber": f"CD2024{i+1:03d}",
                    "status": random.choice(["pending", "review", "completed", "analyzing"]),
                    "riskScore": random.randint(15, 95),
                    "aiRecommendation": random.choice(["approve", "reject", "review"]),
                    "aiConfidence": random.randint(65, 98),
                    "category": category,
                    "subcategory": random.choice(subcategories),
                    "createdAt": case_date.isoformat(),
                    "updatedAt": (case_date + timedelta(hours=random.randint(1, 48))).isoformat(),
                    "priority": random.choice(["low", "medium", "high", "critical"]),
                    "humanDecision": random.choice(human_decisions) if i % 3 != 0 else None,
                    
                    # Transaction details
                    "transaction": {
                        "amount": random.randint(25, 2500),
                        "currency": "USD",
                        "merchantName": merchant_name,
                        "merchantCategory": merchant_category,
                        "transactionDate": (case_date - timedelta(days=random.randint(1, 7))).isoformat(),
                        "cardLast4": f"{random.randint(1000, 9999)}",
                        "location": random.choice(["New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ"]),
                        "checkoutIp": f"{random.randint(192, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                        "checkoutDevice": random.choice(["iPhone 15", "MacBook Pro", "Windows PC", "Android Phone", "iPad", "Chrome OS"]),
                        
                        # Logically connected fields
                        "items": item_name,
                        "digitalGoods": digital_goods,
                        "loginMethod": random.choice([
                            "Password", "App Login", "Biometric", "Two-Factor Auth", "Social Login (Google)",
                            "Social Login (Facebook)", "Guest Checkout", "SMS Verification", "Email Login", "Phone Login"
                        ]),
                        
                        # Proper shipping logic
                        "itemShipped": item_shipped,
                        "itemShippedDate": item_shipped_date,
                        "itemDelivered": item_delivered,
                        "itemDeliveredDate": item_delivered_date,
                        
                        # Legitimacy fields at transaction level too (for backward compatibility)
                        "sameCardSuccessOrders": same_card,
                        "sameAddressSuccessOrders": same_address,
                        "sameIpSuccessOrders": same_ip,
                        "sameDeviceSuccessOrders": same_device
                    },
                    
                    # Customer details with logical constraints
                    "customer": {
                        "name": f"Customer {i+1}",
                        "email": f"customer{i+1}@example.com",
                        "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                        "accountType": random.choice(["premium", "standard", "basic"]),
                        "creditScore": random.randint(550, 850),
                        "customerSince": (case_date - timedelta(days=random.randint(30, 1000))).isoformat(),
                        "previousDisputes": previous_disputes,
                        "disputePercentage": random.randint(0, 15),
                        "disputeCustomerWon": dispute_customer_won,  # Always <= previousDisputes
                        "totalPurchaseAmount": random.randint(500, 50000),
                        "linkedCustomersCount": random.randint(0, 12),
                        "linkedCustomersDisputeRate": random.randint(0, 10),
                        "linkedByDevice": random.randint(0, 5),
                        "linkedByIp": random.randint(0, 8),
                        "linkedByCard": random.randint(0, 3),
                        "linkedByAddress": random.randint(0, 4)
                    },
                    
                    # Dispute details
                    "disputeReason": random.choice([
                        "Unauthorized transaction", "Product not received", "Product defective",
                        "Billing error", "Cancelled transaction", "Duplicate charge",
                        "Quality issues", "Description mismatch", "Processing delay"
                    ]),
                    "disputeDescription": f"Customer dispute regarding transaction {i+1} with detailed explanation of the issue.",
                    
                    # AI Analysis fields that DisputeAnalyzer expects
                    "aiAnalysis": f"Detailed AI analysis for case {i+1}. Risk assessment based on transaction patterns, customer history, and evidence provided.",
                    "evidence": [
                        {"type": "receipt", "description": f"Transaction receipt for case {i+1}", "fileName": f"receipt_{i+1}.pdf"},
                        {"type": "communication", "description": f"Customer communication logs for case {i+1}", "fileName": f"communication_{i+1}.txt"}
                    ] if i % 3 == 0 else [],
                    
                    # Case-level fields
                    "cardIssuer": random.choice(["Chase", "Bank of America", "Wells Fargo", "Citi", "Capital One", "Discover"]),
                    "cardNetwork": random.choice(["Visa", "Mastercard", "American Express", "Discover"]),
                    "reasonCode": random.choice(["4855", "4863", "4837", "4812", "4541", "4534", "4553"]),
                    
                    # LEGITIMACY FIELDS (the key data we've been working on)
                    "same_card_success_orders": same_card,
                    "same_address_success_orders": same_address,
                    "same_ip_success_orders": same_ip,
                    "same_device_success_orders": same_device,
                    
                    # Additional fields we restored (using logical values)
                    "items": item_name,
                    "digital_goods": digital_goods,
                    "login_method": random.choice([
                        "Password", "App Login", "Biometric", "Two-Factor Auth", "Social Login (Google)",
                        "Social Login (Facebook)", "Guest Checkout", "SMS Verification", "Email Login", "Phone Login"
                    ]),
                    "item_shipped": item_shipped,
                    "item_shipped_date": item_shipped_date,
                    "item_delivered": item_delivered,
                    "item_delivered_date": item_delivered_date,
                    
                    # Analyst feedback (for re-analysis feature)
                    "analystFeedback": f"Initial analysis feedback for case {i+1}" if i % 5 == 0 else None
                })
            
            self.wfile.write(json.dumps(cases).encode())
            
        elif self.path == '/api/categories/summary':
            summary = {
                "FRAUD_UNAUTHORIZED": 100,
                "MERCHANT_MERCHANDISE": 60, 
                "PROCESSING_ISSUES": 40
            }
            self.wfile.write(json.dumps(summary).encode())
            
        else:
            self.wfile.write(b'{"status": "ok"}')
    
    def do_POST(self):
        # Handle re-analysis requests
        if '/reanalyze' in self.path:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length:
                post_data = self.rfile.read(content_length)
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": True,
                "riskScore": random.randint(20, 85),
                "recommendation": random.choice(["approve", "reject", "review"]),
                "confidence": random.randint(75, 95),
                "analysis": "Re-analyzed with analyst feedback. Updated risk assessment based on additional context provided.",
                "keyFactors": ["Analyst Input", "Updated Evidence", "Pattern Analysis"],
                "warningFlags": []
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.do_GET()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 5002), ProperHandler)
    print("🚀 PROPER Backend with all features running on http://localhost:5002")
    print("✅ 200 cases with proper distribution: 100 Fraud, 60 Merchandise, 40 Processing")
    print("✅ All legitimacy fields populated")
    print("✅ Send To Merchant option for Processing Issues")
    print("✅ All restored fields included")
    print("✅ Logical constraints: disputeCustomerWon <= previousDisputes")
    server.serve_forever()