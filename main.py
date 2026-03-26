import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

app = Flask(__name__)
CORS(app)

# আপনার নতুন বাংলাদেশ প্রক্সি সেটিংস (Updated)
PROXY_URL = "http://juelranahfs9-zone-abc-region-bd:kCAB1hppXyT@43.159.29.144:4950"
PROXIES = {"http": PROXY_URL, "https": PROXY_URL}

@app.route('/')
def home():
    try:
        # প্রক্সি আইপি চেক করার জন্য টেস্ট রিকোয়েস্ট
        test_res = requests.get("https://ifconfig.me", proxies=PROXIES, timeout=10)
        return f"Server is Running with BD Proxy! Your Proxy IP: {test_res.text}"
    except:
        return "Server is Running, but Proxy Connection Failed!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        if not uid or not password:
            return jsonify({"status": "error", "message": "UID/Pass missing"})

        session = requests.Session()
        # রিট্রাই লজিক (যাতে কানেকশন ড্রপ না হয়)
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        session.proxies.update(PROXIES)

        # হাই-কোয়ালিটি অ্যান্ড্রয়েড হেডার
        headers = {
            'Authority': 'm.facebook.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'bn-BD,bn;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }
        
        # ১. লগইন পেজ থেকে টোকেন সংগ্রহ
        res1 = session.get("https://m.facebook.com/login.php", headers=headers, timeout=20)
        
        lsd = re.search('name="lsd" value="(.*?)"', res1.text)
        jazoest = re.search('name="jazoest" value="(.*?)"', res1.text)
        
        if not lsd:
            return jsonify({"status": "error", "message": "Facebook Blocked! Try rotating proxy IP."})
            
        payload = {
            'lsd': lsd.group(1),
            'jazoest': jazoest.group(1),
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }

        # ২. লগইন সাবমিট
        headers['Origin'] = 'https://m.facebook.com'
        headers['Referer'] = 'https://m.facebook.com/login.php'
        
        response = session.post(
            "https://m.facebook.com/login.php", 
            data=payload, 
            headers=headers,
            allow_redirects=True,
            timeout=25
        )

        cookies = session.cookies.get_dict()
        
        if "c_user" in cookies:
            # সাকসেসফুল হলে সব কুকি সাজানো
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": cookie_str})
        elif "checkpoint" in cookies or "checkpoint" in response.url:
            return jsonify({"status": "error", "message": "Checkpoint! Please approve in FB app."})
        else:
            return jsonify({"status": "error", "message": "Login Failed. Check UID/Pass."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)[:40]}"})

if __name__ == '__main__':
    app.run()
