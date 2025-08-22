#!/usr/bin/env python3
"""
Test script to demonstrate the 4-layer AI Agent Architecture
Resources → Prompts → Tools → Main Logic

This script simulates a complete chargeback analysis workflow
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from resources.chargeback_data import ChargebackDataRepository
from prompts.analysis_prompts import ChargebackAnalysisPrompts
from tools.analysis_tools import RiskScoringEngine, FraudDetectionTool
from agent_core import ChargebackAgent
import json

def demonstrate_ai_agent():
    """Demonstrate the complete AI Agent workflow"""
    
    print("🤖 CHARGEBACK AI AGENT DEMONSTRATION")
    print("=" * 60)
    
    # Initialize the 4-layer architecture
    print("\n1️⃣ INITIALIZING RESOURCES LAYER...")
    data_repo = ChargebackDataRepository()
    
    print("2️⃣ INITIALIZING PROMPTS LAYER...")
    prompts = ChargebackAnalysisPrompts()
    
    print("3️⃣ INITIALIZING TOOLS LAYER...")
    risk_engine = RiskScoringEngine()
    fraud_detector = FraudDetectionTool()
    
    print("4️⃣ INITIALIZING MAIN LOGIC LAYER...")
    agent = ChargebackAgent()
    
    # Test different case types
    test_cases = [
        {
            "case_number": "CD2024001",
            "reason_code": "10.5",
            "card_network": "visa",
            "transaction_amount": 2500.00,
            "merchant_category": "Electronics",
            "customer_history": {"previous_disputes": 0, "credit_score": 780}
        },
        {
            "case_number": "CD2024042", 
            "reason_code": "4808",
            "card_network": "mastercard",
            "transaction_amount": 89.99,
            "merchant_category": "Subscription",
            "customer_history": {"previous_disputes": 2, "credit_score": 620}
        },
        {
            "case_number": "CD2024103",
            "reason_code": "4853",
            "card_network": "mastercard", 
            "transaction_amount": 1200.00,
            "merchant_category": "Travel",
            "customer_history": {"previous_disputes": 1, "credit_score": 750}
        }
    ]
    
    print(f"\n🔍 ANALYZING {len(test_cases)} TEST CASES...")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📋 CASE {i}: {case['case_number']}")
        print("-" * 40)
        
        # Demonstrate each layer in action
        print(f"🎯 Reason Code: {case['reason_code']} ({case['card_network'].upper()})")
        
        # Layer 1: Resources - Route the case
        routing = data_repo.route_dispute_investigation(
            case['reason_code'], 
            case['card_network'], 
            case.get('transaction_context', {})
        )
        print(f"📊 Category: {routing['category']}")
        print(f"👤 Investigation Owner: {routing['owner']}")
        print(f"⚡ Priority: {routing['priority']}")
        print(f"⏰ SLA: {routing['timeline_days']} days")
        
        # Layer 2: Prompts - Generate analysis prompt
        prompt_data = prompts.generate_risk_analysis_prompt(case)
        print(f"🧠 AI Prompt: {prompt_data['content'][:100]}...")
        
        # Layer 3: Tools - Risk analysis
        risk_score = risk_engine.calculate_risk_score(case)
        fraud_result = fraud_detector.analyze_fraud_risk(case)
        
        print(f"🎲 Risk Score: {risk_score}/100")
        print(f"🚨 Fraud Risk Level: {fraud_result['risk_level']}")
        
        # Layer 4: Main Logic - Agent decision
        recommendation = agent.analyze_dispute_case(case)
        print(f"🎯 AI Recommendation: {recommendation['decision'].upper()}")
        print(f"🎯 Confidence: {recommendation['confidence']}%")
        print(f"💡 Reasoning: {recommendation['reasoning'][:100]}...")
        
        if i < len(test_cases):
            print()
    
    print("\n" + "=" * 60)
    print("✅ AI AGENT DEMONSTRATION COMPLETE!")
    print("\n📊 ARCHITECTURE SUMMARY:")
    print("   1️⃣ Resources: Data routing & category management")
    print("   2️⃣ Prompts: AI context generation & formatting") 
    print("   3️⃣ Tools: Specialized analysis algorithms")
    print("   4️⃣ Main Logic: Orchestration & decision making")
    print("\n🚀 Ready for interview demonstration!")

if __name__ == "__main__":
    demonstrate_ai_agent()
