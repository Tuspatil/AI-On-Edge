from flask import Flask,request,jsonify
import requests
import sys 
import json
from pymongo import MongoClient

app = Flask(__name__)

#filter sensor incoming request

registry_ip = 'localhost'
registry_port = 27017
collection_name = 'final9'



@app.route('/getsensordata' ,methods=['GET','POST'])
def fun():

	global registry_port
	global registry_ip


	data=request.get_json()
	user_id  = data['username']

	client = MongoClient(registry_ip ,registry_port,maxPoolSize=50)
	db = client[collection_name]
	d = list(db['sensor'].find({}))
	
	for i in d:
		del i['_id']
		del i['data_dump']
		del i['sensor_data_type']
		del i['sensor_host']
	
	return jsonify(d)

if __name__ == '__main__':
   app.run(debug=True,port=sys.argv[1])