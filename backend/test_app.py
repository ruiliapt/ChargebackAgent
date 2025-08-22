from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/health')
def health():
    return {'status': 'ok'}

@app.route('/api/disputes')
def disputes():
    return {'success': True, 'data': [{'id': 'test', 'case_number': 'TEST001'}]}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
