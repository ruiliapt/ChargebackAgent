#!/bin/bash

echo "🚀 启动智能争议管理系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 需要Python 3.x环境"
    exit 1
fi

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 需要Node.js环境"
    exit 1
fi

# 创建Python虚拟环境（如果不存在）
if [ ! -d "backend/venv" ]; then
    echo "📦 创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# 激活虚拟环境并安装依赖
echo "📦 安装后端依赖..."
cd backend
source venv/bin/activate
pip install -r requirements.txt
cd ..

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 初始化数据库
echo "🗄️ 初始化数据库..."
cd backend
source venv/bin/activate
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('数据库初始化完成')
"
cd ..

echo "✅ 安装完成！"
echo ""
echo "🎯 启动说明:"
echo "1. 启动后端服务: cd backend && source venv/bin/activate && python app.py"
echo "2. 启动前端服务: cd frontend && npm start"
echo "3. 访问应用: http://localhost:3000"
echo ""
echo "💡 演示数据初始化: 访问 http://localhost:5000/api/init-demo-data (POST请求)"

