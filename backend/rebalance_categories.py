#!/usr/bin/env python3
"""
Rebalance case categories to increase Fraud & Unauthorized cases and reduce others.
New target distribution:
- Fraud & Unauthorized: 50% (100 cases)
- Merchandise Issues: 30% (60 cases) 
- Processing Issues: 20% (40 cases)
"""

import random
import sys
from app import app, db, DisputeCase

def rebalance_categories():
    """Rebalance case categories by converting some cases to Fraud & Unauthorized"""
    
    with app.app_context():
        # Get current counts
        fraud_cases = DisputeCase.query.filter_by(category='FRAUD_UNAUTHORIZED').all()
        merchant_cases = DisputeCase.query.filter_by(category='MERCHANT_MERCHANDISE').all()
        processing_cases = DisputeCase.query.filter_by(category='PROCESSING_ISSUES').all()
        
        total_cases = len(fraud_cases) + len(merchant_cases) + len(processing_cases)
        
        print(f"Current Distribution ({total_cases} total cases):")
        print(f"  Fraud & Unauthorized: {len(fraud_cases)} ({len(fraud_cases)/total_cases*100:.1f}%)")
        print(f"  Merchandise Issues: {len(merchant_cases)} ({len(merchant_cases)/total_cases*100:.1f}%)")
        print(f"  Processing Issues: {len(processing_cases)} ({len(processing_cases)/total_cases*100:.1f}%)")
        
        # Target distribution
        target_fraud = 100      # 50%
        target_merchant = 60    # 30%
        target_processing = 40  # 20%
        
        print(f"\nTarget Distribution:")
        print(f"  Fraud & Unauthorized: {target_fraud} (50%)")
        print(f"  Merchandise Issues: {target_merchant} (30%)")
        print(f"  Processing Issues: {target_processing} (20%)")
        
        # Calculate how many cases need to be converted
        fraud_needed = target_fraud - len(fraud_cases)
        merchant_excess = len(merchant_cases) - target_merchant
        processing_excess = len(processing_cases) - target_processing
        
        print(f"\nChanges needed:")
        print(f"  Fraud cases to add: +{fraud_needed}")
        print(f"  Merchant cases to reduce: -{merchant_excess}")
        print(f"  Processing cases to reduce: -{processing_excess}")
        
        if fraud_needed <= 0:
            print("No rebalancing needed - already have enough fraud cases!")
            return True
        
        # Select cases to convert to fraud
        cases_to_convert = []
        
        # Convert some merchant cases
        if merchant_excess > 0:
            merchant_to_convert = min(merchant_excess, fraud_needed)
            random.seed(42)  # For reproducible results
            selected_merchant = random.sample(merchant_cases, merchant_to_convert)
            cases_to_convert.extend(selected_merchant)
            fraud_needed -= merchant_to_convert
            print(f"  Converting {merchant_to_convert} Merchandise cases to Fraud")
        
        # Convert some processing cases if we still need more fraud cases
        if fraud_needed > 0 and processing_excess > 0:
            processing_to_convert = min(processing_excess, fraud_needed)
            selected_processing = random.sample(processing_cases, processing_to_convert)
            cases_to_convert.extend(selected_processing)
            fraud_needed -= processing_to_convert
            print(f"  Converting {processing_to_convert} Processing cases to Fraud")
        
        # If we still need more cases, convert additional ones
        if fraud_needed > 0:
            remaining_merchant = [c for c in merchant_cases if c not in cases_to_convert]
            remaining_processing = [c for c in processing_cases if c not in cases_to_convert]
            additional_candidates = remaining_merchant + remaining_processing
            
            if len(additional_candidates) >= fraud_needed:
                additional_converts = random.sample(additional_candidates, fraud_needed)
                cases_to_convert.extend(additional_converts)
                print(f"  Converting {fraud_needed} additional cases to Fraud")
        
        print(f"\nConverting {len(cases_to_convert)} cases to Fraud & Unauthorized...")
        
        # Convert selected cases to fraud
        fraud_subcategories = ['1A_Card_Fraud', '1B_Identity_Theft', '1C_Account_Takeover', '1D_Friendly_Fraud']
        fraud_reason_codes = ['10.4', '10.5', '4837', '4863', '4540', '4541']
        
        converted_count = 0
        for case in cases_to_convert:
            old_category = case.category
            
            # Update category and related fields
            case.category = 'FRAUD_UNAUTHORIZED'
            case.subcategory = random.choice(fraud_subcategories)
            case.reason_code = random.choice(fraud_reason_codes)
            
            # Reset legitimacy fields for pure fraud cases (60% should have zeros)
            if random.random() < 0.6:  # 60% pure fraud
                case.same_card_success_orders = 0
                case.same_address_success_orders = 0
                case.same_ip_success_orders = 0
                case.same_device_success_orders = 0
            else:  # 40% complex fraud (account takeover, etc.)
                # Keep some legitimacy history for complex fraud scenarios
                if not case.same_card_success_orders:
                    case.same_card_success_orders = random.randint(1, 15)
                if not case.same_address_success_orders:
                    case.same_address_success_orders = random.randint(0, 10)
                if not case.same_ip_success_orders:
                    case.same_ip_success_orders = random.randint(0, 8)
                if not case.same_device_success_orders:
                    case.same_device_success_orders = random.randint(0, 6)
            
            # Update dispute reason
            case.dispute_reason = f"Unauthorized Transaction - {case.subcategory.replace('_', ' ')}"
            
            # Adjust risk score for fraud (typically higher)
            case.risk_score = random.randint(70, 100)
            case.ai_recommendation = 'reject' if case.risk_score > 60 else 'review'
            
            converted_count += 1
            
            if converted_count % 10 == 0:
                print(f"  Converted {converted_count} cases...")
        
        # Commit all changes
        db.session.commit()
        
        print(f"\n✅ Successfully converted {converted_count} cases to Fraud & Unauthorized")
        
        # Verify final distribution
        final_fraud = DisputeCase.query.filter_by(category='FRAUD_UNAUTHORIZED').count()
        final_merchant = DisputeCase.query.filter_by(category='MERCHANT_MERCHANDISE').count()
        final_processing = DisputeCase.query.filter_by(category='PROCESSING_ISSUES').count()
        final_total = final_fraud + final_merchant + final_processing
        
        print(f"\n📊 Final Distribution ({final_total} total cases):")
        print(f"  Fraud & Unauthorized: {final_fraud} ({final_fraud/final_total*100:.1f}%)")
        print(f"  Merchandise Issues: {final_merchant} ({final_merchant/final_total*100:.1f}%)")
        print(f"  Processing Issues: {final_processing} ({final_processing/final_total*100:.1f}%)")
        
        print(f"\n🎯 Rebalancing completed successfully!")
        return True

if __name__ == "__main__":
    print("🔄 Rebalancing case categories to increase Fraud & Unauthorized cases...")
    
    success = rebalance_categories()
    
    if success:
        print("\n🎉 Category rebalancing completed successfully!")
        print("\n💡 The new distribution better reflects real-world chargeback patterns")
        print("   with more fraud cases and fewer merchant/processing disputes.")
    else:
        print("\n❌ Category rebalancing failed!")
        sys.exit(1)
