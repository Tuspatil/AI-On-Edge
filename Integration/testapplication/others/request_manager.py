from flask import Flask,request,jsonify
import requests
import json

def main():

	
	file=open("sensor_registration.json","r")
	data=json.load(file)
	d = {'username':'test1234','config_file':data}
	r=requests.post(url="http://13.68.206.239:5051/sensorregistration",json=d)
	# r=requests.post(url="http://127.0.0.1:9000/temperature1",json = d)
	
	# d = {'username':'ias11'}
	# r=requests.post(url="http://127.0.0.1:5050/getsensordata",json=d)
	# r=requests.post(url="http://127.0.0.1:5000/getsensordata",json=d)
	d = r.json()
	print(d)
	# return 200
	
if __name__ == '__main__':
	main()
