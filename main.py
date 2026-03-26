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
            return jsonify({"status": "error", "message": "UID/Pass missing"})

        session = requests.Session()
        # একদম আসল অ্যান্ড্রয়েড ক্রোম ব্রাউজারের ইউজার এজেন্ট
        ua = "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
        
        # ১. লগইন পেজ থেকে টোকেন সংগ্রহ
        res1 = session.get("https://m.facebook.com/login.php", headers={"User-Agent": ua})
        
        payload = {
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }
        
        # ডাইনামিক সিকিউরিটি ফিল্ড খুঁজে বের করা
        hidden_inputs = re.findall(r'input type="hidden" name="(.*?)" value="(.*?)"', res1.text)
        for name, value in hidden_inputs:
            payload[name] = value

        # ২. লগইন রিকোয়েস্ট পাঠানো (রিডাইরেক্ট অ্যালাউ করা হয়েছে)
        headers = {
            "User-Agent": ua,
            "Referer": "https://m.facebook.com/login.php",
            "Origin": "https://m.facebook.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
        }

        # এটি ফেসবুকের সব রিডাইরেক্ট ফলো করবে
        response = session.post(
            "https://m.facebook.com/login.php", 
            data=payload, 
            headers=headers, 
            allow_redirects=True
        )

        # ৩. সব রিডাইরেক্ট শেষ হওয়ার পর কুকি চেক করা
        cookies = session.cookies.get_dict()
        
        if "c_user" in cookies:
            # সব কুকি একত্রে সাজানো
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": cookie_str})
        
        elif "checkpoint" in cookies:
            return jsonify({"status": "error", "message": "Checkpoint! Approve login from your FB app."})
        
        elif "save-device" in response.text or "ok" in response.text:
            # যদি 'Save login info' পেজে আটকে থাকে, তবে সেখান থেকেও কুকি বের করা সম্ভব
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            if "c_user" in cookie_str:
                return jsonify({"status": "success", "cookie": cookie_str})
            else:
                return jsonify({"status": "error", "message": "Approval needed! Check FB app notifications."})
        
        else:
            return jsonify({"status": "error", "message": "Security Block! Try logging in manually on browser first."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Server Busy! Try again later."})

if __name__ == '__main__':
    app.run()
