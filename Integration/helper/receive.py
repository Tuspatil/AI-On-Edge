from flask import Flask,request,jsonify
import requests
import json

app = Flask(__name__)

@app.route("/recv/",methods=['POST'])
def receive():
	data=request.get_json()
	print(data['user_id'])
	print(data['config_file'])

	return jsonify({"response":"OK"})


if __name__ == "__main__":        # on running python app.py
    app.run(debug=True,port=6060) 