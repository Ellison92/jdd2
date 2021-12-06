import requests,time
from uuid import uuid4
from urllib.parse import quote
from random import randint, random, choices
from utils.toutiao_sdk import cbc_encrypt, cbc_decrypt, create_key_iv, md5


class TouTiao:

    def __init__(self, mobile):
        super(TouTiao, self).__init__()
        self.mobile = mobile
        self.timestamp=int(time.time() * 1000)
        self.flushTime=time.sleep
        self.session = requests.Session()
        self.session.headers = requests.structures.CaseInsensitiveDict({
            "content-type": "application/json; charset=utf-8",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/3.9.1",
        })

    def getDeviceId(self):
        value = '86' + ''.join(choices('0123456789', k=12))
        sum_ = 0
        parity = 1
        for i, digit in enumerate([int(x) for x in value]):
            if i % 2 == parity:
                digit *= 2
                if digit > 9:
                    digit -= 9
            sum_ += digit
        value += str((10 - sum_ % 10) % 10)
        return value

    def getMac(self):
        return ':'.join([''.join(choices('0123456789ABCDE', k=2)) for _ in range(6)])

    def reward(self, options, retry=2):
        # 避免出现orderId相同
        orderId = md5(str(self.timestamp) + self.mobile + uuid4().hex)
        print(orderId)
        media_extra = [
            options.get('ecs_token', ''),
            self.mobile,
            'android',
            options.get('arguments1', ''),
            options.get('arguments2', ''),
            orderId,
            str(options.get('codeId', '')),
            options['remark'],
            'Wifi'  # 4G / Wifi
        ]
        duration = randint(28000, 30000) / 1000
        uuid_ = self.getDeviceId()
        message = {
            "oversea_version_type": 0,
            "reward_name": options['channelName'],
            "reward_amount": 1,
            "network": 4,  # 4 / 5 (Wifi / 4G)
            "sdk_version": "4.0.1.9",
            "user_agent": "Mozilla/5.0 (Linux; Android 8.1.0; MI 8 SE Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36",
            "extra": {
                "ad_slot_type": 7,
                "oaid": "",
                "language": "golang",
                "ug_creative_id": "",
                "ad_id": None,
                "creative_id": None,
                "convert_id": None,
                "uid": None,
                "ad_type": None,
                "pricing": None,
                "ut": 12,
                "version_code": "8.9.2",
                "device_id": None,
                "width": 360,
                "height": 705,
                "mac": self.getMac(),
                "uuid": uuid_,
                "uuid_md5": md5(uuid_),
                "os": "android",
                "client_ip": "",
                "open_udid": "",
                "os_type": None,
                "app_name": "中国联通APP",
                "device_type": "MI 8 SE",
                "os_version": "8.1.0",
                "app_id": "5049584",
                "template_id": 0,
                "template_rate": 0,
                "promotion_type": 0,
                "img_gen_type": 0,
                "img_md5": "",
                "source_type": None,
                "pack_time": round(self.timestamp / 1000 + random(), 6),
                "cid": None,
                "interaction_type": 4,
                "src_type": "app",
                "package_name": "com.sinovatech.unicom.ui",
                "pos": 5,
                "landing_type": None,
                "is_sdk": True,
                "is_dsp_ad": None,
                "imei": "",
                "req_id": "",
                "rit": int(options.get('codeId', 0)),
                "vid": "",
                "orit": 900000000,
                "ad_price": "",
                "shadow_ad_id": None,
                "shadow_creative_id": None,
                "shadow_advertiser_id": None,
                "shadow_campaign_id": None,
                "dynamic_ptpl_id": None,
                "engine_external_url": "",
                "engine_web_url": "",
                "variation_id": "",
                "app_bundle_id": "com.sinovatech.unicom.ui",
                "applog_did": "",
                "ad_site_id": "",
                "ad_site_type": 1,
                "clickid": "",
                "global_did": None,
                "ip": "",
                "ua": "Mozilla/5.0 (Linux; Android 8.1.0; MI 8 SE Build/OPM1.171019.019; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/68.0.3440.91 Mobile Safari/537.36",
                "sys_language": "zh-CN",
                "playable_var_ids": "",
                "playable_template_var_id": 0,
                "country_id": None,
                "province_id": None,
                "city_id": None,
                "dma_id": None,
                "playable_url": None,
                "dco_pl_strategy": None,
                "dy_pl_type": None
            },
            "media_extra": quote('|'.join(media_extra)),
            "video_duration": duration,
            "play_start_ts": int(self.timestamp / 1000) - randint(30, 35),
            "play_end_ts": 0,
            "duration": int(duration * 1000),
            "user_id": "5049584",
            "trans_id": uuid4().hex,
            "latitude": 0,
            "longitude": 0
        }
        key, iv = create_key_iv()
        message = cbc_encrypt(message, key, iv)
        data = {
            'message': message,
            'cypher': 3
        }
        self.flushTime(randint(1, 5))
        url = 'https://api-access.pangolin-sdk-toutiao.com/api/ad/union/sdk/reward_video/reward/'
        resp = self.session.post(url=url, json=data)
        resp.encoding = 'utf8'
        data = resp.json()
        message = {}
        if data.get('message', False):
            try:
                message = cbc_decrypt(data['message'])
                print(message)
            except:
                pass
        print(data)
        if not message.get('verify', False) and retry > 0:
            self.flushTime(randint(1, 5))
            return self.reward(options, retry - 1)
        return orderId


if __name__ == '__main__':
    pass
