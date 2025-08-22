## 📊 Data Schema & API

### Core Database Models

**DisputeCase**
```python
- id: Primary key
- case_number: Unique identifier (CD2024001)
- category: FRAUD_UNAUTHORIZED, PROCESSING_ISSUES, MERCHANT_MERCHANDISE
- subcategory: 1A_Card_Fraud, 2B_Technical_Processing, etc.
- amount: Transaction amount
- risk_score: AI-calculated risk (0-100)
- ai_recommendation: approve, reject, review, merchant_investigation
- status: pending, analyzing, review, completed
```

**Customer**
```python
- id: Primary key
- credit_score: 300-850 range
- previous_disputes: Historical dispute count
- customer_since: Account creation date
- total_purchase_amount: Lifetime transaction value
```

### API Endpoints

```
GET    /api/disputes              # List all disputes
GET    /api/disputes/{id}         # Get specific dispute
POST   /api/disputes/{id}/analyze # Run AI analysis
POST   /api/disputes/{id}/decide  # Submit human decision
GET    /api/categories/summary    # Category statistics
POST   /api/disputes/{id}/reanalyze # Re-analyze with feedback
```

## ⚙️ Configuration

### Environment Variables
```bash
# Backend Configuration
FLASK_ENV=development
DATABASE_URL=sqlite:///chargeback_agent.db
AI_CONFIDENCE_THRESHOLD=75
RISK_TOLERANCE=moderate

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5002/api
REACT_APP_ENVIRONMENT=development
```

### Risk Threshold Customization
Modify decision thresholds in `backend/config.py`:
```python
RISK_THRESHOLDS = {
    'FRAUD_UNAUTHORIZED': {'approve': 30, 'reject': 70},
    'PROCESSING_ISSUES': {'approve': 40, 'reject': 80},
    'MERCHANT_MERCHANDISE': {'approve': 35, 'reject': 75}
}
```

## 🔧 Development

### Project Structure
```
ai-chargeback-agent/
├── backend/
│   ├── app.py              # Flask application
│   ├── models.py           # Database models
│   ├── analysis_engine.py  # AI risk scoring
│   ├── load_demo_data.py   # Data initialization
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── types/          # TypeScript interfaces
│   │   └── index.css       # Custom styles
│   ├── public/             # Static assets
│   └── package.json        # Node dependencies
└── README.md
```

### Adding New Features

1. **Backend**: Add routes in `app.py`, update models in `models.py`
2. **Frontend**: Create components in `src/components/`, update types in `src/types/`
3. **AI Logic**: Modify analysis algorithms in `analysis_engine.py`
4. **Database**: Create migration scripts for schema changes
