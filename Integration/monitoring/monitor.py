import flask
import json
import time, sys
import threading
import kafka
from pymongo import MongoClient
from flask import request
import warnings
warnings.filterwarnings("ignore")

kafka_server = 'localhost:9092'
topic = 'platform_monitor'
mongoDb_server = 'localhost:27017'

def getCurrTimestamp():
	return time.time()

def getStats(mycollection, load):
	load["ip"] = load['machineID'].split(':')[0]
	load["port"] = int(load['machineID'].split(':')[1])
	load.pop('machineID')
	load.pop('timestamp')
	load.pop('_id')
	return load

def connectMongoDB():
	client = MongoClient()
	client = MongoClient(mongoDb_server)
	return client

def getCollection(client):
	mydatabase = client['registry']
	mycollection = mydatabase['machine_stats']
	curr = getCurrTimestamp()
	cursor = mycollection.find() 
	for record in cursor: 
	    ts = record['timestamp']
	    if curr - ts > 15:
	    	mycollection.remove(record)
	return mycollection

def insertIntoDB(mycollection, record):
	rec = mycollection.insert(record) 
	return rec

def checkIntoDB(mycollection, machineID):
	if mycollection.find({'machineID': machineID}).count() == 0:
		return False
	else:
		return True

def updateIntoDB(mycollection, machineID, record):
	mycollection.update_one({'machineID' : machineID},{ "$set": record})

def update_stats(topic, mycollection):
	consumer = kafka.KafkaConsumer(topic, bootstrap_servers=[kafka_server])
	for message in consumer:
		data = (message.value).decode('utf-8')
		data = data.split(' ', 2)
		mid = data[0] + ':' + data[1]
		server_stats = data[2].split(' ')
		load = {}
		load['machineID'] = mid
		load["username"] = server_stats[0]
		load["password"] = server_stats[1]
		load["free_cpu"] = float(server_stats[2])
		load["free_mem"] = float(server_stats[3])
		load["number_of_events_per_sec"] = int(server_stats[4])
		load["free_RAM"] = float(server_stats[5])
		load["temperature"] = float(server_stats[6])
		load["n_cores"] = int(server_stats[7])
		load["load_average_1"] = float(server_stats[8])
		load["load_average_5"] = float(server_stats[9])
		load["load_average_15"] = float(server_stats[10])
		load["timestamp"] = getCurrTimestamp()
		if checkIntoDB(mycollection, mid):
			updateIntoDB(mycollection, mid, load)
			print(mid,'- updated record into registry.')
		else:
			rec = insertIntoDB(mycollection, load)
			print(mid,'- new record inserted into registry with id :',rec)


def req_handler(app, port, mycollection):
	@app.route('/monitoring/getLoad', methods=['GET'])
	def getload():
		data = {}
		cnt = 0
		server_load = []
		curr = getCurrTimestamp()
		cursor = mycollection.find() 
		for record in cursor: 
			ts = record['timestamp']
			if curr - ts < 3:
				load = getStats(mycollection, record)
				server_load.append(load)

		data["n_servers"] = len(server_load)
		data["server_load"] = server_load
		res = json.dumps(data)
		return res


	app.run(port = port)


if __name__ == "__main__":
	app = flask.Flask('sensor_app')
	# port = sys.argv[1]
	port = 5055
	client = connectMongoDB()
	mycollection = getCollection(client)
	req_t = threading.Thread(target = req_handler, args = (app, port, mycollection))
	req_t.start()
	update_t = threading.Thread(target = update_stats, args = (topic, mycollection))
	update_t.start()
	update_t.join()
	req_t.join()
