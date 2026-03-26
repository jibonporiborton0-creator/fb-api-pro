import requests
import re
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
        test = requests.get("https://api.ipify.org?format=json", proxies=PROXIES, timeout=10)
        return f"Server Active! IP: {test.json()['ip']} (Region: BD)"
    except:
        return "Server Active, but Proxy Error!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        session.proxies.update(PROXIES)

        # ১. প্রথমেই ফেসবুকের মেইন পেজ থেকে সিকিউরিটি কুকি (datr) সংগ্রহ করা
        ua = "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36"
        res_init = session.get("https://m.facebook.com/", headers={"User-Agent": ua}, timeout=15)
        
        # ২. mbasic লগইন পেজে গিয়ে হিডেন টোকেন সংগ্রহ করা
        headers = {
            'authority': 'mbasic.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'bn-BD,bn;q=0.9,en-US;q=0.8,en;q=0.7',
            'user-agent': ua,
        }
        res_login_page = session.get("https://mbasic.facebook.com/login.php", headers=headers)
        
        payload = {'email': uid, 'pass': password, 'login': 'Log In'}
        
        # হিডেন ফিল্ড যেমন lsd, jazoest ইত্যাদি সংগ্রহ
        reg = re.findall(r'name="(.*?)" value="(.*?)"', res_login_page.text)
        for name, value in reg:
            if name not in ['email', 'pass']:
                payload[name] = value

        # ৩. লগইন সাবমিট করা
        response = session.post(
            "https://mbasic.facebook.com/login.php", 
            data=payload, 
            headers=headers, 
            allow_redirects=True,
            timeout=20
        )

        cookies = session.cookies.get_dict()
        
        if "c_user" in cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": cookie_str})
        
        elif "checkpoint" in cookies or "checkpoint" in response.url:
            return jsonify({"status": "error", "message": "Approval needed! Check FB app notifications."})
        
        elif "ভুল" in response.text or "Incorrect" in response.text or "invalid" in response.text:
            return jsonify({"status": "error", "message": "Wrong Password! Double check your pass."})
        
        else:
            return jsonify({"status": "error", "message": "FB Security blocked this attempt. Try again in 5 mins."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Connection slow! Try again."})

if __name__ == '__main__':
    app.run()
