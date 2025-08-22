import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chargeback_agent.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI/LLM配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # 外部API配置
    MERCHANT_VERIFICATION_API_KEY = os.environ.get('MERCHANT_VERIFICATION_API_KEY')
    FRAUD_DATABASE_API_KEY = os.environ.get('FRAUD_DATABASE_API_KEY')
    GEOLOCATION_API_KEY = os.environ.get('GEOLOCATION_API_KEY')
    
    # 业务规则配置
    RISK_THRESHOLDS = {
        'low': 30,
        'medium': 70,
        'high': 100
    }
    
    # 自动决策规则
    AUTO_APPROVE_THRESHOLD = 25
    AUTO_REJECT_THRESHOLD = 85
    
    # 系统配置
    MAX_DISPUTES_PER_PAGE = 50
    ANALYSIS_TIMEOUT_SECONDS = 30

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
    'default': DevelopmentConfig
}

