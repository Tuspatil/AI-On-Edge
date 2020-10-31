import requests
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer


def main():
	file=open("config.json","r")
	data=json.load(file)

	URL = "http://127.0.0.1:5080/actionmanager"

	req = {
	'username' : 'pratik',
	'applicationname' : 'testapplication1',
	'servicename' : 'algo1',
	'serviceid' : 'pratik_testapplication1_algo1',
	'config_file' : data,
	'sensor_host' : ['127.0.0.1:9092 camera1_in', '127.0.0.1:9092 camera2_in', '127.0.0.1:9092 camera3_in']
	}

	res = requests.post(url = URL, json = req)

	print(res)
	res = {
	"status" : 200
	}

	return res

if __name__ == '__main__':
	main()
