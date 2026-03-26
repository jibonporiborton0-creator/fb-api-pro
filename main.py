from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re

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
        
        session = requests.Session()
        headers = {
            'authority': 'm.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://m.facebook.com',
            'referer': 'https://m.facebook.com/login.php',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        }
        
        # Initial access to get hidden fields
        res = session.get("https://m.facebook.com/login.php", headers=headers)
        lsd = re.search('name="lsd" value="(.*?)"', res.text).group(1)
        jazoest = re.search('name="jazoest" value="(.*?)"', res.text).group(1)
        m_ts = re.search('name="m_ts" value="(.*?)"', res.text).group(1)
        li = re.search('name="li" value="(.*?)"', res.text).group(1)
        
        login_data = {
            'lsd': lsd, 'jazoest': jazoest, 'm_ts': m_ts, 'li': li,
            'try_number': '0', 'unrecognized_tries': '0',
            'email': uid, 'pass': password, 'login': 'Log In'
        }
        
        response = session.post("https://m.facebook.com/login.php", data=login_data, headers=headers)
        
        cookies = session.cookies.get_dict()
        if 'c_user' in cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": cookie_str})
        elif 'checkpoint' in cookies:
            return jsonify({"status": "error", "message": "Checkpoint! Please approve on FB app."})
        else:
            return jsonify({"status": "error", "message": "Login Failed. Check UID/Pass."})
            
    except Exception as e:
        return jsonify({"status": "error", "message": "Server error. Try again."})

if __name__ == "__main__":
    app.run()
