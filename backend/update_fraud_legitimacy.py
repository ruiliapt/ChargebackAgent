#!/usr/bin/env python3
"""
Update 40% of Fraud & Unauthorized cases to have non-zero legitimacy tracking values.
This represents scenarios where:
- Account takeover fraud (compromised existing customer accounts)
- Card testing with small amounts before large fraud
- Friendly fraud (legitimate customer disputing their own purchases)
"""

import random
import sys
from app import app, db, DisputeCase

def update_fraud_legitimacy():
    """Update 40% of Fraud & Unauthorized cases with legitimacy tracking data"""
    
    with app.app_context():
        # Find all Fraud & Unauthorized cases
        fraud_cases = DisputeCase.query.filter_by(category='FRAUD_UNAUTHORIZED').all()
        
        print(f"Found {len(fraud_cases)} Fraud & Unauthorized cases")
        
        # Calculate 40% of cases to update
        cases_to_update = int(len(fraud_cases) * 0.4)
        
        print(f"Will update {cases_to_update} cases (40%) with legitimacy tracking data")
        
        # Randomly select 40% of cases to update
        random.seed(42)  # For reproducible results
        selected_cases = random.sample(fraud_cases, cases_to_update)
        
        print(f"\nUpdating {len(selected_cases)} fraud cases with legitimacy data...")
        
        updated_count = 0
        for case in selected_cases:
            # Generate different fraud patterns based on fraud type
            fraud_pattern = random.choices([
                'account_takeover',  # Compromised existing customer account
                'card_testing',      # Small test transactions before large fraud
                'friendly_fraud'     # Customer disputing their own legitimate purchases
            ], weights=[50, 30, 20])[0]
            
            if fraud_pattern == 'account_takeover':
                # Compromised account of existing customer - moderate history
                same_card_orders = random.randint(3, 15)
                same_address_orders = random.randint(2, 12)
                same_ip_orders = random.randint(1, 8)
                same_device_orders = random.randint(0, 6)
                
            elif fraud_pattern == 'card_testing':
                # Fraudster testing card with small amounts - minimal history
                same_card_orders = random.randint(1, 5)
                same_address_orders = random.randint(0, 2)
                same_ip_orders = random.randint(0, 3)
                same_device_orders = random.randint(0, 2)
                
            else:  # friendly_fraud
                # Legitimate customer committing friendly fraud - higher history
                same_card_orders = random.randint(5, 25)
                same_address_orders = random.randint(4, 20)
                same_ip_orders = random.randint(2, 15)
                same_device_orders = random.randint(1, 10)
            
            # Update the case
            case.same_card_success_orders = same_card_orders
            case.same_address_success_orders = same_address_orders
            case.same_ip_success_orders = same_ip_orders
            case.same_device_success_orders = same_device_orders
            
            updated_count += 1
            
            if updated_count % 5 == 0:
                print(f"  Updated {updated_count} cases...")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully updated {updated_count} fraud cases with legitimacy tracking data")
        
        # Verify the changes with detailed statistics
        print(f"\n📊 Updated Distribution Analysis:")
        
        all_fraud_cases = DisputeCase.query.filter_by(category='FRAUD_UNAUTHORIZED').all()
        
        # Extract all values for each field
        same_card_values = [c.same_card_success_orders or 0 for c in all_fraud_cases]
        same_address_values = [c.same_address_success_orders or 0 for c in all_fraud_cases]
        same_ip_values = [c.same_ip_success_orders or 0 for c in all_fraud_cases]
        same_device_values = [c.same_device_success_orders or 0 for c in all_fraud_cases]
        
        def analyze_field(values, field_name):
            print(f'\n🔍 {field_name}:')
            print(f'  Min: {min(values)}, Max: {max(values)}, Average: {sum(values)/len(values):.1f}')
            
            # Count distribution
            zero_count = sum(1 for v in values if v == 0)
            low_count = sum(1 for v in values if 1 <= v <= 5)
            medium_count = sum(1 for v in values if 6 <= v <= 15)
            high_count = sum(1 for v in values if v > 15)
            
            total = len(values)
            print(f'  Zero (0): {zero_count} ({zero_count/total*100:.1f}%)')
            print(f'  Low (1-5): {low_count} ({low_count/total*100:.1f}%)')
            print(f'  Medium (6-15): {medium_count} ({medium_count/total*100:.1f}%)')
            print(f'  High (16+): {high_count} ({high_count/total*100:.1f}%)')
            
            # Show some sample non-zero values
            non_zero_values = sorted([v for v in values if v > 0])
            if non_zero_values:
                print(f'  Sample non-zero values: {non_zero_values[:8]}')
        
        analyze_field(same_card_values, '# of Success Orders Paid From Same Card')
        analyze_field(same_address_values, '# of Success Orders Sharing Same Shipping Address')
        analyze_field(same_ip_values, '# of Success Orders Sharing Same IP')
        analyze_field(same_device_values, '# of Success Orders Sharing Same Device')
        
        # Overall analysis
        cases_with_any_links = [
            c for c in all_fraud_cases 
            if any([
                (c.same_card_success_orders or 0) > 0,
                (c.same_address_success_orders or 0) > 0,
                (c.same_ip_success_orders or 0) > 0,
                (c.same_device_success_orders or 0) > 0
            ])
        ]
        
        cases_with_no_links = len(all_fraud_cases) - len(cases_with_any_links)
        
        print(f'\n📈 Overall Summary:')
        print(f'  Cases with ANY legitimacy links: {len(cases_with_any_links)}/{len(all_fraud_cases)} ({len(cases_with_any_links)/len(all_fraud_cases)*100:.1f}%)')
        print(f'  Cases with NO legitimacy links: {cases_with_no_links}/{len(all_fraud_cases)} ({cases_with_no_links/len(all_fraud_cases)*100:.1f}%)')
        
        # Show sample cases
        print(f'\n🎯 Sample Updated Cases:')
        updated_samples = [c for c in all_fraud_cases if (c.same_card_success_orders or 0) > 0][:5]
        for case in updated_samples:
            print(f'  {case.case_number}: Card={case.same_card_success_orders or 0}, Address={case.same_address_success_orders or 0}, IP={case.same_ip_success_orders or 0}, Device={case.same_device_success_orders or 0}')
        
        print(f'\n🎯 Sample Zero-Link Cases (still 60%):')
        zero_samples = [c for c in all_fraud_cases if (c.same_card_success_orders or 0) == 0][:3]
        for case in zero_samples:
            print(f'  {case.case_number}: Card={case.same_card_success_orders or 0}, Address={case.same_address_success_orders or 0}, IP={case.same_ip_success_orders or 0}, Device={case.same_device_success_orders or 0}')
        
        print(f'\n🎯 Update completed successfully!')
        return True

if __name__ == "__main__":
    print("🔄 Updating 40% of Fraud & Unauthorized cases with legitimacy tracking data...")
    
    success = update_fraud_legitimacy()
    
    if success:
        print("\n🎉 Fraud legitimacy data update completed successfully!")
        print("\n💡 This creates a more realistic mix of fraud scenarios:")
        print("   - 60% pure fraud (stolen cards/identity theft)")
        print("   - 40% complex fraud (account takeover, card testing, friendly fraud)")
    else:
        print("\n❌ Fraud legitimacy data update failed!")
        sys.exit(1)
