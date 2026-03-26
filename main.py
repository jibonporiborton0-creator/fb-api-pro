from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/login', methods=['POST'])
def get_cookie():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')
        
        if not uid or not password:
            return jsonify({"status": "error", "message": "UID/Pass missing"}), 400

        session = requests.Session()
        headers = {
            'authority': 'm.facebook.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }
        
        # Login Attempt
        session.get("https://m.facebook.com/login.php", headers=headers)
        login_data = {'email': uid, 'pass': password}
        response = session.post("https://m.facebook.com/login.php", data=login_data, headers=headers)
        
        cookies = session.cookies.get_dict()
        if 'c_user' in cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": cookie_str})
        else:
            return jsonify({"status": "error", "message": "Login Failed. Check UID/Pass."})
            
    except Exception as e:
        return jsonify({"status": "error", "message": "Server error. Try again."})

if __name__ == "__main__":
    app.run()
