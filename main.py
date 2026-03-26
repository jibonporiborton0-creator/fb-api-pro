import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# আপনার প্রক্সি
PROXY = "http://juelranahfs9-zone-abc-region-bd:kCAB1hppXyT@43.159.29.144:4950"

@app.route('/')
def home():
    return "Server is Ready!"

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')

        session = requests.Session()
        session.proxies = {"http": PROXY, "https": PROXY}
        
        # ১. ফেসবুকের কাছে যাওয়ার জন্য একটি সুন্দর সাজ (User Agent)
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        
        # ২. ফেসবুকের মেইন দরজায় নক করা
        head = {"User-Agent": ua, "Accept-Language": "bn-BD,bn;q=0.9,en-US;q=0.8"}
        res1 = session.get("https://mbasic.facebook.com/login.php", headers=head, timeout=15)
        
        # ৩. হিডেন টোকেনগুলো সংগ্রহ করা
        payload = {'email': uid, 'pass': password, 'login': 'Log In'}
        reg = re.findall(r'name="(.*?)" value="(.*?)"', res1.text)
        for name, value in reg:
            if name not in ['email', 'pass']: payload[name] = value

        # ৪. আসল লগইন রিকোয়েস্ট পাঠানো
        res2 = session.post("https://mbasic.facebook.com/login.php", data=payload, headers=head, allow_redirects=True)

        # ৫. ফলাফল চেক করা
        cookies = session.cookies.get_dict()
        if "c_user" in cookies:
            c_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return jsonify({"status": "success", "cookie": c_str})
        elif "checkpoint" in cookies:
            return jsonify({"status": "error", "message": "Go to FB App and click 'Yes, It was me'."})
        else:
            return jsonify({"status": "error", "message": "Failed! Open FB App and Approve Login."})

    except:
        return jsonify({"status": "error", "message": "Connection Error! Wait 2 mins."})

if __name__ == '__main__':
    app.run()
