import time
import requests
from files.discord import send_prompt, get_response
from flask import Flask, redirect, url_for, render_template, request, session


def upsample_image(auth_token: str, channel_id: str, message, prompt:str, image_num:int):
  reaction_id = message['components'][0]['components'][image_num-1]['custom_id']

  body = {
    "type": 3,
    "channel_id": channel_id,
    "message_id": message['id'],
    "application_id": "936929561302675456",
    "session_id": "b235755dee34ceba8d7589ceacf61bf9",
    "data": {
        "component_type": 2,
        "custom_id": reaction_id
    }
  }
  headers = {'Authorization': auth_token}
  res = requests.post('https://discord.com/api/v9/interactions', headers=headers, json=body)

  if res.status_code != 204 and res.status_code != 200: raise SystemError("Something went wrong upsampling the image!")

  while True:
    time.sleep(4)
    upsampled_image = get_response(auth_token, channel_id, prompt, f"#{image_num}")
    if "(Waiting to start)" not in upsampled_image['content']: break

  return upsampled_image['attachments'][0]['url']



def imagine(auth_token:str, channel_id:str, prompt:str):
  res = send_prompt(auth_token, channel_id, prompt)
  if res.status_code != 204 and res.status_code != 200: raise SystemError("Something went wrong sending the prompt!")
  while True:
    time.sleep(6)
    pending_message = get_response(auth_token, channel_id, prompt)
    if ("(Waiting to start)" not in pending_message['content']) and ("%" not in pending_message['content']): break
    print(pending_message['content'])
  
  upscaled_images = [upsample_image(auth_token, channel_id, pending_message, prompt, num) for num in range(1,5)]
  
  return pending_message['attachments'][0]['url'], upscaled_images



