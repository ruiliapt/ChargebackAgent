#!/usr/bin/env python3
"""
Update legitimacy tracking fields for Merchandise Issues and Processing Issues cases
70% of these cases should have at least one non-zero legitimacy tracking field
"""

import random
import sys
from app import app, db, DisputeCase

def update_legitimacy_data():
    """Update 70% of Merchandise Issues and Processing Issues cases with legitimacy tracking data"""
    
    with app.app_context():
        # Find all Merchandise Issues and Processing Issues cases
        target_categories = ['MERCHANT_MERCHANDISE', 'PROCESSING_ISSUES']
        cases = DisputeCase.query.filter(DisputeCase.category.in_(target_categories)).all()
        
        print(f"Found {len(cases)} cases in target categories:")
        
        # Count by category
        merchandise_cases = [c for c in cases if c.category == 'MERCHANT_MERCHANDISE']
        processing_cases = [c for c in cases if c.category == 'PROCESSING_ISSUES']
        
        print(f"  - Merchandise Issues: {len(merchandise_cases)} cases")
        print(f"  - Processing Issues: {len(processing_cases)} cases")
        
        # Calculate 70% of each category
        merchandise_to_update = int(len(merchandise_cases) * 0.7)
        processing_to_update = int(len(processing_cases) * 0.7)
        
        print(f"\nWill update legitimacy data for:")
        print(f"  - Merchandise Issues: {merchandise_to_update} cases (70%)")
        print(f"  - Processing Issues: {processing_to_update} cases (70%)")
        
        # Randomly select cases to update
        random.seed(42)  # For reproducible results
        merchandise_selected = random.sample(merchandise_cases, merchandise_to_update)
        processing_selected = random.sample(processing_cases, processing_to_update)
        
        all_selected = merchandise_selected + processing_selected
        
        print(f"\nUpdating {len(all_selected)} cases with legitimacy tracking data...")
        
        updated_count = 0
        for case in all_selected:
            # Generate realistic legitimacy tracking numbers
            # At least one field must be non-zero
            
            # Define different patterns based on case type - with higher values
            if case.category == 'MERCHANT_MERCHANDISE':
                # For merchandise issues, more likely to have shipping address and card matches
                same_card_orders = random.choice([0, 0, 0, random.randint(5, 35)])
                same_address_orders = random.choice([0, 0, random.randint(3, 25)])
                same_ip_orders = random.choice([0, 0, 0, random.randint(2, 18)])
                same_device_orders = random.choice([0, 0, 0, random.randint(1, 15)])
            else:  # PROCESSING_ISSUES
                # For processing issues, more likely to have card and IP matches
                same_card_orders = random.choice([0, 0, random.randint(8, 45)])
                same_address_orders = random.choice([0, 0, 0, random.randint(4, 22)])
                same_ip_orders = random.choice([0, random.randint(6, 30)])
                same_device_orders = random.choice([0, 0, random.randint(3, 20)])
            
            # Ensure at least one field is non-zero
            if all(x == 0 for x in [same_card_orders, same_address_orders, same_ip_orders, same_device_orders]):
                # Force at least one to be non-zero with higher values
                field_to_set = random.choice(['card', 'address', 'ip', 'device'])
                if field_to_set == 'card':
                    same_card_orders = random.randint(5, 25)
                elif field_to_set == 'address':
                    same_address_orders = random.randint(3, 18)
                elif field_to_set == 'ip':
                    same_ip_orders = random.randint(4, 20)
                else:  # device
                    same_device_orders = random.randint(2, 15)
            
            # Update the case
            case.same_card_success_orders = same_card_orders
            case.same_address_success_orders = same_address_orders
            case.same_ip_success_orders = same_ip_orders
            case.same_device_success_orders = same_device_orders
            
            # Also set some additional fields that might be missing
            if not hasattr(case, 'item_shipped') or case.item_shipped is None:
                case.item_shipped = random.choice(['Y', 'Y', 'N'])  # 66% shipped
            if not hasattr(case, 'item_delivered') or case.item_delivered is None:
                case.item_delivered = random.choice(['Y', 'Y', 'N']) if case.item_shipped == 'Y' else 'N'
            if not hasattr(case, 'digital_goods') or case.digital_goods is None:
                case.digital_goods = random.choice(['N', 'N', 'N', 'Y'])  # 25% digital
            
            updated_count += 1
            
            if updated_count % 20 == 0:
                print(f"  Updated {updated_count} cases...")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully updated {updated_count} cases with legitimacy tracking data")
        
        # Verify the changes
        print(f"\n📊 Verification - Cases with at least one non-zero legitimacy field:")
        
        for category in target_categories:
            cases_in_category = DisputeCase.query.filter_by(category=category).all()
            cases_with_links = [
                c for c in cases_in_category 
                if any([
                    (c.same_card_success_orders or 0) > 0,
                    (c.same_address_success_orders or 0) > 0,
                    (c.same_ip_success_orders or 0) > 0,
                    (c.same_device_success_orders or 0) > 0
                ])
            ]
            
            category_name = "Merchandise Issues" if category == "MERCHANT_MERCHANDISE" else "Processing Issues"
            percentage = (len(cases_with_links) / len(cases_in_category) * 100) if cases_in_category else 0
            
            print(f"  - {category_name}: {len(cases_with_links)}/{len(cases_in_category)} ({percentage:.1f}%)")
        
        print(f"\n🎯 Update completed successfully!")
        return True

if __name__ == "__main__":
    print("🔄 Updating legitimacy tracking data for Merchandise Issues and Processing Issues cases...")
    
    success = update_legitimacy_data()
    
    if success:
        print("\n🎉 Legitimacy data update completed successfully!")
        print("\n💡 The updated data will improve the AI analysis accuracy for these case types.")
    else:
        print("\n❌ Legitimacy data update failed!")
        sys.exit(1)
