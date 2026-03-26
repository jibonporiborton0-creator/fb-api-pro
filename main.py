import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Master API is Running (No Proxy)!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        
        # ১. ফেসবুকের মেইন পেজে যাওয়া
        head = {"User-Agent": ua}
        res1 = session.get("https://mbasic.facebook.com/login.php", headers=head, timeout=15)
        
        # হিডেন সিকিউরিটি টোকেন সংগ্রহ
        payload = {'email': uid, 'pass': password, 'login': 'Log In'}
        reg = re.findall(r'name="(.*?)" value="(.*?)"', res1.text)
        for name, value in reg:
            if name not in ['email', 'pass']: payload[name] = value

        # ২. সরাসরি লগইন রিকোয়েস্ট (কোনো প্রক্সি ছাড়াই)
        res2 = session.post("https://mbasic.facebook.com/login.php", data=payload, headers=head, allow_redirects=True)

        cookies = session.cookies.get_dict()
        if "c_user" in cookies:
            c_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": c_str})
        else:
            return jsonify({"status": "error", "message": "Checkpoint or Login Error"})

    except:
        return jsonify({"status": "error", "message": "Server Busy"})

if __name__ == '__main__':
    app.run()
