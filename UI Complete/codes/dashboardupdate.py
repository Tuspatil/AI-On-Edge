import requests
import json

def update(username):
	params = dict()
	params["username"] = username
	r=requests.post("http://13.68.206.239:5056/req",json=params)
	data=r.json()
	data = json.loads(data)
	send_data=[]
	print('dashboard 2 ',data)
	print(len(data))
	if len(data)==0:
		temp = []
		return temp
	for app in data:
		# print(app)
		app_name=app["appname"]
		for _ in app["data"]:
			# print(_)
			send_data.append([app_name,_["servicename"],_["status"],_["scheduled"],_["serviceid"],app_name+";"+_["serviceid"]])

	return send_data
