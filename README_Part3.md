## 💻 Usage Guide

### Dashboard Overview
Navigate through four main sections:
1. **Dashboard**: Real-time analytics and case overview
2. **Case Analysis**: Detailed case examination with AI insights
3. **Workflow Design**: Visual workflow creation and management
4. **AI Assistant**: Interactive chat for expert consultation

### Case Analysis Workflow
1. **Select a Case**: Click any case from the dashboard table
2. **Review AI Analysis**: Examine risk score, key factors, and warnings
3. **Check Evidence**: Review transaction details and customer history
4. **Make Decision**: Approve, reject, investigate, or send to merchant
5. **Add Feedback**: Provide expert input to improve AI decisions
6. **Submit Decision**: Finalize case with human decision override

### AI Assistant Features
- Ask questions like "Show me high-risk cases" or "Analyze pending fraud cases"
- Get explanations for AI recommendations
- Request case summaries and trends analysis
- Receive proactive alerts for unusual patterns

## 🧠 AI Decision Logic

### Risk Scoring Methodology

The AI uses a comprehensive 0-100 risk scoring system with category-specific thresholds:

| **Category** | **Approve (≤)** | **Review** | **Reject (≥)** |
|--------------|-----------------|------------|----------------|
| **Fraud & Unauthorized** | 30 | 31-69 | 70 |
| **Processing Issues** | 40 | 41-79 | 80 |
| **Merchandise Issues** | 35 | 36-74* | 75 |

*Merchandise Issues in 36-74 range show "Send for Merchant Investigation"

### Transaction Legitimacy Factors

**For Fraud Cases:**
- Order history links = Suspicious (potential abusive chargeback)
- No history = Consistent with stolen card/identity theft

**For Merchandise/Processing Cases:**
- Order history links = Loyal customer (lower risk)
- No history = New customer (moderate risk)

### Key Risk Factors Analyzed
- **Customer Profile**: Credit score, dispute history, account tenure
- **Transaction Details**: Amount, merchant category, location
- **Evidence Quality**: Completeness and authenticity of documentation
- **Order History**: Same card, address, IP, device usage patterns
- **Temporal Patterns**: Transaction timing and frequency
