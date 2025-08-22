## 🏗️ Architecture & Technology Stack

### Frontend
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for responsive, modern UI design
- **Recharts** for interactive data visualizations
- **React Hooks** for state management and side effects

### Backend
- **Flask** web framework with Python 3.8+
- **SQLAlchemy** ORM for database operations
- **SQLite** (development) / **PostgreSQL** (production)
- **Flask-CORS** for cross-origin resource sharing

### AI Engine
- **Custom Risk Scoring Algorithms** with category-aware logic
- **Transaction Pattern Analysis** for legitimacy assessment
- **Machine Learning Features** for continuous improvement
- **Confidence Scoring** for decision reliability

### Data & APIs
- **RESTful API** design with JSON data exchange
- **Real-time Updates** for case status changes
- **Batch Processing** for large-scale data imports
- **Integration-ready** for payment processor APIs

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** 16+ and npm
- **Python** 3.8+ and pip
- **Git** for version control

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/your-org/ai-chargeback-agent.git
cd ai-chargeback-agent
```

2. **Set Up Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Set Up Frontend**
```bash
cd frontend
npm install
```

4. **Initialize Database**
```bash
cd backend
python load_demo_data.py
```

5. **Start the Application**

Backend (Terminal 1):
```bash
cd backend
source venv/bin/activate
python app.py
```

Frontend (Terminal 2):
```bash
cd frontend
npm start
```

6. **Access the Application**
- Open your browser to `http://localhost:3000`
- Backend API runs on `http://localhost:5002`
