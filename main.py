import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "API is Running!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        # লেটেস্ট গুগল পিক্সেল ফোনের ইউজার এজেন্ট (ফেসবুক এটিকে সহজে ব্লক করে না)
        ua = "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
        
        # ১. লগইন পেজ এক্সেস
        res1 = session.get("https://m.facebook.com/login.php", headers={"User-Agent": ua})
        
        # সব সিকিউরিটি টোকেন সংগ্রহ
        lsd = re.search('name="lsd" value="(.*?)"', res1.text).group(1)
        jazoest = re.search('name="jazoest" value="(.*?)"', res1.text).group(1)
        m_ts = re.search('name="m_ts" value="(.*?)"', res1.text).group(1)
        li = re.search('name="li" value="(.*?)"', res1.text).group(1)

        payload = {
            'lsd': lsd, 'jazoest': jazoest, 'm_ts': m_ts, 'li': li,
            'email': uid, 'pass': password, 'login': 'Log In'
        }

        # ২. ফেসবুকের মেইন লগইন রিকোয়েস্ট
        login_headers = {
            "User-Agent": ua,
            "Referer": "https://m.facebook.com/login.php",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        }

        response = session.post(
            "https://m.facebook.com/login.php", 
            data=payload, 
            headers=login_headers, 
            allow_redirects=True
        )

        cookies = session.cookies.get_dict()
        
        if "c_user" in cookies:
            full_cookie = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": full_cookie})
        
        elif "checkpoint" in cookies or "checkpoint" in response.url:
            return jsonify({"status": "error", "message": "Approval needed! Approve from your FB app now."})
        
        else:
            return jsonify({"status": "error", "message": "Security Gate! Please login once on Chrome and click 'Save Info'."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Server error. Try again."})

if __name__ == '__main__':
    app.run()
