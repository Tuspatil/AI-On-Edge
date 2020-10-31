from flask import Flask,request,jsonify
import requests
import json

def main():

	
	file=open("config.json","r")
	data=json.load(file)
	d = {'username':'pratik','config_file':data}
	r=requests.post(url="http://127.0.0.1:5050/sensorregistration",json=d)
	
	# d = {'username':'pratik','config_file':data}
	# r=requests.post(url="http://127.0.0.1:5000/getsensordata",json=d)
	# r=requests.post(url="http://127.0.0.1:5000/getsensordata",json=d)
	d = r.json()
	print(d)
	
if __name__ == '__main__':
	main()