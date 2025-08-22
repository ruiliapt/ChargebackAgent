#!/usr/bin/env python3
"""
Populate missing transaction fields for all dispute cases:
- Items
- Digital Goods (Y/N)
- Login Method
- Item Shipped (Y/N)
- Item Shipped Date
- Item Delivered (Y/N)
- Item Delivered Date
"""

import random
import sys
from datetime import datetime, timedelta
from app import app, db, DisputeCase

def populate_missing_fields():
    """Populate missing transaction fields for all dispute cases"""
    
    # Sample data for realistic field values
    SAMPLE_ITEMS = [
        # Physical goods
        "Gaming Laptop", "iPhone 14 Pro", "Nike Air Jordans", "Samsung TV 55\"", "Coffee Maker",
        "Wireless Headphones", "Designer Handbag", "Winter Jacket", "Running Shoes", "Tablet",
        "Smart Watch", "Bluetooth Speaker", "Kitchen Knife Set", "Yoga Mat", "Backpack",
        "Sunglasses", "Power Bank", "Fitness Tracker", "Motorcycle Helmet", "Guitar",
        "Camera Lens", "Office Chair", "Perfume", "Skincare Set", "Book Collection",
        "Board Games", "Tools Set", "Bicycle", "Home Decor", "Kitchenware",
        
        # Services
        "Hotel Booking", "Flight Ticket", "Car Rental", "Concert Ticket", "Restaurant Meal",
        "Spa Service", "Haircut & Styling", "Personal Training", "Legal Consultation", "Home Cleaning",
        "Food Delivery", "Uber Ride", "Movie Tickets", "Event Photography", "Wedding Planning",
        
        # Digital goods
        "Software License", "Mobile App Purchase", "Digital Music Album", "E-book", "Online Course",
        "Video Game Download", "Streaming Subscription", "Cloud Storage", "VPN Service", "Design Templates",
        "Stock Photos", "Digital Art", "Cryptocurrency", "NFT Purchase", "Online Coaching"
    ]
    
    DIGITAL_ITEMS = {
        "Software License", "Mobile App Purchase", "Digital Music Album", "E-book", "Online Course",
        "Video Game Download", "Streaming Subscription", "Cloud Storage", "VPN Service", "Design Templates",
        "Stock Photos", "Digital Art", "Cryptocurrency", "NFT Purchase", "Online Coaching"
    }
    
    SERVICE_ITEMS = {
        "Hotel Booking", "Flight Ticket", "Car Rental", "Concert Ticket", "Restaurant Meal",
        "Spa Service", "Haircut & Styling", "Personal Training", "Legal Consultation", "Home Cleaning",
        "Food Delivery", "Uber Ride", "Movie Tickets", "Event Photography", "Wedding Planning"
    }
    
    LOGIN_METHODS = [
        "Password", "App Login", "Biometric", "Two-Factor Auth", "Social Login (Google)",
        "Social Login (Facebook)", "Guest Checkout", "SMS Verification", "Email Login", "Phone Login"
    ]
    
    with app.app_context():
        cases = DisputeCase.query.all()
        
        print(f"Populating missing fields for {len(cases)} dispute cases...")
        
        updated_count = 0
        for case in cases:
            # Set Items if missing
            if not case.items:
                case.items = random.choice(SAMPLE_ITEMS)
            
            # Set Digital Goods based on item type
            if not case.digital_goods:
                case.digital_goods = 'Y' if case.items in DIGITAL_ITEMS else 'N'
            
            # Set Login Method if missing
            if not case.login_method:
                case.login_method = random.choice(LOGIN_METHODS)
            
            # Set shipping info based on item type
            is_digital = case.items in DIGITAL_ITEMS
            is_service = case.items in SERVICE_ITEMS
            
            # Digital goods and services don't ship
            if is_digital or is_service:
                if not case.item_shipped:
                    case.item_shipped = 'N'
                if not case.item_delivered:
                    case.item_delivered = 'N'
            else:
                # Physical goods shipping logic
                if not case.item_shipped:
                    case.item_shipped = random.choices(['Y', 'N'], weights=[85, 15])[0]  # 85% shipped
                
                if case.item_shipped == 'Y':
                    # Set shipped date if missing
                    if not case.item_shipped_date:
                        # Random date between transaction date and now
                        transaction_date = case.transaction_date
                        max_ship_days = min(7, (datetime.now() - transaction_date).days)
                        if max_ship_days > 0:
                            ship_days = random.randint(0, max_ship_days)
                            case.item_shipped_date = transaction_date + timedelta(days=ship_days)
                    
                    # Set delivered status and date
                    if not case.item_delivered:
                        case.item_delivered = random.choices(['Y', 'N'], weights=[75, 25])[0]  # 75% delivered if shipped
                    
                    if case.item_delivered == 'Y' and not case.item_delivered_date:
                        # Delivery 1-5 days after shipping
                        if case.item_shipped_date:
                            delivery_days = random.randint(1, 5)
                            case.item_delivered_date = case.item_shipped_date + timedelta(days=delivery_days)
                else:
                    # Not shipped means not delivered
                    if not case.item_delivered:
                        case.item_delivered = 'N'
            
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"  Updated {updated_count} cases...")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully populated missing fields for {updated_count} cases")
        
        # Verify the changes
        print(f"\n📊 Field Population Statistics:")
        
        cases_with_items = DisputeCase.query.filter(DisputeCase.items.isnot(None)).count()
        digital_goods_y = DisputeCase.query.filter_by(digital_goods='Y').count()
        digital_goods_n = DisputeCase.query.filter_by(digital_goods='N').count()
        shipped_y = DisputeCase.query.filter_by(item_shipped='Y').count()
        shipped_n = DisputeCase.query.filter_by(item_shipped='N').count()
        delivered_y = DisputeCase.query.filter_by(item_delivered='Y').count()
        delivered_n = DisputeCase.query.filter_by(item_delivered='N').count()
        
        print(f"  - Items populated: {cases_with_items}/{len(cases)}")
        print(f"  - Digital Goods: Y={digital_goods_y}, N={digital_goods_n}")
        print(f"  - Item Shipped: Y={shipped_y}, N={shipped_n}")
        print(f"  - Item Delivered: Y={delivered_y}, N={delivered_n}")
        
        print(f"\n🎯 Field population completed successfully!")
        return True

if __name__ == "__main__":
    print("🔄 Populating missing transaction fields for all dispute cases...")
    
    success = populate_missing_fields()
    
    if success:
        print("\n🎉 Missing fields population completed successfully!")
        print("\n💡 All cases now have complete transaction details.")
    else:
        print("\n❌ Field population failed!")
        sys.exit(1)
