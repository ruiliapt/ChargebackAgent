"""
Main Logic: Core AI Agent orchestration for chargeback dispute management
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

from resources.chargeback_data import ChargebackDataRepository, DisputeResource
from prompts.analysis_prompts import PromptTemplateManager
from tools.analysis_tools import RiskScoringEngine, RiskAssessment

@dataclass
class AgentDecision:
    """Agent decision output structure"""
    dispute_id: str
    recommendation: str
    confidence: int
    risk_score: int
    reasoning: str
    supporting_factors: List[str]
    warning_flags: List[str]
    required_actions: List[str]
    estimated_resolution_time: int
    category_assessment: Dict[str, Any]

class ChargebackAgent:
    """Main AI Agent for chargeback dispute management"""
    
    def __init__(self, data_repository: ChargebackDataRepository):
        self.data_repo = data_repository
        self.prompt_manager = PromptTemplateManager()
        self.risk_engine = RiskScoringEngine()
        self.logger = self._setup_logging()
        
        # Agent configuration
        self.config = {
            'risk_tolerance': 'moderate',
            'auto_approval_threshold': 25,
            'auto_rejection_threshold': 75,
            'fraud_escalation_threshold': 80,
            'processing_sla_hours': 72,
            'fraud_sla_hours': 24
        }
    
    def analyze_dispute(self, dispute_id: str) -> AgentDecision:
        """
        Main analysis method - orchestrates the complete dispute assessment
        """
        self.logger.info(f"Starting analysis for dispute {dispute_id}")
        
        # Step 1: Gather resources
        dispute_data = self._gather_dispute_data(dispute_id)
        if not dispute_data:
            raise ValueError(f"Dispute {dispute_id} not found")
        
        # Step 2: Perform risk assessment
        risk_assessment = self._assess_risk(dispute_data)
        
        # Step 3: Generate category-specific analysis
        category_analysis = self._perform_category_analysis(dispute_data, risk_assessment)
        
        # Step 4: Make final decision
        decision = self._make_decision(dispute_data, risk_assessment, category_analysis)
        
        # Step 5: Log and return
        self.logger.info(f"Analysis complete for {dispute_id}: {decision.recommendation}")
        return decision
    
    def batch_analyze_disputes(self, category: str = None, priority: str = None) -> List[AgentDecision]:
        """
        Batch analysis for multiple disputes with filtering
        """
        disputes = self._get_disputes_for_analysis(category, priority)
        decisions = []
        
        for dispute in disputes:
            try:
                decision = self.analyze_dispute(dispute.id)
                decisions.append(decision)
            except Exception as e:
                self.logger.error(f"Failed to analyze dispute {dispute.id}: {e}")
                continue
        
        return decisions
    
    def get_insights_summary(self) -> Dict[str, Any]:
        """
        Generate high-level insights and analytics
        """
        return {
            'fraud_trends': self._analyze_fraud_trends(),
            'processing_health': self._analyze_processing_health(),
            'merchant_performance': self._analyze_merchant_performance(),
            'risk_distribution': self._analyze_risk_distribution(),
            'recommendations': self._generate_strategic_recommendations()
        }
    
    def handle_chat_query(self, user_query: str, context: Dict = None) -> str:
        """
        Handle conversational queries about disputes and analytics
        """
        # Analyze query intent
        intent = self._analyze_query_intent(user_query)
        
        # Gather relevant context
        query_context = self._gather_query_context(intent, context or {})
        
        # Generate contextual response
        response = self._generate_chat_response(user_query, intent, query_context)
        
        return response
    
    def _gather_dispute_data(self, dispute_id: str) -> Dict[str, Any]:
        """Gather all relevant data for dispute analysis"""
        dispute = self.data_repo.get_dispute_by_id(dispute_id)
        if not dispute:
            return None
        
        customer = self.data_repo.get_customer_data(dispute.customer_id)
        fraud_indicators = self.data_repo.get_fraud_indicators(dispute_id)
        
        return {
            'dispute': dispute,
            'customer': customer,
            'fraud_indicators': fraud_indicators,
            'dispute_dict': {
                'case_number': dispute.case_number,
                'category': dispute.category,
                'subcategory': dispute.subcategory,
                'reason_code': dispute.reason_code,
                'card_network': dispute.card_network,
                'amount': dispute.amount,
                'merchant_name': dispute.merchant_name,
                'merchant_category': dispute.merchant_category,
                'dispute_description': dispute.dispute_description,
                'status': dispute.status,
                'priority': dispute.priority
            },
            'customer_dict': {
                'id': customer.id if customer else 'unknown',
                'credit_score': customer.credit_score if customer else 650,
                'account_type': customer.account_type if customer else 'standard',
                'previous_disputes': customer.previous_disputes if customer else 0,
                'customer_since': customer.customer_since.isoformat() if customer else '2020-01-01'
            }
        }
    
    def _assess_risk(self, dispute_data: Dict) -> RiskAssessment:
        """Perform comprehensive risk assessment"""
        return self.risk_engine.calculate_comprehensive_risk(
            dispute_data['dispute_dict'],
            dispute_data['customer_dict'],
            dispute_data['fraud_indicators']
        )
    
    def _perform_category_analysis(self, dispute_data: Dict, risk_assessment: RiskAssessment) -> Dict:
        """Perform category-specific deep analysis"""
        category = dispute_data['dispute_dict']['category']
        
        analysis = {
            'category': category,
            'specialized_assessment': {},
            'compliance_check': {},
            'evidence_requirements': [],
            'escalation_needed': False
        }
        
        if category == 'FRAUD_UNAUTHORIZED':
            analysis.update(self._analyze_fraud_case(dispute_data, risk_assessment))
        elif category == 'PROCESSING_ISSUES':
            analysis.update(self._analyze_processing_case(dispute_data, risk_assessment))
        elif category == 'MERCHANT_MERCHANDISE':
            analysis.update(self._analyze_merchant_case(dispute_data, risk_assessment))
        
        return analysis
    
    def _analyze_fraud_case(self, dispute_data: Dict, risk_assessment: RiskAssessment) -> Dict:
        """Specialized fraud case analysis"""
        return {
            'fraud_probability': risk_assessment.category_specific_score.get('fraud', 50),
            'investigation_priority': 'high' if risk_assessment.score > 70 else 'medium',
            'law_enforcement_flag': risk_assessment.score > 85,
            'customer_verification_required': True,
            'evidence_requirements': ['transaction_logs', 'customer_authentication', 'fraud_indicators'],
            'escalation_needed': risk_assessment.score > self.config['fraud_escalation_threshold']
        }
    
    def _analyze_processing_case(self, dispute_data: Dict, risk_assessment: RiskAssessment) -> Dict:
        """Specialized processing issue analysis"""
        return {
            'technical_liability': risk_assessment.category_specific_score.get('processing', 0) > 60,
            'system_investigation_required': True,
            'processor_notification_needed': risk_assessment.score > 50,
            'evidence_requirements': ['system_logs', 'authorization_records', 'settlement_data'],
            'escalation_needed': risk_assessment.category_specific_score.get('processing', 0) > 80
        }
    
    def _analyze_merchant_case(self, dispute_data: Dict, risk_assessment: RiskAssessment) -> Dict:
        """Specialized merchant case analysis"""
        return {
            'merchant_liability_score': risk_assessment.category_specific_score.get('merchant', 30),
            'policy_compliance_check': True,
            'customer_service_review': True,
            'evidence_requirements': ['delivery_confirmation', 'customer_communication', 'return_policy'],
            'escalation_needed': risk_assessment.category_specific_score.get('merchant', 0) > 70
        }
    
    def _make_decision(self, dispute_data: Dict, risk_assessment: RiskAssessment, category_analysis: Dict) -> AgentDecision:
        """Make final decision based on all analysis"""
        dispute = dispute_data['dispute']
        
        # Determine required actions
        required_actions = self._determine_required_actions(risk_assessment, category_analysis)
        
        # Estimate resolution time
        resolution_time = self._estimate_resolution_time(
            dispute_data['dispute_dict']['category'], 
            risk_assessment.recommendation,
            category_analysis
        )
        
        # Generate detailed reasoning
        reasoning = self._generate_reasoning(dispute_data, risk_assessment, category_analysis)
        
        return AgentDecision(
            dispute_id=dispute.id,
            recommendation=risk_assessment.recommendation,
            confidence=risk_assessment.confidence,
            risk_score=risk_assessment.score,
            reasoning=reasoning,
            supporting_factors=risk_assessment.factors,
            warning_flags=risk_assessment.warnings,
            required_actions=required_actions,
            estimated_resolution_time=resolution_time,
            category_assessment=category_analysis
        )
    
    def _determine_required_actions(self, risk_assessment: RiskAssessment, category_analysis: Dict) -> List[str]:
        """Determine specific actions required for case resolution"""
        actions = []
        
        # Standard actions based on recommendation
        if risk_assessment.recommendation == 'approve':
            actions.append('Process refund to customer')
            actions.append('Close case with approval')
        elif risk_assessment.recommendation == 'reject':
            actions.append('Prepare rejection documentation')
            actions.append('Notify customer of decision')
        else:  # review
            actions.append('Assign to specialist for manual review')
            actions.append('Gather additional evidence')
        
        # Category-specific actions
        if category_analysis.get('escalation_needed'):
            actions.append('Escalate to senior analyst')
        
        if category_analysis.get('law_enforcement_flag'):
            actions.append('Report to fraud investigation unit')
        
        if category_analysis.get('system_investigation_required'):
            actions.append('Initiate technical system investigation')
        
        return actions
    
    def _estimate_resolution_time(self, category: str, recommendation: str, category_analysis: Dict) -> int:
        """Estimate resolution time in hours"""
        base_times = {
            'FRAUD_UNAUTHORIZED': 24,
            'PROCESSING_ISSUES': 72,
            'MERCHANT_MERCHANDISE': 120
        }
        
        base_time = base_times.get(category, 96)
        
        # Adjust based on recommendation
        if recommendation == 'approve':
            return base_time // 2
        elif recommendation == 'reject':
            return int(base_time * 0.75)
        else:  # review
            return int(base_time * 1.5)
    
    def _generate_reasoning(self, dispute_data: Dict, risk_assessment: RiskAssessment, category_analysis: Dict) -> str:
        """Generate detailed reasoning for the decision"""
        category = dispute_data['dispute_dict']['category']
        amount = dispute_data['dispute_dict']['amount']
        
        reasoning = f"Analysis of {category} dispute for ${amount:.2f}. "
        reasoning += f"Risk score: {risk_assessment.score}/100 ({risk_assessment.confidence}% confidence). "
        
        if risk_assessment.factors:
            reasoning += f"Supporting factors: {', '.join(risk_assessment.factors[:3])}. "
        
        if risk_assessment.warnings:
            reasoning += f"Risk factors: {', '.join(risk_assessment.warnings[:3])}. "
        
        reasoning += f"Recommendation: {risk_assessment.recommendation.upper()} based on {category.lower()} analysis framework."
        
        return reasoning
    
    def _get_disputes_for_analysis(self, category: str = None, priority: str = None) -> List[DisputeResource]:
        """Get disputes that need analysis"""
        if category:
            return self.data_repo.get_disputes_by_category(category)
        else:
            # This would need to be implemented in the repository
            return []
    
    def _analyze_fraud_trends(self) -> Dict:
        """Analyze fraud trends across all cases"""
        return {
            'trend': 'stable',
            'high_risk_categories': ['Luxury Goods', 'Online Services'],
            'emerging_patterns': ['CNP fraud increase', 'Account takeover attempts']
        }
    
    def _analyze_processing_health(self) -> Dict:
        """Analyze processing system health"""
        return {
            'system_health': 'good',
            'error_rate': '2.1%',
            'top_issues': ['Authorization timeouts', 'Duplicate processing']
        }
    
    def _analyze_merchant_performance(self) -> Dict:
        """Analyze merchant performance metrics"""
        return {
            'top_performers': ['Merchant A', 'Merchant B'],
            'high_dispute_merchants': ['Merchant X', 'Merchant Y'],
            'compliance_score': '87%'
        }
    
    def _analyze_risk_distribution(self) -> Dict:
        """Analyze risk score distribution"""
        return {
            'high_risk_percentage': '20%',
            'medium_risk_percentage': '45%',
            'low_risk_percentage': '35%'
        }
    
    def _generate_strategic_recommendations(self) -> List[str]:
        """Generate strategic recommendations"""
        return [
            'Increase monitoring for CNP fraud',
            'Review authorization timeout thresholds',
            'Implement enhanced merchant onboarding'
        ]
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze user query intent"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['analyze', 'analysis', 'assess']):
            return 'analysis_request'
        elif any(word in query_lower for word in ['fraud', 'suspicious']):
            return 'fraud_inquiry'
        elif any(word in query_lower for word in ['summary', 'overview', 'status']):
            return 'summary_request'
        else:
            return 'general_inquiry'
    
    def _gather_query_context(self, intent: str, context: Dict) -> Dict:
        """Gather relevant context for query response"""
        return {
            'intent': intent,
            'total_cases': context.get('total_cases', 200),
            'pending_cases': context.get('pending_cases', 64),
            'high_risk_cases': context.get('high_risk_cases', 40)
        }
    
    def _generate_chat_response(self, query: str, intent: str, context: Dict) -> str:
        """Generate contextual chat response"""
        if intent == 'analysis_request':
            return f"I can help analyze dispute cases. Currently tracking {context['total_cases']} cases with {context['pending_cases']} pending review."
        elif intent == 'fraud_inquiry':
            return f"Fraud monitoring active. {context['high_risk_cases']} high-risk cases identified requiring immediate attention."
        elif intent == 'summary_request':
            return f"System Status: {context['total_cases']} total cases, {context['pending_cases']} pending, {context['high_risk_cases']} high-risk. All systems operational."
        else:
            return "I'm here to help with chargeback dispute analysis. I can analyze cases, provide risk assessments, and offer insights on fraud patterns."
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the agent"""
        logger = logging.getLogger('ChargebackAgent')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

# Factory function for creating configured agent instances
def create_chargeback_agent(db_session) -> ChargebackAgent:
    """Factory function to create a properly configured chargeback agent"""
    data_repo = ChargebackDataRepository(db_session)
    return ChargebackAgent(data_repo)

