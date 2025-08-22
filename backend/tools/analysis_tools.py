"""
Tools: Analysis and utility tools for chargeback processing
"""

import re
import math
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class RiskAssessment:
    """Risk assessment result structure"""
    score: int
    confidence: int
    recommendation: str
    factors: List[str]
    warnings: List[str]
    category_specific_score: Dict[str, int]

class FraudDetectionTool:
    """Advanced fraud detection and analysis tool"""
    
    def __init__(self):
        self.velocity_thresholds = {
            'transactions_per_hour': 5,
            'transactions_per_day': 20,
            'amount_per_hour': 2000,
            'amount_per_day': 10000
        }
        
        self.suspicious_patterns = [
            'rapid_succession_transactions',
            'round_dollar_amounts',
            'geographic_anomalies',
            'unusual_merchant_categories',
            'high_value_new_customer'
        ]
    
    def analyze_transaction_velocity(self, customer_id: str, transaction_data: Dict) -> Dict:
        """Analyze transaction velocity for fraud indicators"""
        # Simplified implementation - in production would query transaction history
        velocity_score = 0
        flags = []
        
        amount = transaction_data.get('amount', 0)
        if amount > 1000:
            velocity_score += 20
            flags.append('high_value_transaction')
        
        if amount % 100 == 0 and amount > 500:
            velocity_score += 15
            flags.append('round_dollar_amount')
        
        return {
            'velocity_score': velocity_score,
            'flags': flags,
            'risk_level': 'high' if velocity_score > 50 else 'medium' if velocity_score > 25 else 'low'
        }
    
    def detect_geographic_anomalies(self, customer_profile: Dict, transaction_location: str) -> Dict:
        """Detect geographic inconsistencies"""
        # Simplified geographic analysis
        home_location = customer_profile.get('primary_location', 'Unknown')
        travel_score = 0
        
        if home_location != 'Unknown' and transaction_location:
            # Simplified distance calculation
            if home_location.split(',')[1].strip() != transaction_location.split(',')[1].strip():
                travel_score = 30
        
        return {
            'geographic_risk': travel_score,
            'is_travel': travel_score > 0,
            'risk_explanation': f"Transaction in {transaction_location}, customer typically in {home_location}"
        }
    
    def assess_behavioral_patterns(self, customer_data: Dict, transaction_data: Dict) -> Dict:
        """Assess behavioral consistency"""
        behavior_score = 0
        patterns = []
        
        # Customer history analysis
        previous_disputes = customer_data.get('previous_disputes', 0)
        if previous_disputes > 3:
            behavior_score += 25
            patterns.append('high_dispute_history')
        
        credit_score = customer_data.get('credit_score', 650)
        if credit_score < 600:
            behavior_score += 15
            patterns.append('low_credit_score')
        
        account_age_days = (datetime.now() - datetime.fromisoformat(customer_data.get('customer_since', '2020-01-01'))).days
        if account_age_days < 90:
            behavior_score += 20
            patterns.append('new_customer')
        
        return {
            'behavioral_risk': behavior_score,
            'risk_patterns': patterns,
            'account_stability': 'stable' if account_age_days > 365 else 'new'
        }

class ProcessingAnalysisTool:
    """Technical processing analysis tool"""
    
    def __init__(self):
        self.error_patterns = {
            'duplicate_processing': r'duplicate|multiple|twice',
            'authorization_failure': r'auth|authorization|declined',
            'settlement_error': r'settlement|clearing|batch',
            'amount_mismatch': r'amount|currency|total'
        }
    
    def analyze_processing_error(self, dispute_description: str, reason_code: str) -> Dict:
        """Analyze technical processing errors"""
        error_type = 'unknown'
        technical_score = 0
        
        description_lower = dispute_description.lower()
        
        for error, pattern in self.error_patterns.items():
            if re.search(pattern, description_lower):
                error_type = error
                break
        
        # Technical error scoring
        if reason_code in ['12.6', '4834', 'P08']:  # Duplicate processing codes
            technical_score = 85
            error_type = 'duplicate_processing'
        elif reason_code in ['11.1', '11.2', '11.3', '4808']:  # Auth issues
            technical_score = 75
            error_type = 'authorization_failure'
        elif reason_code in ['12.1', '4842']:  # Late presentment
            technical_score = 70
            error_type = 'settlement_error'
        
        return {
            'error_type': error_type,
            'technical_score': technical_score,
            'system_responsibility': technical_score > 60,
            'recommended_action': self._get_technical_action(error_type)
        }
    
    def _get_technical_action(self, error_type: str) -> str:
        """Get recommended action for technical errors"""
        actions = {
            'duplicate_processing': 'Refund duplicate transaction, review processing controls',
            'authorization_failure': 'Investigate authorization logs, verify merchant compliance',
            'settlement_error': 'Review settlement timing, check batch processing',
            'amount_mismatch': 'Reconcile transaction amounts, verify currency conversion',
            'unknown': 'Escalate to technical team for detailed investigation'
        }
        return actions.get(error_type, actions['unknown'])

class MerchantAnalysisTool:
    """Merchant and business analysis tool"""
    
    def __init__(self):
        self.merchant_categories = {
            'high_risk': ['Adult Entertainment', 'Gambling', 'Cryptocurrency', 'Multi-level Marketing'],
            'medium_risk': ['Travel', 'Electronics', 'Luxury Goods', 'Online Services'],
            'low_risk': ['Grocery', 'Gas Stations', 'Utilities', 'Subscription Services']
        }
    
    def assess_merchant_risk(self, merchant_name: str, merchant_category: str) -> Dict:
        """Assess merchant-specific risk factors"""
        risk_level = 'low'
        risk_score = 10
        
        for level, categories in self.merchant_categories.items():
            if merchant_category in categories:
                risk_level = level
                break
        
        # Risk scoring by category
        if risk_level == 'high_risk':
            risk_score = 70
        elif risk_level == 'medium_risk':
            risk_score = 40
        
        # Additional merchant-specific factors
        if 'online' in merchant_name.lower():
            risk_score += 10
        
        return {
            'merchant_risk_level': risk_level,
            'merchant_risk_score': risk_score,
            'category_risk': merchant_category,
            'risk_factors': self._identify_merchant_risk_factors(merchant_name, merchant_category)
        }
    
    def analyze_policy_compliance(self, dispute_data: Dict) -> Dict:
        """Analyze merchant policy compliance"""
        compliance_score = 80  # Default good compliance
        issues = []
        
        # Analyze dispute reason for policy violations
        reason = dispute_data.get('dispute_reason', '').lower()
        
        if 'cancelled' in reason and 'recurring' in reason:
            compliance_score -= 20
            issues.append('subscription_cancellation_difficulty')
        
        if 'not received' in reason:
            compliance_score -= 15
            issues.append('delivery_fulfillment_issue')
        
        if 'refund' in reason and 'not processed' in reason:
            compliance_score -= 25
            issues.append('refund_processing_delay')
        
        return {
            'compliance_score': max(compliance_score, 0),
            'policy_issues': issues,
            'recommended_evidence': self._get_required_evidence(dispute_data),
            'merchant_liability': compliance_score < 60
        }
    
    def _identify_merchant_risk_factors(self, merchant_name: str, category: str) -> List[str]:
        """Identify specific merchant risk factors"""
        factors = []
        
        if category in self.merchant_categories['high_risk']:
            factors.append('high_risk_industry')
        
        if 'online' in merchant_name.lower():
            factors.append('card_not_present_transactions')
        
        return factors
    
    def _get_required_evidence(self, dispute_data: Dict) -> List[str]:
        """Get required evidence based on dispute type"""
        evidence_requirements = {
            'not received': ['delivery_confirmation', 'tracking_number', 'shipping_receipt'],
            'cancelled': ['cancellation_policy', 'cancellation_request', 'refund_processing'],
            'defective': ['product_description', 'quality_control_records', 'return_policy'],
            'unauthorized': ['authorization_logs', 'customer_verification', 'fraud_analysis']
        }
        
        reason = dispute_data.get('dispute_reason', '').lower()
        for key, evidence in evidence_requirements.items():
            if key in reason:
                return evidence
        
        return ['transaction_receipt', 'customer_communication', 'merchant_terms']

class RiskScoringEngine:
    """Comprehensive risk scoring engine"""
    
    def __init__(self):
        self.fraud_tool = FraudDetectionTool()
        self.processing_tool = ProcessingAnalysisTool()
        self.merchant_tool = MerchantAnalysisTool()
        
        self.category_weights = {
            'FRAUD_UNAUTHORIZED': {'fraud': 0.7, 'processing': 0.1, 'merchant': 0.2},
            'PROCESSING_ISSUES': {'fraud': 0.2, 'processing': 0.7, 'merchant': 0.1},
            'MERCHANT_MERCHANDISE': {'fraud': 0.1, 'processing': 0.2, 'merchant': 0.7}
        }
    
    def calculate_comprehensive_risk(self, dispute_data: Dict, customer_data: Dict, context: Dict) -> RiskAssessment:
        """Calculate comprehensive risk assessment"""
        category = dispute_data.get('category', 'UNKNOWN')
        
        # Get component scores
        fraud_analysis = self.fraud_tool.analyze_transaction_velocity(
            customer_data.get('id'), dispute_data
        )
        behavioral_analysis = self.fraud_tool.assess_behavioral_patterns(
            customer_data, dispute_data
        )
        processing_analysis = self.processing_tool.analyze_processing_error(
            dispute_data.get('dispute_description', ''), 
            dispute_data.get('reason_code', '')
        )
        merchant_analysis = self.merchant_tool.assess_merchant_risk(
            dispute_data.get('merchant_name', ''),
            dispute_data.get('merchant_category', '')
        )
        
        # Calculate weighted scores
        fraud_score = (fraud_analysis['velocity_score'] + behavioral_analysis['behavioral_risk']) / 2
        processing_score = processing_analysis['technical_score']
        merchant_score = merchant_analysis['merchant_risk_score']
        
        # Apply category-specific weights
        weights = self.category_weights.get(category, {'fraud': 0.4, 'processing': 0.3, 'merchant': 0.3})
        
        final_score = int(
            fraud_score * weights['fraud'] +
            processing_score * weights['processing'] +
            merchant_score * weights['merchant']
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(final_score, category)
        confidence = self._calculate_confidence(final_score, category)
        
        # Collect factors and warnings
        factors = self._collect_positive_factors(fraud_analysis, processing_analysis, merchant_analysis)
        warnings = self._collect_warning_factors(fraud_analysis, processing_analysis, merchant_analysis)
        
        return RiskAssessment(
            score=final_score,
            confidence=confidence,
            recommendation=recommendation,
            factors=factors,
            warnings=warnings,
            category_specific_score={
                'fraud': int(fraud_score),
                'processing': int(processing_score),
                'merchant': int(merchant_score)
            }
        )
    
    def _generate_recommendation(self, score: int, category: str) -> str:
        """Generate recommendation based on score and category"""
        thresholds = {
            'FRAUD_UNAUTHORIZED': {'approve': 30, 'reject': 70},
            'PROCESSING_ISSUES': {'approve': 40, 'reject': 80},
            'MERCHANT_MERCHANDISE': {'approve': 35, 'reject': 75}
        }
        
        category_thresholds = thresholds.get(category, {'approve': 35, 'reject': 75})
        
        if score <= category_thresholds['approve']:
            return 'approve'
        elif score >= category_thresholds['reject']:
            return 'reject'
        else:
            return 'review'
    
    def _calculate_confidence(self, score: int, category: str) -> int:
        """Calculate confidence level for the assessment"""
        # Higher confidence for extreme scores, lower for middle range
        if score <= 20 or score >= 80:
            return random.randint(85, 95)
        elif score <= 35 or score >= 65:
            return random.randint(70, 85)
        else:
            return random.randint(60, 75)
    
    def _collect_positive_factors(self, fraud_analysis: Dict, processing_analysis: Dict, merchant_analysis: Dict) -> List[str]:
        """Collect positive risk factors"""
        factors = []
        
        if fraud_analysis['velocity_score'] < 20:
            factors.append('Normal transaction velocity')
        
        if processing_analysis['technical_score'] < 30:
            factors.append('No technical processing issues')
        
        if merchant_analysis['merchant_risk_score'] < 30:
            factors.append('Low-risk merchant category')
        
        return factors
    
    def _collect_warning_factors(self, fraud_analysis: Dict, processing_analysis: Dict, merchant_analysis: Dict) -> List[str]:
        """Collect warning factors"""
        warnings = []
        
        if fraud_analysis['velocity_score'] > 50:
            warnings.append('High transaction velocity risk')
        
        if processing_analysis['technical_score'] > 70:
            warnings.append('Technical processing error detected')
        
        if merchant_analysis['merchant_risk_score'] > 60:
            warnings.append('High-risk merchant category')
        
        return warnings

import random  # For demo confidence calculation

