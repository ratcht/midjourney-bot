import json
import requests
import logging
from flask import Flask, redirect, url_for, render_template, request, session

logging.basicConfig(level=logging.NOTSET)


def attempt_auth(email:str, password:str, captcha_key: str|None):
  body = {
    "gift_code_sku_id": None,
    "login": email,
    "login_source": None,
    "password": password,
    "undelete": "false"

  }

  headers = {}
  if captcha_key:
    logging.info("Captcha key exists!")
    body["captcha_key"] = captcha_key
    headers['X-Captcha-Key'] = captcha_key

  res = requests.post("https://discord.com/api/v9/auth/login", json=body, headers=headers)
  logging.info(res.status_code)
  return res



def get_messages(auth_token: str, channel_id: str):
  headers = {'Authorization': auth_token}
  messages = requests.get(f'https://discord.com/api/v9/channels/{channel_id}/messages', headers=headers)

  return json.loads(messages.text)


def get_response(auth_token: str, channel_id:str, prompt: str, optional_check:str = ""):
  messages = get_messages(auth_token, channel_id)
  for message in messages:
    content = message['content']
    if prompt in content and optional_check in content: return message
  
  raise Exception("Message not found...")


def send_prompt(auth_token:str, channel_id:str, prompt:str):
  body = {
    "type": 2,
    "application_id": "936929561302675456",
    "channel_id": channel_id,
    "session_id": "18522fab02189be9d40f102fd074be2b",
    "data": {
        "version": "1118961510123847772",
        "id": "938956540159881230",
        "name": "imagine",
        "type": 1,
        "options": [
            {
                "type": 3,
                "name": "prompt",
                "value": prompt
            }
        ]
    }
  }
  headers = {'Authorization': auth_token}
  res = requests.post('https://discord.com/api/v9/interactions', headers=headers, json=body)

  return res




def get_dm_channel_id(auth_token:str, recipient:str):
  headers = {'Authorization': auth_token}
  res = requests.get("https://discord.com/api/v9/users/@me/channels", headers = headers)
  if res.status_code != 200: raise LookupError("Error fetching channels...")

  channels = json.loads(res.text)

  for channel in channels:
    if channel["type"] != 1: continue
    if channel["recipients"][0]["username"] != recipient: continue

    return channel["id"]
  
  raise KeyError("Couldn't find user")