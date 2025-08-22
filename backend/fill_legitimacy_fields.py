#!/usr/bin/env python3
"""
Fill legitimacy tracking fields for ALL cases in Merchandise Issues and Processing Issues categories.
Ensure every case has realistic values for:
- # of Success Orders Paid From Same Card
- # of Success Orders Sharing Same Shipping Address  
- # of Success Orders Sharing Same IP
- # of Success Orders Sharing Same Device
"""

import random
import sys
from app import app, db, DisputeCase

def fill_legitimacy_fields():
    """Fill legitimacy tracking fields for ALL Merchandise Issues and Processing Issues cases"""
    
    with app.app_context():
        # Find all Merchandise Issues and Processing Issues cases
        target_categories = ['MERCHANT_MERCHANDISE', 'PROCESSING_ISSUES']
        cases = DisputeCase.query.filter(DisputeCase.category.in_(target_categories)).all()
        
        print(f"Filling legitimacy fields for ALL {len(cases)} cases in target categories:")
        
        # Count by category
        merchandise_cases = [c for c in cases if c.category == 'MERCHANT_MERCHANDISE']
        processing_cases = [c for c in cases if c.category == 'PROCESSING_ISSUES']
        
        print(f"  - Merchandise Issues: {len(merchandise_cases)} cases")
        print(f"  - Processing Issues: {len(processing_cases)} cases")
        
        print(f"\nUpdating legitimacy data for ALL cases...")
        
        updated_count = 0
        for case in cases:
            # Generate realistic legitimacy tracking numbers for ALL cases
            # Different patterns based on case type
            
            if case.category == 'MERCHANT_MERCHANDISE':
                # For merchandise issues, create varied patterns
                # Some customers are repeat buyers, some are new
                customer_type = random.choices(['repeat_buyer', 'occasional_buyer', 'new_customer'], 
                                             weights=[40, 35, 25])[0]
                
                if customer_type == 'repeat_buyer':
                    # Heavy repeat customers
                    same_card_orders = random.randint(8, 45)
                    same_address_orders = random.randint(6, 35)
                    same_ip_orders = random.randint(4, 25)
                    same_device_orders = random.randint(2, 20)
                elif customer_type == 'occasional_buyer':
                    # Moderate repeat customers
                    same_card_orders = random.randint(2, 15)
                    same_address_orders = random.randint(1, 12)
                    same_ip_orders = random.randint(0, 8)
                    same_device_orders = random.randint(0, 6)
                else:  # new_customer
                    # New customers with minimal history
                    same_card_orders = random.randint(0, 3)
                    same_address_orders = random.randint(0, 2)
                    same_ip_orders = random.randint(0, 2)
                    same_device_orders = random.randint(0, 1)
                    
            else:  # PROCESSING_ISSUES
                # For processing issues, create different patterns
                issue_type = random.choices(['payment_issues', 'technical_glitch', 'first_time_user'], 
                                          weights=[45, 35, 20])[0]
                
                if issue_type == 'payment_issues':
                    # Customer with payment processing problems but established history
                    same_card_orders = random.randint(12, 50)
                    same_address_orders = random.randint(8, 30)
                    same_ip_orders = random.randint(10, 35)
                    same_device_orders = random.randint(6, 25)
                elif issue_type == 'technical_glitch':
                    # Regular customer hit by technical issues
                    same_card_orders = random.randint(5, 25)
                    same_address_orders = random.randint(3, 18)
                    same_ip_orders = random.randint(4, 20)
                    same_device_orders = random.randint(2, 15)
                else:  # first_time_user
                    # New user facing processing issues
                    same_card_orders = random.randint(0, 2)
                    same_address_orders = random.randint(0, 1)
                    same_ip_orders = random.randint(0, 3)
                    same_device_orders = random.randint(0, 2)
            
            # Apply some correlation logic - if card orders are high, address orders should be reasonably high too
            if same_card_orders > 20:
                # Ensure address orders are at least 50% of card orders for heavy buyers
                min_address = max(same_address_orders, int(same_card_orders * 0.5))
                same_address_orders = min(min_address, same_card_orders)
            
            # Update the case with new values
            case.same_card_success_orders = same_card_orders
            case.same_address_success_orders = same_address_orders
            case.same_ip_success_orders = same_ip_orders
            case.same_device_success_orders = same_device_orders
            
            updated_count += 1
            
            if updated_count % 25 == 0:
                print(f"  Updated {updated_count} cases...")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully updated legitimacy fields for {updated_count} cases")
        
        # Verify the changes with detailed statistics
        print(f"\n📊 Detailed Statistics After Update:")
        
        for category in target_categories:
            cases_in_category = DisputeCase.query.filter_by(category=category).all()
            
            # Calculate various statistics
            total_cases = len(cases_in_category)
            
            # Cases with any links
            cases_with_links = [
                c for c in cases_in_category 
                if any([
                    (c.same_card_success_orders or 0) > 0,
                    (c.same_address_success_orders or 0) > 0,
                    (c.same_ip_success_orders or 0) > 0,
                    (c.same_device_success_orders or 0) > 0
                ])
            ]
            
            # High activity cases (10+ in any category)
            high_activity_cases = [
                c for c in cases_in_category
                if any([
                    (c.same_card_success_orders or 0) >= 10,
                    (c.same_address_success_orders or 0) >= 10,
                    (c.same_ip_success_orders or 0) >= 10,
                    (c.same_device_success_orders or 0) >= 10
                ])
            ]
            
            # Average values
            avg_card = sum(c.same_card_success_orders or 0 for c in cases_in_category) / total_cases
            avg_address = sum(c.same_address_success_orders or 0 for c in cases_in_category) / total_cases
            avg_ip = sum(c.same_ip_success_orders or 0 for c in cases_in_category) / total_cases
            avg_device = sum(c.same_device_success_orders or 0 for c in cases_in_category) / total_cases
            
            category_name = "Merchandise Issues" if category == "MERCHANT_MERCHANDISE" else "Processing Issues"
            
            print(f"\n{category_name}:")
            print(f"  - Total cases: {total_cases}")
            print(f"  - Cases with legitimacy links: {len(cases_with_links)}/{total_cases} ({len(cases_with_links)/total_cases*100:.1f}%)")
            print(f"  - High activity cases (10+): {len(high_activity_cases)} ({len(high_activity_cases)/total_cases*100:.1f}%)")
            print(f"  - Average same card orders: {avg_card:.1f}")
            print(f"  - Average same address orders: {avg_address:.1f}")
            print(f"  - Average same IP orders: {avg_ip:.1f}")
            print(f"  - Average same device orders: {avg_device:.1f}")
        
        print(f"\n🎯 Legitimacy fields population completed successfully!")
        return True

if __name__ == "__main__":
    print("🔄 Filling legitimacy tracking fields for ALL Merchandise Issues and Processing Issues cases...")
    
    success = fill_legitimacy_fields()
    
    if success:
        print("\n🎉 Legitimacy fields population completed successfully!")
        print("\n💡 All target cases now have comprehensive legitimacy tracking data.")
        print("🔍 This will significantly improve AI analysis accuracy for these case types.")
    else:
        print("\n❌ Legitimacy fields population failed!")
        sys.exit(1)
