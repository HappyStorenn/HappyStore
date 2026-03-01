import time
import requests
import hashlib
import base64
import hmac

def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()

    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')

    return sign

def send_fs_msg(content_str):
    url = "https://open.feishu.cn/open-apis/bot/v2/hook/111111111111"
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        "timestamp": 'str(round(time.time() * 1000)',
        "sign": gen_sign(round(time.time() * 1000),'11111111111111'),
        "msg_type": "text",
        "content": {
                "text": f"<at user_id=\"all\">所有人</at> \n{content_str}"
        }
    }
    res = requests.post(url, json=data, headers=headers)
    return res.text

if __name__ == '__main__':
    print(send_fs_msg())

