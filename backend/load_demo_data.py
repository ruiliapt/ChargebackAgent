#!/usr/bin/env python3
"""
Load generated chargeback demo data into SQLite database
"""

import json
import sys
import os
from datetime import datetime
from app import app, db, DisputeCase, Customer

def load_data_to_database():
    """Load the generated JSON data into SQLite database"""
    
    # Read the generated data
    try:
        with open('chargeback_demo_data.json', 'r') as f:
            cases_data = json.load(f)
    except FileNotFoundError:
        print("Error: chargeback_demo_data.json not found. Please run generate_demo_data.py first.")
        return False
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        DisputeCase.query.delete()
        Customer.query.delete()
        db.session.commit()
        
        # Track unique customers
        customers_added = set()
        
        print(f"Loading {len(cases_data)} cases into database...")
        
        for i, case_data in enumerate(cases_data, 1):
            try:
                # Add customer if not already added
                customer_id = case_data['customer']['id']
                if customer_id not in customers_added:
                    customer = Customer(
                        id=customer_id,
                        name=case_data['customer']['name'],
                        email=case_data['customer']['email'],
                        phone=case_data['customer']['phone'],
                        account_type=case_data['customer']['accountType'],
                        credit_score=case_data['customer']['creditScore'],
                        customer_since=datetime.fromisoformat(case_data['customer']['customerSince']).date(),
                        previous_disputes=case_data['customer']['previousDisputes']
                    )
                    db.session.add(customer)
                    customers_added.add(customer_id)
                
                # Add dispute case
                dispute = DisputeCase(
                    id=case_data['id'],
                    case_number=case_data['case_number'],
                    transaction_id=case_data['transaction']['id'],
                    customer_id=customer_id,
                    amount=case_data['transaction']['amount'],
                    currency=case_data['transaction']['currency'],
                    merchant_name=case_data['transaction']['merchantName'],
                    merchant_category=case_data['transaction']['merchantCategory'],
                    transaction_date=datetime.fromisoformat(case_data['transaction']['transactionDate'].replace('Z', '+00:00')),
                    location=case_data['transaction']['location'],
                    card_last4=case_data['transaction']['cardLast4'],
                    dispute_reason=case_data['disputeReason'],
                    dispute_description=case_data['disputeDescription'],
                    risk_score=case_data['riskScore'],
                    ai_recommendation=case_data['aiRecommendation'],
                    ai_confidence=case_data['aiConfidence'],
                    ai_analysis=case_data['aiAnalysis'],
                    status=case_data['status'],
                    priority=case_data['priority'],
                    created_at=datetime.fromisoformat(case_data['createdAt'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(case_data['updatedAt'].replace('Z', '+00:00'))
                )
                
                # Add custom fields for categorization (if not in existing model, we'll add them)
                if hasattr(dispute, 'category'):
                    dispute.category = case_data.get('category', 'OTHER')
                if hasattr(dispute, 'subcategory'):
                    dispute.subcategory = case_data.get('subcategory', 'OTHER')
                if hasattr(dispute, 'reason_code'):
                    dispute.reason_code = case_data.get('reason_code', 'UNKNOWN')
                if hasattr(dispute, 'card_network'):
                    dispute.card_network = case_data.get('card_network', 'unknown')
                
                db.session.add(dispute)
                
                # Commit every 50 records to avoid memory issues
                if i % 50 == 0:
                    db.session.commit()
                    print(f"Loaded {i} cases...")
                    
            except Exception as e:
                print(f"Error loading case {i}: {e}")
                db.session.rollback()
                continue
        
        # Final commit
        db.session.commit()
        
        # Verify data was loaded
        total_cases = DisputeCase.query.count()
        total_customers = Customer.query.count()
        
        print(f"\n✅ Successfully loaded:")
        print(f"   📊 {total_cases} dispute cases")
        print(f"   👥 {total_customers} unique customers")
        
        # Show breakdown by category
        print(f"\n📋 Case breakdown by status:")
        for status in ['pending', 'analyzing', 'review']:
            count = DisputeCase.query.filter_by(status=status).count()
            print(f"   {status.capitalize()}: {count} cases")
            
        print(f"\n🎯 Case breakdown by priority:")
        for priority in ['low', 'medium', 'high', 'critical']:
            count = DisputeCase.query.filter_by(priority=priority).count()
            print(f"   {priority.capitalize()}: {count} cases")
            
        print(f"\n💡 AI Recommendations:")
        for rec in ['approve', 'reject', 'review']:
            count = DisputeCase.query.filter_by(ai_recommendation=rec).count()
            print(f"   {rec.capitalize()}: {count} cases")
        
        return True

def extend_database_schema():
    """Add new columns to existing database for categorization"""
    print("Extending database schema for new categorization fields...")
    
    with app.app_context():
        try:
            # Check if we need to add new columns
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('dispute_case')]
            
            new_columns = []
            if 'category' not in columns:
                new_columns.append('category VARCHAR(50)')
            if 'subcategory' not in columns:
                new_columns.append('subcategory VARCHAR(50)')
            if 'reason_code' not in columns:
                new_columns.append('reason_code VARCHAR(10)')
            if 'card_network' not in columns:
                new_columns.append('card_network VARCHAR(20)')
                
            if new_columns:
                for column in new_columns:
                    db.engine.execute(f'ALTER TABLE dispute_case ADD COLUMN {column}')
                print(f"Added columns: {', '.join(new_columns)}")
            else:
                print("All required columns already exist.")
                
        except Exception as e:
            print(f"Schema extension completed (some columns may already exist): {e}")

if __name__ == "__main__":
    print("🚀 Loading chargeback demo data into SQLite database...")
    
    # Extend schema first
    extend_database_schema()
    
    # Load the data
    success = load_data_to_database()
    
    if success:
        print("\n🎉 Database loading completed successfully!")
        print("\n🔗 You can now start the Flask backend to see the data:")
        print("   python app.py")
    else:
        print("\n❌ Database loading failed!")
        sys.exit(1)

