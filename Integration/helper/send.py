from flask import Flask,request
import requests
import json

app = Flask(__name__)

@app.route("/send/")
def send():
	file=open("config.json","r")
	data=json.load(file)

	d = {'user_id':'IAS','config_file':data}
	r=requests.post(url="http://127.0.0.1:6060/recv/",json=d)
	return r.json()


if __name__ == "__main__":        # on running python app.py
    send()