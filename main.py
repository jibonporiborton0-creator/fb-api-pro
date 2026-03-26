import requests
import re
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# আপনার প্রক্সি সেটিংস
PROXY_URL = "http://juelranahfs9-zone-abc-region-bd:kCAB1hppXyT@43.159.29.144:4950"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

@app.route('/')
def home():
    try:
        test_res = requests.get("https://api.ipify.org?format=json", proxies=PROXIES, timeout=10)
        return f"Server Active! IP: {test_res.json()['ip']} (Region: BD)"
    except:
        return "Server Active, but Proxy Connection Failed!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        session.proxies.update(PROXIES)

        # হাই-কোয়ালিটি রিয়েল ইউজার এজেন্ট
        ua = "Mozilla/5.0 (Linux; Android 12; Pixel 6 Build/SD1A.210817.036; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.115;]"
        
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'bn-BD,bn;q=0.9,en-US;q=0.8,en;q=0.7',
            'origin': 'https://mbasic.facebook.com',
            'referer': 'https://mbasic.facebook.com/login.php',
            'user-agent': ua,
        }

        # ১. mbasic লগইন পেজ ভিজিট করা
        res1 = session.get("https://mbasic.facebook.com/login.php", headers=headers, timeout=15)
        
        # সব হিডেন ফিল্ড অটোমেটিক খুঁজে বের করা
        payload = {
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }
        
        # Regex দিয়ে সব সিকিউরিটি ফিল্ড (lsd, jazoest, etc) সংগ্রহ
        reg = re.findall(r'name="(.*?)" value="(.*?)"', res1.text)
        for name, value in reg:
            if name not in ['email', 'pass']:
                payload[name] = value

        # ২. লগইন সাবমিট করা
        response = session.post(
            "https://mbasic.facebook.com/login.php", 
            data=payload, 
            headers=headers, 
            allow_redirects=True,
            timeout=20
        )

        cookies = session.cookies.get_dict()
        
        if "c_user" in cookies:
            # সাকসেসফুলি কুকি পাওয়া গেলে সাজানো
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": cookie_str})
        elif "checkpoint" in cookies or "checkpoint" in response.url:
            return jsonify({"status": "error", "message": "Checkpoint! Approve in FB app."})
        else:
            # যদি ব্লক করে, তবে মেইন সাইটে মেসেজ কি আছে চেক করা
            if "blocked" in response.text.lower() or "suspicious" in response.text.lower():
                return jsonify({"status": "error", "message": "Facebook Blocked Proxy! Change Proxy IP."})
            return jsonify({"status": "error", "message": "Incorrect Password or Locked ID."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Connection slow! Try again."})

if __name__ == '__main__':
    app.run()
