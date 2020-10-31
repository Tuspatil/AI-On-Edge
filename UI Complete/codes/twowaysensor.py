import requests
import json

def getsensordata(username):
    d = {'username': username}
    sensordetail = []
    r=requests.post(url="http://13.68.206.239:5050/getsensordata",json=d)
    
    data = r.json()
    for i in data:
    	l = i.keys()
    	if('api' in l):
    		sensordetail.append(i['sensor_name'])

    return sensordetail

def getoutput(sensorname,querytype):
	d = {'value': querytype}
	api = "http://13.68.206.239:9000/temperature1"
	r=requests.post(url=api,json=d)

	data = r.json()
	return data['value']