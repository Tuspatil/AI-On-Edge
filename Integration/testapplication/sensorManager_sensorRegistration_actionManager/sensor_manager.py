from flask import Flask ,jsonify,request
import sys
import json
from pymongo import MongoClient
import threading
from kafka import KafkaProducer
from kafka import KafkaConsumer
import time
import random

registry_ip = 'localhost'
registry_port = 27017
sensor_client = 'demo123'
sensor_document = 'sensor'
kafka_platform_ip = 'localhost:9092'

app = Flask(__name__)


def dump_data(ip,topic ,service_id ,sensor_id ,temptopic,rate): 

	producer = KafkaProducer(bootstrap_servers=[kafka_platform_ip])
	consumer = KafkaConsumer(str(topic),bootstrap_servers=[ip],auto_offset_reset = "latest")
	print("temptopic ",temptopic)
	for message in consumer:
		msg = message.value.decode('utf-8')
		# print(msg)
		# dump data in temporary topic like " msg > sensor_host_id(127.0.0.1:9092 topic)"
		producer.send(temptopic, bytes(msg,"utf-8"))    
		producer.flush()
		time.sleep(rate)

def sensor_topic_binding_to_tempTopic(sensor_topic,host_topic,service_id,temptopic,data_rate):

	for i in range(len(sensor_topic)):
		temp = sensor_topic[i].split(' ')
		ip = temp[0]
		topic=temp[1]
		sensor_host_id = host_topic[i]
		t= threading.Thread(target=dump_data ,args=(ip,topic ,service_id,sensor_host_id,temptopic,data_rate[i] ,))
		t.start()
		
		
def find_nearest(lat ,lon,sensor_name,user_id):
	client = MongoClient('localhost' ,27017)

	mydb = client[sensor_client]
	mycol = mydb[sensor_document]

	docs = mycol.find({})

	min_dis = sys.maxsize
	sensor_topic = None
	host_topic = None 

	for i in docs:

		if(('sensor_geolocation' in i.keys()) and (i['sensor_name']== sensor_name) and (user_id == i['user_id'])):
			doc_lat = int(i['sensor_geolocation']['lat'])
			doc_lon = int(i['sensor_geolocation']['long'])

			if (abs(doc_lat -lat) + abs(doc_lon-lon) ) < min_dis:
				min_dis = abs(doc_lat -lat) + abs(doc_lon-lon)
				sensor_topic = i['data_dump']['kafka']['broker_ip'] + " " + i['data_dump']['kafka']['topic']
				host_topic = i['sensor_host']['kafka']['kafka_broker_ip'] + " " + i['sensor_host']['kafka']['kafka_topic']

	return sensor_topic ,host_topic

def resolver(query,username):
	client = MongoClient('localhost' ,27017)

	mydb = client[sensor_client]
	mycol = mydb[sensor_document]

	# my_query = {'user_id':user_id ,q1:q2}
	sensor_topic = []
	host_topic=[]

	for i in range(len(query)):
		# print("keys are ",query[i].keys())
		if(('sensor_geolocation' in query[i].keys()) and query[i]['sensor_geolocation'] != None):
			lat = int(query[i]['sensor_geolocation']['lat'])
			lon = int(query[i]['sensor_geolocation']['long'])

			sen_top ,hos_top = find_nearest(lat, lon,query[i]['sensor_name'],username)
			sensor_topic.append(sen_top)
			host_topic.append(hos_top)
		else:
			docs = mycol.find(query[i])
			for j in docs:
				if(j['user_id'] == username):
					sensor_topic.append(j['data_dump']['kafka']['broker_ip'] + " " + j['data_dump']['kafka']['topic'])
					host_topic.append(j['sensor_host']['kafka']['kafka_broker_ip'] + " " + j['sensor_host']['kafka']['kafka_topic'])
					break

	return sensor_topic ,host_topic

def filter(d):
	for i in d:
		if(d[i]['sensor_name'] == "None"):
			del d[i]['sensor_name']
		if(d[i]['sensor_geolocation']['lat'] == "None" or d[i]['sensor_geolocation']['long'] == "None"):
			del d[i]['sensor_geolocation']
		if(d[i]['sensor_address']['area'] == "None" or d[i]['sensor_address']['building'] == "None" or d[i]['sensor_address']['room_no'] == "None"):
			del d[i]['sensor_address']
	return d

def getsensor(d,servicename):
	l = d['Application']['services'].keys()
	for i in l:
		if(d['Application']['services'][i]['servicename'] == servicename):
			d = d['Application']['services'][i]['sensor']
			break

	return d

def writelogs(sensor_topic,host_topic,serviceid,temptopic,data_rate):
	f = open('logs.txt','a')
	for i in range(len(sensor_topic)):
		f.write(str(sensor_topic[i]))
		if(i != len(sensor_topic)-1):
			f.write('#')
	f.write('%')

	for i in range(len(host_topic)):
		f.write(str(host_topic[i]))
		if(i != len(host_topic)-1):
			f.write('#')
	f.write('%')

	f.write(str(serviceid))
	f.write('%')
	f.write(temptopic)
	f.write('%')
	for i in range(len(data_rate)):
		f.write(str(data_rate[i]))
		if(i != len(data_rate)-1):
			f.write('#')
	f.write('%')
	f.write('\n')
	f.close()


@app.route('/getsensordata' ,methods=['GET','POST'])
def fun1():

	global registry_port
	global registry_ip


	data=request.get_json()
	user_id  = data['username']

	client = MongoClient(registry_ip ,registry_port,maxPoolSize=50)
	db = client[sensor_client]
	d = list(db['sensor'].find({'user_id':user_id}))
	
	print(d)

	for i in d:
		print(i)
		del i['_id']
		del i['data_dump']
		del i['sensor_data_type']
		del i['sensor_host']
		del i['user_id']
	
	return jsonify(d)

@app.route('/sensormanager' ,methods=['GET' ,'POST'])
def fun():


	#get userid , config file as a request
	data = request.get_json()
	user_id = data['username']
	servicename = data['servicename']
	d = data['config_file']
	serviceid = data['serviceid']
	
	#get sensor part from the config
	d = getsensor(d,servicename)
	d=filter(d)
	# #store each query in a list	
	query=[]
	data_rate = []

	for i in d:
		data_rate.append(d[i]['processing']['data_rate'])
		removed_value = d[i].pop('processing')
		query.append(d[i])

	# #get sensor topic and host topic
	sensor_topic,host_topic = resolver(query,user_id)
	print("resolver ",sensor_topic)
	# # create temp topic
	temptopic = serviceid + str(random.randrange(0,2000))
	# print(temptopic)
	
	# Open thread for execution
	t = threading.Thread( target = sensor_topic_binding_to_tempTopic , args=(sensor_topic,host_topic,serviceid,temptopic,data_rate,))
	t.start()
	writelogs(sensor_topic,host_topic,serviceid,temptopic,data_rate)

	# send temp topic to deployer
	# print("temptopic for request ",serviceid,temptopic)
	res = {
		'temporary_topic' : temptopic,
		'sensor_host' : host_topic
	}
	return jsonify(res)

if __name__ == '__main__':
	try:
		with open("logs.txt","r") as f:
			#stuff goes here
			data1 = "None"
			while(data1 != ''):
				data1 = f.readline()
				if(data1 != ''):
					data = data1.split('%')
					sensor_host= data[0].split('#')
					host_topic = data[1].split('#')
					serviceid = data[2]
					temptopic = data[3]
					data_rate=[]
					data = data[4].split('#')
					# print(data)
					for i in data:
						data_rate.append(int(i))
					t = threading.Thread( target = sensor_topic_binding_to_tempTopic , args=(sensor_host,host_topic,serviceid,temptopic,data_rate,))
					t.start()
		f.close()
	except IOError:
		print("No File")
	    #do what you want if there is an error with the file opening
	app.run(host="0.0.0.0",port=5050)
