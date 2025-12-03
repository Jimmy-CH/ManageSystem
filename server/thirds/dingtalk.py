import requests
import time
from functools import wraps
from django.conf import settings

__all__ = ['ding', 'DingTalkAPI']


class DingTalkAPI:
    def __init__(self, agent_id, app_key, app_secret):
        self.agent_id = agent_id
        self.app_key = app_key
        self.app_secret = app_secret
        self.access_token = None
        self.token_expiry = 0

    def get_access_token(self):
        if self.access_token is None or time.time() > self.token_expiry:
            url = f'{settings.DING_URL}/gettoken'
            params = {
                'appkey': self.app_key,
                'appsecret': self.app_secret
            }
            response = requests.get(url, params=params)
            data = response.json()
            if data['errcode'] == 0:
                self.access_token = data['access_token']
                self.token_expiry = time.time() + data['expires_in'] - 60  # 提前60秒更新token
                print('self.access_token:', self.access_token)
            else:
                raise Exception(f'Failed to get access token: {data["errmsg"]}')
        return self.access_token

    def ensure_access_token(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            self.get_access_token()
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def user_or_group(recipient_type, recipient_id, payload):
        if recipient_type == 'user':
            payload['userid_list'] = recipient_id
        elif recipient_type == 'group':
            payload['chatid'] = recipient_id
        else:
            raise ValueError("Invalid recipient_type. Must be 'user' or 'group'.")

    @ensure_access_token
    def send_text_message(self, recipient_id, content, recipient_type='user'):
        """
        给用户或者群发送普通消息
        """
        url = f'{settings.DING_URL}/topapi/message/corpconversation/asyncsend_v2?access_token={self.access_token}'
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            'agent_id': self.agent_id,
            'chatid': recipient_id,
            'msg': {
                'msgtype': 'text',
                'text': {
                    'content': content
                }
            }
        }
        self.user_or_group(recipient_type, recipient_id, payload)

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data['errcode'] != 0:
            raise Exception(f'Failed to send message: {data["errmsg"]}')
        return data

    @ensure_access_token
    def send_markdown_message(self, title, text, recipient_id, recipient_type='user'):
        """
        发送markdown格式普通消息(标题+内容)
        """
        url = f'{settings.DING_URL}/topapi/message/corpconversation/asyncsend_v2?access_token={self.access_token}'
        headers = {
            'Content-Type': 'application/json'
        }
        markdown = {
            'title': title,
            'text': text
        }
        payload = {
            'agent_id': self.agent_id,
            'msg': {'msgtype': 'markdown', 'markdown': markdown},
        }
        self.user_or_group(recipient_type, recipient_id, payload)

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data['errcode'] != 0:
            raise Exception(f'Failed to send message: {data["errmsg"]}')
        return data

    @ensure_access_token
    def send_card_message(self, title, content, recipient_id, recipient_type='user', single_url=None,
                          single_title=None):
        """
        发送卡片消息给用户或者给群
        """
        url = f'{settings.DING_URL}/topapi/message/corpconversation/asyncsend_v2?access_token={self.access_token}'
        headers = {
            'Content-Type': 'application/json'
        }
        action_card = {
            'title': title,
            'markdown': content,
        }
        if single_url and single_title:
            action_card['single_title'] = single_title
            action_card['single_url'] = single_url
        payload = {
            'agent_id': self.agent_id,

            'msg': {
                'msgtype': 'action_card',
                'action_card': action_card
            }
        }
        self.user_or_group(recipient_type, recipient_id, payload)
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        if data['errcode'] != 0:
            raise Exception(f'Failed to send message: {data["errmsg"]}')
        return data

    @staticmethod
    def send_robot_action_card_message(webhook_access_token, action_card_template):
        """
        通过机器人发送actionCard消息
        """
        headers = {
            'Content-Type': 'application/json'
        }
        payload = {
            'msgtype': 'actionCard',
            "actionCard": action_card_template
        }
        webhook_url = f'https://oapi.dingtalk.com/robot/send?access_token={webhook_access_token}'
        response = requests.post(webhook_url, json=payload, headers=headers)
        data = response.json()
        if data['errcode'] != 0:
            raise Exception(f'Failed to send message: {data["errmsg"]}')
        return data


ding = DingTalkAPI(
    agent_id=settings.DING_AGENT_ID,
    app_key=settings.DING_APP_KEY,
    app_secret=settings.DING_APP_SECRET
)
