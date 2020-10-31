from flask import Flask,request,jsonify
import requests
import json

app = Flask(__name__)

@app.route("/getsensordata",methods=['GET','POST'])
def send():
	file=open("response.json","r")
	data=json.load(file)
	# print(data)


	return jsonify(data)

if __name__ == "__main__":        # on running python app.py
    app.run(debug=True,port=5051) 