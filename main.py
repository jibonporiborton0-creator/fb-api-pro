import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# আপনার প্রক্সি সেটিংস (স্ক্রিনশট অনুযায়ী)
PROXIES = {
    "http": "http://juelranahfs9-zone-abc-region-OM:kCAB1hppXyT@43.159.29.144:4950",
    "https": "http://juelranahfs9-zone-abc-region-OM:kCAB1hppXyT@43.159.29.144:4950"
}

@app.route('/')
def home():
    return "Server is Running with Proxy!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        # প্রক্সি কানেক্ট করা
        session.proxies.update(PROXIES)

        ua = "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
        
        # ১. লগইন পেজ ভিজিট
        res1 = session.get("https://m.facebook.com/login.php", headers={"User-Agent": ua}, timeout=20)
        
        # টোকেন সংগ্রহ
        lsd = re.search('name="lsd" value="(.*?)"', res1.text).group(1)
        jazoest = re.search('name="jazoest" value="(.*?)"', res1.text).group(1)
        
        payload = {
            'lsd': lsd, 'jazoest': jazoest,
            'email': uid, 'pass': password, 'login': 'Log In'
        }

        # ২. লগইন রিকোয়েস্ট পাঠানো
        response = session.post(
            "https://m.facebook.com/login.php", 
            data=payload, 
            headers={"User-Agent": ua, "Referer": "https://m.facebook.com/login.php"},
            allow_redirects=True,
            timeout=20
        )

        cookies = session.cookies.get_dict()
        
        if "c_user" in cookies:
            full_cookie = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": full_cookie})
        
        elif "checkpoint" in cookies:
            return jsonify({"status": "error", "message": "Checkpoint! Approve login on your FB app."})
        
        else:
            return jsonify({"status": "error", "message": "Login Failed. Check UID/Pass or Proxy Error."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Proxy Connection Error! Try again."})

if __name__ == '__main__':
    app.run()
