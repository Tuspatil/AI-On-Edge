import flask
import threading
import requests
import json
import sshclient
import deployer_helper
from flask import request
from pathlib import Path

def req_handler(app,port):
	@app.route('/deployment/dodeploy', methods=['POST'])
	def dodeploy():
		try :
			req = request.get_json()
			print(req)
			ip = req["serverip"]
			sshport = req['sshPort']
			machine_username = req['machineusername']
			machine_password = req['password']
			serviceid = req['serviceid']
			username = req['username']
			application_name = req['applicationname']
			service_name = req['servicename']

			if username != 'admin':
				config_path = '/userservice/'+ username + '/' + application_name + '/config.json'
				filename = deployer_helper.getFileName(config_path, service_name)			
				smres = deployer_helper.getSensorTopic(username,application_name,service_name,serviceid,config_path)
				deployer_helper.notifyActionManager(username,application_name,service_name,serviceid,config_path,smres['sensor_host'])
				sensortopic = smres['temporary_topic']			
				print("Returned Sensor topic by sensor manager is ",sensortopic)
				deployer_helper.generateDokerFile(config_path, service_name, sensortopic, serviceid)			
				file_path = '/userservice/'+username + '/' + application_name + '/' + service_name + '/' + filename						
			else:
				filename = service_name + '.py'
				file_path = '/userservice/bootstrap/init/' + service_name +'/' + filename
				sensortopic = "None"
			print("file path : ",file_path)
			containerid = sshclient.deployService(username, machine_username, machine_password,ip,port,serviceid,service_name,file_path, filename,sensortopic)
			containerid = containerid[:-1]
			URL = "http://localhost:8080/servicelcm/service/deploymentStatus"
			req = {
				'serviceId' : serviceid,
				'username' : username,
				'serviceName' : service_name,
				'status' : 'success',
				'ip' : ip,
				'port' : 55555,
				'containerId' : containerid,
				'applicationName' : application_name
			}
			print(req)
			requests.post(url = URL, json = req)
			
		except Exception as error:
			print("Error ",error)
			URL = "http://localhost:8080/servicelcm/service/deploymentStatus"
			req = {
				'serviceId' : serviceid,
				'username' : username,
				'serviceName' : service_name,
				'status' : 'success',
				'ip' : ip,
				'port' : 55555,
				'containerId' : containerid,
				'applicationName' : application_name
			}		
			requests.post(url = URL, json = req)			
		res = {'status' : 'ok'}
		return flask.jsonify(res)

	app.run(host = '0.0.0.0',port = port)

def main():
	app = flask.Flask('Deoployment Manger')
	port = 8888 #deployer port
	req_t = threading.Thread(target = req_handler, args = (app,port))
	req_t.start()
	req_t.join()
	return

if __name__ == '__main__':
	main()
