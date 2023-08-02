import requests
import json
import time
from flask import Flask, redirect, url_for, render_template, request, session
import logging
from files.midjourney import imagine
from files.discord import attempt_auth, get_dm_channel_id

# init logging
logging.basicConfig(level=logging.NOTSET)




app = Flask(__name__)
app.secret_key = "admin"



@app.route("/auth", methods=["POST"])
def auth():  
  logging.info("/auth POST")

  data = request.form

  email = data.get('email')
  password = data.get('password')
  captcha_key = data.get('h-captcha-response')

  logging.info("Authenticating...")
  res = attempt_auth(email, password, captcha_key)

  logging.critical(res.text)
  logging.info(res.request.body)
  logging.info(res.request.headers)

  if res.status_code == 400:
    # check captcha
    response = json.loads(res.text)
    if "captcha_sitekey" in response:
      logging.error("Captcha Required!")
      captcha_sitekey = response["captcha_sitekey"]
      return redirect(url_for("login",captcha_sitekey=captcha_sitekey, prev_email=email, prev_password=password))

  if res.status_code == 200 or res.status_code == 203:
    response = json.loads(res.text)
    user_id = response['user_id']
    auth_token = response['token']

    session["user_id"] = user_id
    session["auth_token"] = auth_token
    session["midjourney_channel_id"] = get_dm_channel_id(auth_token, "Midjourney Bot")

  return redirect(url_for("index"))


@app.route("/login", methods=["GET"])
def login(): 
  logging.info("In Login Page")

  if "auth_token" in session: return redirect(url_for('index'))

  captcha_sitekey = request.args.get("captcha_sitekey")
  if captcha_sitekey is None:
    logging.info("No Captcha Sitekey!")
    return render_template("login.html")
  
  return render_template("login.html", captcha_sitekey = captcha_sitekey)


@app.route("/logout", methods=["GET"])
def logout():
  # clear user_id
  session.pop("user_id")

  # clear auth_token
  session.pop("auth_token")

  # clear midjourney channel id
  session.pop("midjourney_channel_id")

  return redirect(url_for("login"))

@app.route("/generate", methods=["POST"])
def generate():
  logging.info("/generate")
  # get midjourney channel id
  if "auth_token" not in session: return redirect(url_for('login'))

  data = request.form

  auth_token = session["auth_token"]
  channel_id = session["midjourney_channel_id"]

  prompt = data["prompt"]

  standard_image, upscaled_images = imagine(auth_token, channel_id, prompt)

  return render_template("preview.html", standard_image=standard_image, upscaled_images=upscaled_images)
 



@app.route("/", methods=["GET"])
def index():  
  logging.info("In Index Page")

  if "auth_token" not in session: return redirect(url_for('login'))


  return render_template("index.html")


#auth = get_auth_token("alialhamadani72@gmail.com", "Thorthor11")
#print(auth)
#channel_id = get_dm_channel_id(auth, "Midjourney Bot")
#print(channel_id)
#print(imagine(auth, channel_id, "a man eating lettice"))

if __name__ == "__main__":
  # webbrowser.open('http://127.0.0.1:8000')  # Go to example.com
  # set upload folder
  app.config["SESSION_TYPE"] = 'filesystem'

  # run app
  app.run(port=8000, debug=True)