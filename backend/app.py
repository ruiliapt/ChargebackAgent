from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import json
import random
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chargeback_agent.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Data models
class DisputeCase(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    case_number = db.Column(db.String(20), unique=True, nullable=False)
    transaction_id = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    merchant_name = db.Column(db.String(200), nullable=False)
    merchant_category = db.Column(db.String(100))
    transaction_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    card_last4 = db.Column(db.String(4))
    dispute_reason = db.Column(db.String(200), nullable=False)
    dispute_description = db.Column(db.Text)
    risk_score = db.Column(db.Integer, default=0)
    ai_recommendation = db.Column(db.String(20))  # approve, reject, review
    ai_confidence = db.Column(db.Integer, default=0)
    ai_analysis = db.Column(db.Text)
    human_decision = db.Column(db.String(20))  # approve, reject
    status = db.Column(db.String(20), default='pending')  # pending, analyzing, review, completed
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    category = db.Column(db.String(50))  # FRAUD_UNAUTHORIZED, PROCESSING_ISSUES, MERCHANT_MERCHANDISE
    subcategory = db.Column(db.String(50))  # 1A_Card_Fraud, 2B_Technical_Processing, etc.
    reason_code = db.Column(db.String(10))  # Visa/MC/Amex reason codes
    card_network = db.Column(db.String(20))  # visa, mastercard, amex
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # New transaction-related fields
    items = db.Column(db.String(200))
    digital_goods = db.Column(db.String(1))
    login_method = db.Column(db.String(50))
    item_shipped = db.Column(db.String(1))
    item_shipped_date = db.Column(db.DateTime)
    item_delivered = db.Column(db.String(1))
    item_delivered_date = db.Column(db.DateTime)
    same_card_success_orders = db.Column(db.Integer)
    same_address_success_orders = db.Column(db.Integer)
    same_ip_success_orders = db.Column(db.Integer)
    same_device_success_orders = db.Column(db.Integer)
    checkout_ip = db.Column(db.String(50))
    checkout_device = db.Column(db.String(100))
    card_issuer = db.Column(db.String(100))
    analyst_feedback = db.Column(db.Text)

class Customer(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    account_type = db.Column(db.String(50))
    credit_score = db.Column(db.Integer)
    customer_since = db.Column(db.DateTime)
    previous_disputes = db.Column(db.Integer, default=0)
    
    # New customer analytics fields
    dispute_customer_won = db.Column(db.Integer)
    total_purchase_amount = db.Column(db.Float)
    dispute_percentage = db.Column(db.Float)
    linked_customers_count = db.Column(db.Integer)
    linked_customers_dispute_rate = db.Column(db.Float)
    linked_by_device = db.Column(db.Integer)
    linked_by_ip = db.Column(db.Integer)
    linked_by_card = db.Column(db.Integer)
    linked_by_address = db.Column(db.Integer)

# AI Analysis Engine
class ChargebackAnalysisEngine:
    def __init__(self):
        self.risk_factors = {
            'amount_weight': 0.10,                  # 10% - Transaction amount factor
            'customer_history_weight': 0.10,        # 10% - Customer history factor
            'merchant_risk_weight': 0.05,           # 5% - Merchant risk factor
            'dispute_reason_weight': 0.05,          # 5% - Dispute reason factor
            'evidence_weight': 0.10,                # 10% - Evidence completeness factor
            'transaction_legitimacy_weight': 0.40,  # 40% - Transaction legitimacy (PRIMARY FACTOR)
            'abuse_patterns_weight': 0.20           # 20% - Abuse patterns (SECONDARY FACTOR)
        }
    
    def calculate_risk_score(self, dispute_data, customer_data):
        """Calculate risk score with abusive chargeback detection"""
        score = 0
        
        # Transaction amount factor (10%)
        amount_score = self._calculate_amount_risk(dispute_data['amount'])
        score += amount_score * self.risk_factors['amount_weight']
        
        # Customer history factor (10%)
        customer_score = self._calculate_customer_risk(customer_data)
        score += customer_score * self.risk_factors['customer_history_weight']
        
        # Merchant risk factor (5%)
        merchant_score = self._calculate_merchant_risk(dispute_data['merchant_category'])
        score += merchant_score * self.risk_factors['merchant_risk_weight']
        
        # Dispute reason factor (5%)
        reason_score = self._calculate_reason_risk(dispute_data['dispute_reason'])
        score += reason_score * self.risk_factors['dispute_reason_weight']
        
        # Evidence completeness factor (10%)
        evidence_score = self._calculate_evidence_risk(dispute_data.get('evidence', []))
        score += evidence_score * self.risk_factors['evidence_weight']
        
        # NEW: Transaction legitimacy factor (40%) - legitimate customer patterns
        legitimacy_score = self._calculate_transaction_legitimacy(dispute_data)
        score += legitimacy_score * self.risk_factors['transaction_legitimacy_weight']
        
        # NEW: Abusive chargeback patterns factor (20%) - abusive behavior detection
        abuse_score = self._calculate_abuse_patterns(dispute_data, customer_data)
        score += abuse_score * self.risk_factors['abuse_patterns_weight']
        
        return min(100, max(0, int(score)))
    
    def _calculate_amount_risk(self, amount):
        """Calculate risk based on amount"""
        if amount < 100:
            return 10
        elif amount < 500:
            return 25
        elif amount < 2000:
            return 50
        else:
            return 80
    
    def _calculate_customer_risk(self, customer_data):
        """Calculate risk based on customer history"""
        score = 0
        
        # Credit score
        credit_score = customer_data.get('credit_score', 650)
        if credit_score > 750:
            score += 10
        elif credit_score > 650:
            score += 30
        else:
            score += 70
        
        # Historical dispute count
        previous_disputes = customer_data.get('previous_disputes', 0)
        score += min(30, previous_disputes * 10)
        
        return score
    
    def _calculate_merchant_risk(self, category):
        """Calculate risk based on merchant category"""
        high_risk_categories = ['Luxury Goods', 'Online Services', 'Travel Services']
        medium_risk_categories = ['Electronics', 'Subscription Service']
        
        if category in high_risk_categories:
            return 60
        elif category in medium_risk_categories:
            return 35
        else:
            return 20
    
    def _calculate_reason_risk(self, reason):
        """Calculate risk based on dispute reason"""
        high_risk_reasons = ['Fraudulent Transaction', 'Identity Theft']
        medium_risk_reasons = ['Unauthorized Transaction', 'Duplicate Charge']
        
        if reason in high_risk_reasons:
            return 80
        elif reason in medium_risk_reasons:
            return 50
        else:
            return 30
    
    def _calculate_evidence_risk(self, evidence):
        """Calculate risk based on evidence completeness"""
        if len(evidence) == 0:
            return 80
        elif len(evidence) == 1:
            return 50
        else:
            return 20
    
    def _calculate_transaction_legitimacy(self, dispute_data):
        """Calculate legitimacy score based on previous successful transaction patterns
        CATEGORY-AWARE LOGIC:
        - FRAUD_UNAUTHORIZED: Higher links = Higher score (likely abusive chargeback)
        - MERCHANT_MERCHANDISE/PROCESSING_ISSUES: Higher links = Lower score (loyal customer)
        """
        # Get transaction linking data
        same_card_orders = dispute_data.get('same_card_success_orders', 0)
        same_address_orders = dispute_data.get('same_address_success_orders', 0)
        same_ip_orders = dispute_data.get('same_ip_success_orders', 0)
        same_device_orders = dispute_data.get('same_device_success_orders', 0)
        category = dispute_data.get('category', 'UNKNOWN')
        
        # Calculate total linked orders
        total_linked_orders = same_card_orders + same_address_orders + same_ip_orders + same_device_orders
        has_any_links = total_linked_orders > 0
        
        # Additional context factors
        item_shipped = dispute_data.get('item_shipped', 'N')
        item_delivered = dispute_data.get('item_delivered', 'N')
        digital_goods = dispute_data.get('digital_goods', 'N')
        
        if category == 'FRAUD_UNAUTHORIZED':
            # FRAUD LOGIC: Links indicate abusive chargeback (stolen account with history)
            if not has_any_links:
                return 10  # Pure fraud - stolen card/identity theft
            
            # Base score of 80 when ANY links exist
            legitimacy_score = 80
            
            # More links = higher score (more suspicious for fraud)
            if total_linked_orders >= 20:
                legitimacy_score += 15  # Very suspicious (95 total)
            elif total_linked_orders >= 10:
                legitimacy_score += 10  # High suspicion (90 total)
            elif total_linked_orders >= 5:
                legitimacy_score += 5   # Moderate suspicion (85 total)
            
            # Context factors for fraud
            if digital_goods == 'Y':
                legitimacy_score += 5
            elif item_delivered == 'Y':
                legitimacy_score += 10
            elif item_shipped == 'Y':
                legitimacy_score += 5
            
            return min(100, legitimacy_score)
        
        elif category in ['MERCHANT_MERCHANDISE', 'PROCESSING_ISSUES']:
            # LOYAL CUSTOMER LOGIC: More links = Lower score (legitimate loyal customer)
            if not has_any_links:
                # No history - could be new customer or fraud
                return 70  # Medium-high risk for new customers
            
            # Start with high score, reduce based on loyalty indicators
            legitimacy_score = 90
            
            # More links = lower score (loyal customer)
            if total_linked_orders >= 30:
                legitimacy_score -= 40  # Very loyal customer (50 total)
            elif total_linked_orders >= 20:
                legitimacy_score -= 30  # Loyal customer (60 total)
            elif total_linked_orders >= 10:
                legitimacy_score -= 20  # Regular customer (70 total)
            elif total_linked_orders >= 5:
                legitimacy_score -= 10  # Occasional customer (80 total)
            # For 1-4 linked orders, stay at 90 (still somewhat suspicious)
            
            # Context factors for merchandise/processing
            if item_delivered == 'Y':
                legitimacy_score -= 10  # Delivered item supports customer claim
            elif item_shipped == 'Y':
                legitimacy_score -= 5   # Shipped item shows merchant compliance
            
            if digital_goods == 'Y':
                legitimacy_score += 5   # Digital goods harder to verify
            
            return max(10, legitimacy_score)  # Minimum score of 10
        
        else:
            # Unknown category - use moderate approach
            return 50
    
    def _calculate_abuse_patterns(self, dispute_data, customer_data):
        """Calculate risk based on abusive chargeback patterns
        Higher scores indicate more abusive behavior
        """
        abuse_score = 0
        
        # Customer dispute rate analysis
        dispute_percentage = customer_data.get('dispute_percentage', 0)
        if dispute_percentage >= 10:  # >10% dispute rate is very high
            abuse_score += 80
        elif dispute_percentage >= 5:  # 5-10% is high
            abuse_score += 60
        elif dispute_percentage >= 2:  # 2-5% is concerning
            abuse_score += 35
        elif dispute_percentage >= 1:  # 1-2% is elevated
            abuse_score += 20
        else:
            abuse_score += 5  # <1% is normal
        
        # Customer dispute win rate (customers who win too many disputes are suspicious)
        dispute_customer_won = customer_data.get('dispute_customer_won', 0)
        previous_disputes = customer_data.get('previous_disputes', 0)
        
        if previous_disputes > 0:
            win_rate = (dispute_customer_won / previous_disputes) * 100
            if win_rate >= 80:  # Winning >80% of disputes is suspicious
                abuse_score += 70
            elif win_rate >= 60:  # 60-80% win rate
                abuse_score += 45
            elif win_rate >= 40:  # 40-60% win rate
                abuse_score += 25
            else:
                abuse_score += 10  # <40% win rate is normal
        
        # Linked customers analysis (fraud rings)
        linked_customers_count = customer_data.get('linked_customers_count', 0)
        linked_customers_dispute_rate = customer_data.get('linked_customers_dispute_rate', 0)
        
        if linked_customers_count > 0:
            if linked_customers_dispute_rate >= 8:  # Linked customers with high dispute rate
                abuse_score += 60  # Likely fraud ring
            elif linked_customers_dispute_rate >= 4:
                abuse_score += 35  # Concerning network
            elif linked_customers_dispute_rate >= 2:
                abuse_score += 20  # Elevated network risk
            else:
                abuse_score += 5   # Normal linked customer activity
        
        # Multiple linking methods (suspicious if linked by many different methods)
        linked_by_device = customer_data.get('linked_by_device', 0)
        linked_by_ip = customer_data.get('linked_by_ip', 0)
        linked_by_card = customer_data.get('linked_by_card', 0)
        linked_by_address = customer_data.get('linked_by_address', 0)
        
        linking_methods = sum([1 for x in [linked_by_device, linked_by_ip, linked_by_card, linked_by_address] if x > 0])
        if linking_methods >= 4:  # Linked by all methods - very suspicious
            abuse_score += 50
        elif linking_methods >= 3:  # Linked by 3 methods
            abuse_score += 30
        elif linking_methods >= 2:  # Linked by 2 methods
            abuse_score += 15
        # 1 or 0 linking methods is normal
        
        # Total purchase amount vs dispute amount (frequent small disputes on large purchase history)
        total_purchase = customer_data.get('total_purchase_amount', 0)
        current_dispute_amount = dispute_data.get('amount', 0)
        
        if total_purchase > 0:
            dispute_ratio = (current_dispute_amount / total_purchase) * 100
            if dispute_ratio < 1 and previous_disputes > 5:  # Many small disputes relative to total spending
                abuse_score += 30  # Potential abuse pattern
        
        # Average the abuse indicators (divide by 5 main factors)
        return min(100, int(abuse_score / 5))
    
    def generate_recommendation(self, risk_score):
        """Generate AI recommendation with adjusted thresholds for new weight distribution"""
        if risk_score < 40:
            return 'approve', 85 + random.randint(0, 10)
        elif risk_score < 60:
            return 'review', 70 + random.randint(0, 15)
        else:
            return 'reject', 60 + random.randint(0, 20)
    
    def generate_analysis(self, dispute_data, customer_data, risk_score, recommendation):
        """Generate analysis report"""
        analysis_templates = {
            'approve': "After AI analysis, this dispute case has low risk. Customer has good credit record and reasonable dispute reason. Recommend approving refund.",
            'reject': "After AI analysis, this dispute case has high risk. Recommend further investigation or rejecting the refund request.",
            'review': "This case requires manual review. AI analysis found some risk factors. Recommend detailed investigation before making a decision."
        }
        
        base_analysis = analysis_templates.get(recommendation, "")
        
        # Add specific analysis details
        details = []
        if customer_data.get('credit_score', 0) > 700:
            details.append("Customer has excellent credit score")
        if customer_data.get('previous_disputes', 0) == 0:
            details.append("No historical dispute records")
        if dispute_data['amount'] > 2000:
            details.append("Large transaction requires special attention")
        
        if details:
            base_analysis += " Key factors include: " + ", ".join(details) + "."
        
        return base_analysis

# Initialize analysis engine
analysis_engine = ChargebackAnalysisEngine()

# API Routes
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/disputes', methods=['GET'])
def get_disputes():
    """Get all dispute cases"""
    disputes = DisputeCase.query.all()
    result = []
    
    for dispute in disputes:
        customer = Customer.query.get(dispute.customer_id)
        dispute_dict = {
            'id': dispute.id,
            'caseNumber': dispute.case_number,
            'transaction': {
                'id': dispute.transaction_id,
                'amount': dispute.amount,
                'currency': dispute.currency,
                'merchantName': dispute.merchant_name,
                'merchantCategory': dispute.merchant_category,
                'transactionDate': dispute.transaction_date.isoformat(),
                'location': dispute.location,
                'cardLast4': dispute.card_last4,
                # New transaction fields
                'items': dispute.items or 'N/A',
                'digitalGoods': dispute.digital_goods or 'N/A',
                'loginMethod': dispute.login_method or 'N/A',
                'itemShipped': dispute.item_shipped or 'N/A',
                'itemShippedDate': dispute.item_shipped_date.isoformat() if dispute.item_shipped_date else 'N/A',
                'itemDelivered': dispute.item_delivered or 'N/A',
                'itemDeliveredDate': dispute.item_delivered_date.isoformat() if dispute.item_delivered_date else 'N/A',
                'sameCardSuccessOrders': dispute.same_card_success_orders or 0,
                'sameAddressSuccessOrders': dispute.same_address_success_orders or 0,
                'sameIpSuccessOrders': dispute.same_ip_success_orders or 0,
                'sameDeviceSuccessOrders': dispute.same_device_success_orders or 0,
                'checkoutIp': dispute.checkout_ip or 'N/A',
                'checkoutDevice': dispute.checkout_device or 'N/A'
            },
            'customer': {
                'id': customer.id if customer else '',
                'name': customer.name if customer else '',
                'email': customer.email if customer else '',
                'phone': customer.phone if customer else '',
                'accountType': customer.account_type if customer else '',
                'creditScore': customer.credit_score if customer else 0,
                'customerSince': customer.customer_since.isoformat() if customer and customer.customer_since else '',
                'previousDisputes': customer.previous_disputes if customer else 0,
                # New customer fields
                'disputeCustomerWon': customer.dispute_customer_won or 0 if customer else 0,
                'totalPurchaseAmount': customer.total_purchase_amount or 0 if customer else 0,
                'disputePercentage': customer.dispute_percentage or 0 if customer else 0,
                'linkedCustomersCount': customer.linked_customers_count or 0 if customer else 0,
                'linkedCustomersDisputeRate': customer.linked_customers_dispute_rate or 0 if customer else 0,
                'linkedByDevice': customer.linked_by_device or 0 if customer else 0,
                'linkedByIp': customer.linked_by_ip or 0 if customer else 0,
                'linkedByCard': customer.linked_by_card or 0 if customer else 0,
                'linkedByAddress': customer.linked_by_address or 0 if customer else 0
            },
            'disputeReason': dispute.dispute_reason,
            'disputeDescription': dispute.dispute_description,
            'evidence': [],  # Simplified processing
            'riskScore': dispute.risk_score,
            'aiRecommendation': dispute.ai_recommendation,
            'aiConfidence': dispute.ai_confidence,
            'aiAnalysis': dispute.ai_analysis,
            'humanDecision': dispute.human_decision,
            'status': dispute.status,
            'createdAt': dispute.created_at.isoformat(),
            'updatedAt': dispute.updated_at.isoformat(),
            'priority': dispute.priority,
            'category': dispute.category,
            'subcategory': dispute.subcategory,
            'reasonCode': dispute.reason_code,
            'cardNetwork': dispute.card_network,
            'cardIssuer': dispute.card_issuer or 'N/A',
            # Add legitimacy fields at root level for easier access
            'sameCardSuccessOrders': dispute.same_card_success_orders or 0,
            'sameAddressSuccessOrders': dispute.same_address_success_orders or 0,
            'sameIpSuccessOrders': dispute.same_ip_success_orders or 0,
            'sameDeviceSuccessOrders': dispute.same_device_success_orders or 0
        }
        result.append(dispute_dict)
    
    return jsonify(result)

@app.route('/api/disputes/<dispute_id>/analyze', methods=['POST'])
def analyze_dispute(dispute_id):
    """Analyze specific dispute case"""
    dispute = DisputeCase.query.get(dispute_id)
    if not dispute:
        return jsonify({'error': 'Dispute not found'}), 404
    
    customer = Customer.query.get(dispute.customer_id)
    
    # Simulate AI analysis process
    time.sleep(2)  # Simulate analysis delay
    
    # Build analysis data with all fields
    dispute_data = {
        'amount': dispute.amount,
        'merchant_category': dispute.merchant_category,
        'dispute_reason': dispute.dispute_reason,
        'evidence': [],  # Simplified processing
        'same_card_success_orders': dispute.same_card_success_orders or 0,
        'same_address_success_orders': dispute.same_address_success_orders or 0,
        'same_ip_success_orders': dispute.same_ip_success_orders or 0,
        'same_device_success_orders': dispute.same_device_success_orders or 0,
        'item_shipped': dispute.item_shipped or 'N',
        'item_delivered': dispute.item_delivered or 'N',
        'digital_goods': dispute.digital_goods or 'N'
    }
    
    customer_data = {
        'credit_score': customer.credit_score if customer else 650,
        'previous_disputes': customer.previous_disputes if customer else 0,
        'dispute_customer_won': customer.dispute_customer_won or 0 if customer else 0,
        'total_purchase_amount': customer.total_purchase_amount or 0 if customer else 0,
        'dispute_percentage': customer.dispute_percentage or 0 if customer else 0,
        'linked_customers_count': customer.linked_customers_count or 0 if customer else 0,
        'linked_customers_dispute_rate': customer.linked_customers_dispute_rate or 0 if customer else 0,
        'linked_by_device': customer.linked_by_device or 0 if customer else 0,
        'linked_by_ip': customer.linked_by_ip or 0 if customer else 0,
        'linked_by_card': customer.linked_by_card or 0 if customer else 0,
        'linked_by_address': customer.linked_by_address or 0 if customer else 0
    }
    
    # Calculate risk score
    risk_score = analysis_engine.calculate_risk_score(dispute_data, customer_data)
    
    # Generate recommendation
    recommendation, confidence = analysis_engine.generate_recommendation(risk_score)
    
    # Generate analysis report
    analysis = analysis_engine.generate_analysis(dispute_data, customer_data, risk_score, recommendation)
    
    # Update database
    dispute.risk_score = risk_score
    dispute.ai_recommendation = recommendation
    dispute.ai_confidence = confidence
    dispute.ai_analysis = analysis
    dispute.status = 'review' if recommendation == 'review' else 'analyzing'
    dispute.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'riskScore': risk_score,
        'recommendation': recommendation,
        'confidence': confidence,
        'analysis': analysis,
        'keyFactors': _get_key_factors(dispute_data, customer_data),
        'warningFlags': _get_warning_flags(dispute_data, customer_data, risk_score)
    })

def _get_key_factors(dispute_data, customer_data):
    """Get supporting factors"""
    factors = []
    if customer_data.get('credit_score', 0) > 700:
        factors.append('Customer has excellent credit score')
    if customer_data.get('previous_disputes', 0) == 0:
        factors.append('No dispute history records')
    if dispute_data['amount'] < 500:
        factors.append('Dispute amount is small')
    return factors

def _get_warning_flags(dispute_data, customer_data, risk_score):
    """Get risk flags"""
    flags = []
    if customer_data.get('previous_disputes', 0) > 2:
        flags.append('Multiple dispute history')
    if risk_score > 70:
        flags.append('High risk score')
    if dispute_data['amount'] > 2000:
        flags.append('Large transaction amount')
    return flags

@app.route('/api/disputes/<dispute_id>/decision', methods=['POST'])
def make_decision(dispute_id):
    """Make human decision"""
    data = request.json
    decision = data.get('decision')
    
    if decision not in ['approve', 'reject']:
        return jsonify({'error': 'Invalid decision'}), 400
    
    dispute = DisputeCase.query.get(dispute_id)
    if not dispute:
        return jsonify({'error': 'Dispute not found'}), 404
    
    dispute.human_decision = decision
    dispute.status = 'completed'
    dispute.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Decision recorded successfully'})

@app.route('/api/init-demo-data', methods=['POST'])
def init_demo_data():
    """Initialize demo data"""
    # Clear existing data
    db.drop_all()
    db.create_all()
    
    # Create demo customers
    customers = [
        Customer(id='cust_001', name='张伟', email='zhang.wei@email.com', phone='+1-555-0123',
                account_type='白金卡', credit_score=750, customer_since=datetime(2019, 3, 15), previous_disputes=1,
                dispute_customer_won=0, total_purchase_amount=25000.0, dispute_percentage=1.2,
                linked_customers_count=0, linked_customers_dispute_rate=0.0,
                linked_by_device=0, linked_by_ip=0, linked_by_card=0, linked_by_address=0),
        Customer(id='cust_002', name='李明', email='li.ming@email.com', phone='+1-555-0456',
                account_type='普通卡', credit_score=680, customer_since=datetime(2021, 7, 20), previous_disputes=0,
                dispute_customer_won=0, total_purchase_amount=5000.0, dispute_percentage=0.0,
                linked_customers_count=0, linked_customers_dispute_rate=0.0,
                linked_by_device=0, linked_by_ip=0, linked_by_card=0, linked_by_address=0),
        Customer(id='cust_003', name='王芳', email='wang.fang@email.com', phone='+1-555-0789',
                account_type='黑金卡', credit_score=820, customer_since=datetime(2015, 5, 10), previous_disputes=3,
                dispute_customer_won=2, total_purchase_amount=150000.0, dispute_percentage=2.3,
                linked_customers_count=2, linked_customers_dispute_rate=3.5,
                linked_by_device=1, linked_by_ip=1, linked_by_card=0, linked_by_address=1)
    ]
    
    for customer in customers:
        db.session.add(customer)
    
    # Create demo dispute cases
    disputes = [
        DisputeCase(
            id='1', case_number='CD2024001', transaction_id='txn_001', customer_id='cust_001',
            amount=1250.00, merchant_name='TechMart Online', merchant_category='电子产品',
            transaction_date=datetime(2024, 1, 15, 10, 30), location='纽约, NY', card_last4='4567',
            dispute_reason='未授权交易', dispute_description='客户声称没有进行此笔交易。',
            risk_score=45, ai_recommendation='review', ai_confidence=72,
            ai_analysis='该案例存在中等风险。',
            status='pending', priority='medium', category='FRAUD_UNAUTHORIZED', subcategory='1A_Card_Fraud',
            reason_code='10.4', card_network='visa', card_issuer='Chase Bank',
            items='Gaming Laptop', digital_goods='N', login_method='Password', 
            item_shipped='Y', item_delivered='N', same_card_success_orders=0, same_address_success_orders=0,
            same_ip_success_orders=0, same_device_success_orders=0
        ),
        DisputeCase(
            id='2', case_number='CD2024002', transaction_id='txn_002', customer_id='cust_002',
            amount=89.99, merchant_name='QuickFood Delivery', merchant_category='餐饮外卖',
            transaction_date=datetime(2024, 1, 14, 19, 45), location='旧金山, CA', card_last4='8901',
            dispute_reason='商品质量问题', dispute_description='客户收到的食物与订单不符。',
            risk_score=85, ai_recommendation='reject', ai_confidence=88,
            ai_analysis='高风险案例。客户有多个成功订单使用相同支付信息，表明可能为恶意退单。',
            status='pending', priority='high', category='MERCHANT_MERCHANDISE', subcategory='3A_Product_Service',
            reason_code='13.1', card_network='mastercard', card_issuer='Bank of America',
            items='Food Delivery', digital_goods='N', login_method='App Login',
            item_shipped='N', item_delivered='Y', same_card_success_orders=8, same_address_success_orders=8,
            same_ip_success_orders=12, same_device_success_orders=10
        ),
        DisputeCase(
            id='3', case_number='CD2024003', transaction_id='txn_003', customer_id='cust_003',
            amount=3500.00, merchant_name='Luxury Watches Co.', merchant_category='奢侈品',
            transaction_date=datetime(2024, 1, 13, 14, 20), location='迈阿密, FL', card_last4='2345',
            dispute_reason='重复收费', dispute_description='客户声称被重复收费。',
            risk_score=95, ai_recommendation='reject', ai_confidence=92,
            ai_analysis='极高风险案例。客户有大量成功订单记录使用相同信息，明显为恶意退单行为。',
            status='analyzing', priority='critical', category='PROCESSING_ISSUES', subcategory='2B_Technical_Processing',
            reason_code='12.6', card_network='amex', card_issuer='American Express',
            items='Rolex Submariner', digital_goods='N', login_method='Biometric',
            item_shipped='Y', item_delivered='Y', same_card_success_orders=15, same_address_success_orders=20,
            same_ip_success_orders=25, same_device_success_orders=18
        )
    ]
    
    for dispute in disputes:
        db.session.add(dispute)
    
    db.session.commit()
    
    return jsonify({'message': 'Demo data initialized successfully'})

@app.route('/api/analyze/<case_id>/reanalyze', methods=['POST'])
def reanalyze_dispute(case_id):
    """Re-analyze a dispute case with analyst feedback"""
    try:
        data = request.get_json()
        analyst_feedback = data.get('analystFeedback', '')
        
        if not analyst_feedback.strip():
            return jsonify({'error': 'Analyst feedback is required'}), 400
        
        # Get the existing dispute
        dispute = DisputeCase.query.filter_by(id=case_id).first()
        if not dispute:
            return jsonify({'error': 'Dispute not found'}), 404
        
        # Get customer data
        customer = Customer.query.get(dispute.customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Prepare dispute data with analyst feedback
        dispute_data = {
            'id': dispute.id,
            'case_number': dispute.case_number,
            'amount': dispute.amount,
            'currency': dispute.currency,
            'dispute_reason': dispute.dispute_reason,
            'dispute_description': dispute.dispute_description,
            'category': dispute.category,
            'subcategory': dispute.subcategory,
            'same_card_success_orders': dispute.same_card_success_orders,
            'same_address_success_orders': dispute.same_address_success_orders,
            'same_ip_success_orders': dispute.same_ip_success_orders,
            'same_device_success_orders': dispute.same_device_success_orders,
            'digital_goods': dispute.digital_goods,
            'item_shipped': dispute.item_shipped,
            'item_delivered': dispute.item_delivered,
            'analyst_feedback': analyst_feedback  # Include analyst feedback
        }
        
        customer_data = {
            'previous_disputes': customer.previous_disputes,
            'account_age_days': customer.account_age_days,
            'total_transaction_amount': customer.total_transaction_amount,
            'dispute_percentage': customer.dispute_percentage
        }
        
        # Re-run analysis with analyst context
        analysis_engine = ChargebackAnalysisEngine()
        result = analysis_engine.analyze_dispute(dispute_data, customer_data)
        
        # Update the dispute with new analysis results
        dispute.ai_analysis = f"UPDATED ANALYSIS (with analyst feedback):\n\n{result['analysis']}\n\n📝 ANALYST FEEDBACK:\n\"{analyst_feedback}\""
        dispute.risk_score = result['risk_score']
        dispute.ai_recommendation = result['recommendation']
        dispute.ai_confidence = result['confidence']
        dispute.analyst_feedback = analyst_feedback
        dispute.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'riskScore': result['risk_score'],
            'recommendation': result['recommendation'],
            'confidence': result['confidence'],
            'analysis': result['analysis'],
            'keyFactors': result.get('key_factors', []),
            'warningFlags': result.get('warning_flags', [])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5002)
