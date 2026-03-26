import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server is Running!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        if not uid or not password:
            return jsonify({"status": "error", "message": "UID and Pass required"})

        session = requests.Session()
        # উন্নত মোবাইল ইউজার এজেন্ট
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        
        # ১. লগইন পেজ থেকে টোকেন সংগ্রহ
        response1 = session.get("https://m.facebook.com/login.php", headers={"User-Agent": ua})
        
        # পেজের সব হিডেন ইনপুট ফিল্ড স্বয়ংক্রিয়ভাবে খুঁজে বের করা
        payload = {
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }
        
        # Regex দিয়ে সব সিকিউরিটি টোকেন খুঁজে বের করা (lsd, jazoest, ইত্যাদি)
        hidden_inputs = re.findall(r'input type="hidden" name="(.*?)" value="(.*?)"', response1.text)
        for name, value in hidden_inputs:
            payload[name] = value

        # ২. লগইন রিকোয়েস্ট পাঠানো
        response2 = session.post(
            "https://m.facebook.com/login.php", 
            data=payload, 
            headers={
                "User-Agent": ua,
                "Referer": "https://m.facebook.com/login.php",
                "Origin": "https://m.facebook.com",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        cookies = session.cookies.get_dict()
        
        # ৩. রেজাল্ট চেক করা
        if "c_user" in cookies:
            full_cookie = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": full_cookie})
        elif "checkpoint" in cookies:
            return jsonify({"status": "error", "message": "Checkpoint! Approve in FB App."})
        else:
            return jsonify({"status": "error", "message": "Login failed! Incorrect UID/Pass."})

    except Exception as e:
        # কোনো সমস্যা হলে এরর মেসেজ দেখাবে
        return jsonify({"status": "error", "message": "Server busy! Try again."})

if __name__ == '__main__':
    app.run()
