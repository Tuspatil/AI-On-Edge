from flask import Flask,request,Response
import requests
import json
import threading
import paramiko
import argparse
import time
import sys
app = Flask(__name__)

testing_new_machine  = False
lock_load = threading.Lock()
lock_allocate = threading.Lock()

service_life_cycle_ip = "127.0.0.1"
service_life_cycle_port = 8080 
monitoring_ip = "127.0.0.1"
monitoring_port = 5055

# @app.route("/serverlcm/check/<username>")
# def test(username):
# 	ip,port=GetDetails(service_life_cycle_ip,service_life_cycle_port,username)
# 	print((ip,port))
# 	return (ip,port)

def GetDetails(service_life_cycle_ip,service_life_cycle_port,username):
	res=requests.get('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/servicelcm/service/topology/'+username)
	data=res.json()[0]
	return data["ip"],data["port"]

def load_balance():
	lock_load.acquire()
	# monitoring_ip,monitoring_port=GetDetails(service_life_cycle_ip,service_life_cycle_port,"monitoring")
	res=requests.get('http://'+monitoring_ip+':'+str(monitoring_port)+'/monitoring/getLoad')
	data=res.json()
	loads=[]

	for i in range(data["n_servers"]):
		if(data["server_load"][i]["load_average_1"]/data["server_load"][i]["n_cores"] >= 0.8 or data["server_load"][i]["load_average_5"]/data["server_load"][i]["n_cores"] >= 0.7):
			continue
		coeff1=1/((3/data["server_load"][i]["free_cpu"])+(1/data["server_load"][i]["free_mem"]))
		coeff2=data["server_load"][i]["number_of_events_per_sec"]/10000 + min(2,data["server_load"][i]["free_RAM"])
		coeff3=1 if data["server_load"][i]["temperature"] < 70 else 0
		coeff=coeff1*coeff2*coeff3
		loads.append((coeff,data["server_load"][i]["ip"],data["server_load"][i]["port"],data["server_load"][i]["username"],data["server_load"][i]["password"]))

	if(len(loads)==0):
		lock_load.release()
		return "NO MACHINE","","","",""
	else:
		# print(loads)
		loads.sort(key = lambda x:x[0],reverse=True)
		# print(loads)
		lock_load.release()
		return "OK",loads[0][1],loads[0][3],loads[0][4],loads[0][2]

def setup_new_machine(ip,username,password,port):
	print("setup_new_machine")
	ssh_client =paramiko.SSHClient()
	ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh_client.connect(hostname=ip,username=username,password=password)
	ftp_client=ssh_client.open_sftp()
	ftp_client.put("code/ma.py","ma.py");
	ftp_client.close()
	ssh_client.exec_command("python3 ma.py "+str(ip)+" "+str(port)+" "+username+" "+password)
	ssh_client.close()
	
def allocate_new_machine():
	lock_allocate.acquire()
	result,ip,username,password="","","",""
	file=open("freelist.json")
	free_list=json.load(file)
	if( len(free_list["Servers"])==0):
		result = "NO MACHINE"
	else:
		result = "OK"
		ip = free_list["Servers"][0]["ip"]
		username = free_list["Servers"][0]["username"]
		password = free_list["Servers"][0]["password"]
		port = free_list["Servers"][0]["port"]
		setup_new_machine(ip,username,password,port)
		del free_list["Servers"][0]
		file.close()
		file=open("freelist.json","w")
		# file.write(json.dumps(free_list))
		# print(free_list)
		json.dump(free_list,file)
		file.close()
	lock_allocate.release()
	return result,ip,username,password,port

def allocate_server_kernel(serviceid):
	global testing_new_machine
	result,ip,username,password,port = load_balance()
	print("Result: {}".format(result))
	if(testing_new_machine or result=="NO MACHINE"):
		print("allocate new machine")
		result,ip,username,password,port = allocate_new_machine()

	data={"result":result,"serviceid": serviceid,"serverip":ip,"machineusername":username,"password":password,"sshPort":port}

# 	data={"result":"ok","serviceid": serviceid,"serverip":"13.68.206.239","machineusername":"ias","password":"Asdfghjkl@123","sshPort":"22"}
	print(data)
	r=requests.post(url="http://"+service_life_cycle_ip+":"+str(service_life_cycle_port)+"/servicelcm/service/update",json=data)
	# print(r.json())


@app.route("/serverlcm/allocate_server/<serviceid>")
def allocate_server(serviceid):
	_=threading.Thread(target=allocate_server_kernel,args=(serviceid,))
	_.start()

	data={"status":"ok"}
	resp = Response(json.dumps(data), status=200, mimetype='application/json')
	return resp

if __name__ == "__main__":        # on running python app.py
	# ap = argparse.ArgumentParser()
	# ap.add_argument("-a","--service_life_cycle_ip",required=True)
	# ap.add_argument("-b","--service_life_cycle_port",required=True)
	# ap.add_argument("-c","--monitoring_ip",required=True)
	# ap.add_argument("-d","--monitoring_port",required=True)
	# args = vars(ap.parse_args())          
	# service_life_cycle_ip = args["service_life_cycle_ip"]
	# service_life_cycle_port = int(args["service_life_cycle_port"])
	# monitoring_ip = args["monitoring_ip"]
	# monitoring_port = int(args["monitoring_port"])
	app.run(debug=True,host="0.0.0.0",port=int(5054)) 
