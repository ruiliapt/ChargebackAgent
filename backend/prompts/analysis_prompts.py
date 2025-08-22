"""
Prompts: AI prompting templates for chargeback analysis
"""

from typing import Dict, Any

class ChargebackAnalysisPrompts:
    """Structured prompts for AI-powered chargeback analysis"""
    
    @staticmethod
    def fraud_analysis_prompt(dispute_data: Dict, customer_data: Dict) -> str:
        """Generate prompt for fraud case analysis"""
        return f"""
        You are an expert fraud analyst reviewing a chargeback dispute case.
        
        CASE DETAILS:
        - Case ID: {dispute_data.get('case_number')}
        - Amount: ${dispute_data.get('amount', 0):.2f}
        - Merchant: {dispute_data.get('merchant_name')} ({dispute_data.get('merchant_category')})
        - Reason Code: {dispute_data.get('reason_code')} ({dispute_data.get('card_network')})
        - Description: {dispute_data.get('dispute_description')}
        
        CUSTOMER PROFILE:
        - Credit Score: {customer_data.get('credit_score', 'Unknown')}
        - Account Type: {customer_data.get('account_type', 'Unknown')}
        - Previous Disputes: {customer_data.get('previous_disputes', 0)}
        - Customer Since: {customer_data.get('customer_since', 'Unknown')}
        
        ANALYSIS FRAMEWORK:
        1. Fraud Indicators Assessment
        2. Transaction Pattern Analysis
        3. Customer Behavior Evaluation
        4. Risk Factor Identification
        5. Recommendation with Confidence Level
        
        Please provide:
        - Risk score (0-100)
        - Recommendation (approve/reject/review)
        - Confidence level (0-100)
        - Key risk factors
        - Detailed analysis explanation
        
        Focus on fraud-specific indicators such as:
        - Transaction velocity and patterns
        - Geographic anomalies
        - Customer behavior consistency
        - Merchant fraud history
        - Card network fraud signals
        """
    
    @staticmethod
    def processing_issue_prompt(dispute_data: Dict, technical_context: Dict) -> str:
        """Generate prompt for processing issue analysis"""
        return f"""
        You are a payment processing specialist analyzing a technical chargeback dispute.
        
        TECHNICAL CASE DETAILS:
        - Case ID: {dispute_data.get('case_number')}
        - Processing Issue: {dispute_data.get('subcategory')}
        - Amount: ${dispute_data.get('amount', 0):.2f}
        - Reason Code: {dispute_data.get('reason_code')} ({dispute_data.get('card_network')})
        - Issue Description: {dispute_data.get('dispute_description')}
        
        PROCESSING CONTEXT:
        - Authorization Status: {technical_context.get('auth_status', 'Unknown')}
        - Settlement Status: {technical_context.get('settlement_status', 'Unknown')}
        - System Logs: {technical_context.get('system_logs', 'Not available')}
        
        ANALYSIS FOCUS:
        1. Technical Process Validation
        2. System Error Identification
        3. Compliance Check
        4. Liability Assessment
        5. Resolution Recommendation
        
        Evaluate:
        - Processing system integrity
        - Authorization compliance
        - Settlement accuracy
        - Technical liability
        - Remediation actions required
        
        Provide technical analysis with emphasis on:
        - System process validation
        - Error root cause analysis
        - Compliance with card network rules
        - Recommended technical remediation
        """
    
    @staticmethod
    def merchant_dispute_prompt(dispute_data: Dict, merchant_context: Dict) -> str:
        """Generate prompt for merchant/merchandise dispute analysis"""
        return f"""
        You are a merchant relations specialist analyzing a business dispute case.
        
        MERCHANT DISPUTE DETAILS:
        - Case ID: {dispute_data.get('case_number')}
        - Dispute Type: {dispute_data.get('subcategory')}
        - Amount: ${dispute_data.get('amount', 0):.2f}
        - Merchant: {dispute_data.get('merchant_name')} ({dispute_data.get('merchant_category')})
        - Customer Claim: {dispute_data.get('dispute_description')}
        
        MERCHANT CONTEXT:
        - Business Type: {merchant_context.get('business_type', 'Unknown')}
        - Return Policy: {merchant_context.get('return_policy', 'Standard')}
        - Dispute History: {merchant_context.get('dispute_rate', 'Unknown')}
        - Customer Service Rating: {merchant_context.get('service_rating', 'Unknown')}
        
        BUSINESS ANALYSIS FRAMEWORK:
        1. Policy Compliance Review
        2. Service Quality Assessment
        3. Customer Communication Evaluation
        4. Evidence Sufficiency Check
        5. Fair Resolution Determination
        
        Evaluate:
        - Merchant policy adherence
        - Service delivery quality
        - Customer communication
        - Evidence documentation
        - Fair business practices
        
        Consider:
        - Consumer protection laws
        - Industry best practices
        - Merchant reputation impact
        - Customer satisfaction
        - Long-term relationship preservation
        """
    
    @staticmethod
    def risk_scoring_prompt(all_factors: Dict) -> str:
        """Generate comprehensive risk scoring prompt"""
        return f"""
        You are a senior risk analyst creating a comprehensive risk assessment.
        
        COMPREHENSIVE CASE DATA:
        {all_factors}
        
        RISK SCORING METHODOLOGY:
        
        1. FRAUD RISK FACTORS (40% weight):
           - Transaction patterns and velocity
           - Geographic and behavioral anomalies
           - Customer authentication status
           - Historical fraud indicators
        
        2. OPERATIONAL RISK FACTORS (30% weight):
           - Processing system integrity
           - Authorization compliance
           - Technical error probability
           - Settlement accuracy
        
        3. BUSINESS RISK FACTORS (30% weight):
           - Merchant reputation and history
           - Customer service quality
           - Policy compliance
           - Industry risk factors
        
        CALCULATE:
        - Overall risk score (0-100)
        - Category-specific risk scores
        - Confidence interval
        - Key risk drivers
        - Mitigation recommendations
        
        PROVIDE:
        - Final risk score with justification
        - Risk category classification
        - Top 3 risk factors
        - Recommended actions
        - Monitoring requirements
        """
    
    @staticmethod
    def chat_response_prompt(user_query: str, context: Dict) -> str:
        """Generate prompt for chat assistant responses"""
        return f"""
        You are an intelligent chargeback dispute assistant helping analysts.
        
        USER QUERY: {user_query}
        
        CURRENT CONTEXT:
        - Total Cases: {context.get('total_cases', 0)}
        - Pending Cases: {context.get('pending_cases', 0)}
        - High Risk Cases: {context.get('high_risk_cases', 0)}
        - Recent Activity: {context.get('recent_activity', 'None')}
        
        RESPONSE GUIDELINES:
        1. Be professional and knowledgeable
        2. Provide actionable insights
        3. Reference specific data when possible
        4. Suggest next steps or actions
        5. Maintain focus on dispute management
        
        CAPABILITIES:
        - Case analysis and recommendations
        - Risk assessment interpretation
        - Category-based insights
        - Workflow guidance
        - Industry best practices
        
        Provide a helpful, accurate response that assists the analyst in their work.
        """
    
    @staticmethod
    def decision_support_prompt(analysis_results: Dict, business_context: Dict) -> str:
        """Generate prompt for decision support recommendations"""
        return f"""
        You are a senior decision support specialist providing final recommendations.
        
        ANALYSIS RESULTS:
        {analysis_results}
        
        BUSINESS CONTEXT:
        - Risk tolerance: {business_context.get('risk_tolerance', 'moderate')}
        - Regulatory requirements: {business_context.get('regulatory_focus', 'standard')}
        - Customer relationship priority: {business_context.get('customer_priority', 'balanced')}
        - Cost considerations: {business_context.get('cost_sensitivity', 'moderate')}
        
        DECISION FRAMEWORK:
        1. Risk-benefit analysis
        2. Regulatory compliance check
        3. Customer impact assessment
        4. Financial cost evaluation
        5. Precedent consideration
        
        PROVIDE:
        - Clear recommendation (approve/reject/investigate)
        - Confidence level and reasoning
        - Alternative options if applicable
        - Risk mitigation strategies
        - Expected outcomes and monitoring plan
        
        Focus on practical, business-aligned decisions that balance risk, compliance, and customer relationships.
        """

class PromptTemplateManager:
    """Manages and customizes prompt templates"""
    
    def __init__(self):
        self.prompts = ChargebackAnalysisPrompts()
    
    def get_analysis_prompt(self, category: str, dispute_data: Dict, context: Dict) -> str:
        """Get appropriate analysis prompt based on dispute category"""
        if category == 'FRAUD_UNAUTHORIZED':
            return self.prompts.fraud_analysis_prompt(dispute_data, context)
        elif category == 'PROCESSING_ISSUES':
            return self.prompts.processing_issue_prompt(dispute_data, context)
        elif category == 'MERCHANT_MERCHANDISE':
            return self.prompts.merchant_dispute_prompt(dispute_data, context)
        else:
            return self.prompts.risk_scoring_prompt({**dispute_data, **context})
    
    def customize_prompt(self, base_prompt: str, customizations: Dict) -> str:
        """Apply custom modifications to prompts"""
        prompt = base_prompt
        for key, value in customizations.items():
            prompt = prompt.replace(f"{{{key}}}", str(value))
        return prompt

