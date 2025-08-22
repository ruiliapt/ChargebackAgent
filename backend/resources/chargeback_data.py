"""
Resources: Data access layer for chargeback dispute management
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class DisputeResource:
    """Resource model for dispute cases"""
    id: str
    case_number: str
    category: str
    subcategory: str
    reason_code: str
    card_network: str
    amount: float
    merchant_name: str
    merchant_category: str
    customer_id: str
    dispute_reason: str
    dispute_description: str
    risk_score: int
    ai_recommendation: str
    ai_confidence: int
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime

@dataclass
class CustomerResource:
    """Resource model for customer data"""
    id: str
    name: str
    email: str
    credit_score: int
    account_type: str
    previous_disputes: int
    customer_since: datetime

@dataclass
class TransactionResource:
    """Resource model for transaction data"""
    id: str
    amount: float
    currency: str
    merchant_name: str
    merchant_category: str
    transaction_date: datetime
    location: str
    card_last4: str

class ChargebackDataRepository:
    """Data access layer for chargeback resources"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    def get_dispute_by_id(self, dispute_id: str) -> Optional[DisputeResource]:
        """Retrieve a specific dispute case"""
        from app import DisputeCase
        dispute = DisputeCase.query.get(dispute_id)
        if not dispute:
            return None
            
        return DisputeResource(
            id=dispute.id,
            case_number=dispute.case_number,
            category=dispute.category,
            subcategory=dispute.subcategory,
            reason_code=dispute.reason_code,
            card_network=dispute.card_network,
            amount=dispute.amount,
            merchant_name=dispute.merchant_name,
            merchant_category=dispute.merchant_category,
            customer_id=dispute.customer_id,
            dispute_reason=dispute.dispute_reason,
            dispute_description=dispute.dispute_description,
            risk_score=dispute.risk_score,
            ai_recommendation=dispute.ai_recommendation,
            ai_confidence=dispute.ai_confidence,
            status=dispute.status,
            priority=dispute.priority,
            created_at=dispute.created_at,
            updated_at=dispute.updated_at
        )
    
    def get_disputes_by_category(self, category: str) -> List[DisputeResource]:
        """Retrieve disputes by main category"""
        from app import DisputeCase
        disputes = DisputeCase.query.filter_by(category=category).all()
        return [self._to_resource(d) for d in disputes]
    
    def get_disputes_by_subcategory(self, subcategory: str) -> List[DisputeResource]:
        """Retrieve disputes by subcategory"""
        from app import DisputeCase
        disputes = DisputeCase.query.filter_by(subcategory=subcategory).all()
        return [self._to_resource(d) for d in disputes]
    
    def get_customer_data(self, customer_id: str) -> Optional[CustomerResource]:
        """Retrieve customer information"""
        from app import Customer
        customer = Customer.query.get(customer_id)
        if not customer:
            return None
            
        return CustomerResource(
            id=customer.id,
            name=customer.name,
            email=customer.email,
            credit_score=customer.credit_score,
            account_type=customer.account_type,
            previous_disputes=customer.previous_disputes,
            customer_since=customer.customer_since
        )
    
    def get_fraud_indicators(self, dispute_id: str) -> Dict:
        """Get fraud-related data for analysis"""
        dispute = self.get_dispute_by_id(dispute_id)
        customer = self.get_customer_data(dispute.customer_id)
        
        return {
            'transaction_amount': dispute.amount,
            'merchant_category': dispute.merchant_category,
            'customer_credit_score': customer.credit_score if customer else 650,
            'previous_disputes': customer.previous_disputes if customer else 0,
            'reason_code': dispute.reason_code,
            'card_network': dispute.card_network,
            'transaction_velocity': self._calculate_velocity(dispute.customer_id),
            'geographic_risk': self._assess_geographic_risk(dispute_id)
        }
    
    def _to_resource(self, dispute) -> DisputeResource:
        """Convert database model to resource"""
        return DisputeResource(
            id=dispute.id,
            case_number=dispute.case_number,
            category=dispute.category or 'UNKNOWN',
            subcategory=dispute.subcategory or 'UNKNOWN',
            reason_code=dispute.reason_code or 'UNKNOWN',
            card_network=dispute.card_network or 'unknown',
            amount=dispute.amount,
            merchant_name=dispute.merchant_name,
            merchant_category=dispute.merchant_category,
            customer_id=dispute.customer_id,
            dispute_reason=dispute.dispute_reason,
            dispute_description=dispute.dispute_description,
            risk_score=dispute.risk_score,
            ai_recommendation=dispute.ai_recommendation,
            ai_confidence=dispute.ai_confidence,
            status=dispute.status,
            priority=dispute.priority,
            created_at=dispute.created_at,
            updated_at=dispute.updated_at
        )
    
    def _calculate_velocity(self, customer_id: str) -> str:
        """Calculate transaction velocity for fraud detection"""
        # Simplified implementation
        return "normal"
    
    def _assess_geographic_risk(self, dispute_id: str) -> str:
        """Assess geographic risk factors"""
        # Simplified implementation
        return "low"

# Industry-specific knowledge resources
CHARGEBACK_REASON_CODES = {
    'visa': {
        '10.1': 'EMV Liability Shift Counterfeit Fraud',
        '10.4': 'Other Fraud: Card-Absent Environment',
        '11.3': 'No Authorization',
        '12.6': 'Duplicate Processing',
        '13.1': 'Merchandise/Services Not Received',
        '13.2': 'Cancelled Recurring Transaction'
    },
    'mastercard': {
        '4837': 'No Cardholder Authorization',
        '4808': 'Authorization-Related Chargeback',
        '4834': 'Duplicate Processing',
        '4853': 'Cardholder Dispute',
        '4855': 'Goods/Services Not Provided'
    },
    'amex': {
        'F24': 'No Cardmember Authorization',
        'F29': 'Card Not Present',
        'C08': 'Goods/Services Not Received',
        'C28': 'Cancelled Recurring Billing'
    }
}

MERCHANT_RISK_CATEGORIES = {
    'high_risk': ['Luxury Goods', 'Online Services', 'Travel Services', 'Digital Goods'],
    'medium_risk': ['Electronics', 'Clothing', 'Home & Garden'],
    'low_risk': ['Grocery', 'Gas Stations', 'Utilities']
}

CATEGORY_THRESHOLDS = {
    'FRAUD_UNAUTHORIZED': {
        'auto_approve_threshold': 30,
        'auto_reject_threshold': 70,
        'investigation_required': 50
    },
    'PROCESSING_ISSUES': {
        'auto_approve_threshold': 40,
        'auto_reject_threshold': 80,
        'investigation_required': 60
    },
    'MERCHANT_MERCHANDISE': {
        'auto_approve_threshold': 35,
        'auto_reject_threshold': 75,
        'investigation_required': 55
    }
}

