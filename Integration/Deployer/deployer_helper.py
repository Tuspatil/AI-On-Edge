import json
from flask import request
import requests

def generateDokerFile(user_config, service_name, sensor_topic,output_topic):
	configfile = open(user_config, 'r')
	config = json.load(configfile)
	configfile.close()

	df = open('dockerfile', 'w')

	services = config['Application']['services']
	environment = []
	fg = True
	for key, val in services.items():  #[service_name]['environment'].items():
		if val['servicename'] == service_name:
			filename = val['filename']
			environment.append(val['environment'])
			pip = val['python3-packages']
			dependency = val['dependency']
			fg = False
			break
	if fg:
		print("service not found in config file")
		raise Exception("service not found in congfig file") 
		return
	baseimage = '''from base_image\n'''
	df.write(baseimage)
	df.write('\n')

	env = ''
	for tech in environment:
		if tech == 'tomcat':
			env += '''RUN apt-get install -y wget
RUN mkdir /usr/local/tomcat
RUN wget https://downloads.apache.org/tomcat/tomcat-8/v8.5.53/bin/apache-tomcat-8.5.53.tar.gz -O /tmp/tomcat.tar.gz
RUN cd /tmp && tar xvfz tomcat.tar.gz
RUN cp -Rv /tmp/apache-tomcat-8.5.53/* /usr/local/tomcat/
EXPOSE 8080\n\n'''

		elif tech == 'nginx':
			env += '''RUN apt-get install -y nginx\n\n'''
		
		elif tech == 'flask':
			env += '''RUN pip3 install flask\n\n'''

	df.write(env)

	for package in pip:
		cmd = 'RUN pip3 install ' + package + ' ; exit 0\n'
		df.write(cmd)
	df.write('\n')

	
	file = 'ADD ' + filename + ' .\n'
	df.write(file)
	df.write('\n')

	file_type = filename.split('.')[-1]
	dependency_topics = ''
	for topic in dependency:
		dependency_topics += topic + ' '
	print("dependency_topics : ",dependency_topics)
	if file_type == 'py':
		df.write('ENTRYPOINT python3 -u ' + filename + ' ' + sensor_topic + ' ' + output_topic + " " + dependency_topics)
	elif file_type == 'class':
		df.write('ENTRYPOINT java ' + filename.split('.')[0] + ' ' + sensor_topic + ' ' + output_topic + " " + dependency_topics)
	elif file_type == 'out':
		df.write('ENTRYPOINT ./'+filename + ' ' + sensor_topic + ' ' + output_topic + " " + dependency_topics)

	df.close()


def getFileName(config_path, service_name):
	file = open(config_path, 'r')
	config_file = json.load(file)
	file.close()

	services = config_file['Application']['services']
	for key,value in services.items():
		if value['servicename'] == service_name:
			filename = value['filename']
			return filename

	print("service not found in config file")
	raise Exception("service not found in congfig file") 


def getSensorTopic(username,application_name,service_name,serviceid,config_path):
	configfile = open(config_path, 'r')
	config = json.load(configfile)
	configfile.close()
	URL = "http://localhost:5050/sensormanager"
	req = {
		'username' : username,
		'applicationname' : application_name,
		'servicename' : service_name,
		'serviceid' : serviceid,
		'config_file' : config
	}
	res = requests.post(url = URL, json = req)	# print(json.load(res))
	return res.json()

def notifyActionManager(username,application_name,servicename,serviceid,config_path,sensor_host):
	URL = "http://localhost:5052/actionmanager"
	configfile = open(config_path, 'r')
	config = json.load(configfile)
	configfile.close()
	req = {
		'username' : username,
		'applicationname' : application_name,
		'servicename' : servicename,
		'serviceid' : serviceid,
		'config_file' : config,
		'sensor_host' : sensor_host
	}
	res = requests.post(url = URL, json = req)

