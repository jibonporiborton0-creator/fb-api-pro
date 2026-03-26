import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# প্রক্সি ইউআরএল ফরম্যাট ঠিক করা হয়েছে
PROXY_URL = "http://juelranahfs9-zone-abc-region-OM:kCAB1hppXyT@43.159.29.144:4950"
PROXIES = {
    "http": PROXY_URL,
    "https": PROXY_URL
}

@app.route('/')
def home():
    # প্রক্সি কাজ করছে কি না তা চেক করার জন্য একটি টেস্ট
    try:
        test_res = requests.get("https://ifconfig.me", proxies=PROXIES, timeout=10)
        return f"Server is Running! Proxy IP: {test_res.text}"
    except:
        return "Server is Running, but Proxy is NOT working!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        session.proxies.update(PROXIES)

        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        
        # ১. ফেসবুক লগইন পেজ
        try:
            res1 = session.get("https://m.facebook.com/login.php", headers={"User-Agent": ua}, timeout=15)
        except requests.exceptions.ProxyError:
            return jsonify({"status": "error", "message": "Proxy Rejected Connection!"})
        except Exception:
            return jsonify({"status": "error", "message": "Proxy is too slow or down!"})

        # টোকেন এক্সট্রাকশন
        lsd_match = re.search('name="lsd" value="(.*?)"', res1.text)
        if not lsd_match:
            return jsonify({"status": "error", "message": "Facebook blocked this proxy!"})
            
        lsd = lsd_match.group(1)
        jazoest = re.search('name="jazoest" value="(.*?)"', res1.text).group(1)
        
        payload = {
            'lsd': lsd, 'jazoest': jazoest,
            'email': uid, 'pass': password, 'login': 'Log In'
        }

        # ২. লগইন সাবমিট
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
            return jsonify({"status": "error", "message": "Checkpoint! Approve on FB app."})
        else:
            return jsonify({"status": "error", "message": "Login Failed. ID/Pass incorrect."})

    except Exception as e:
        return jsonify({"status": "error", "message": f"Connection Error: {str(e)[:50]}"})

if __name__ == '__main__':
    app.run()
