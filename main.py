import requests
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Server is Running Successfully!"

@app.route('/login', methods=['POST'])
def get_cookie():
    try:
        data = request.json
        uid = data.get('uid')
        password = data.get('password')
        
        session = requests.Session()
        
        # ১. ফেসবুকের মেইন পেজ থেকে ডাটা সংগ্রহ
        headers = {
            'authority': 'm.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        }
        
        response = session.get('https://m.facebook.com/login.php', headers=headers)
        
        # ফেসবুকের হিডেন সিকিউরিটি ফিল্ড খুঁজে বের করা
        lsd = re.search('name="lsd" value="(.*?)"', response.text).group(1)
        jazoest = re.search('name="jazoest" value="(.*?)"', response.text).group(1)
        m_ts = re.search('name="m_ts" value="(.*?)"', response.text).group(1)
        li = re.search('name="li" value="(.*?)"', response.text).group(1)
        
        # ২. লগইন করার আসল ডাটা তৈরি
        login_payload = {
            'lsd': lsd,
            'jazoest': jazoest,
            'm_ts': m_ts,
            'li': li,
            'try_number': '0',
            'unrecognized_tries': '0',
            'email': uid,
            'pass': password,
            'login': 'Log In',
        }
        
        # ৩. লগইন রিকোয়েস্ট পাঠানো
        post_headers = headers.copy()
        post_headers.update({
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://m.facebook.com',
            'referer': 'https://m.facebook.com/login.php',
        })
        
        final_response = session.post('https://m.facebook.com/login.php', data=login_payload, headers=post_headers)
        
        cookies = session.cookies.get_dict()
        
        if 'c_user' in cookies:
            # সাকসেসফুল হলে সব কুকি সাজানো
            cookie_list = [f"{key}={value}" for key, value in cookies.items()]
            full_cookie = "; ".join(cookie_list)
            return jsonify({"status": "success", "cookie": full_cookie})
        
        elif 'checkpoint' in cookies:
            return jsonify({"status": "error", "message": "Checkpoint! Approve on your FB App."})
        
        else:
            return jsonify({"status": "error", "message": "Login Failed. Try again or check Pass."})

    except Exception as e:
        return jsonify({"status": "error", "message": "Connection Error! Try again."})

if __name__ == '__main__':
    app.run()
