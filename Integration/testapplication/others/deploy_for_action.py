import requests
import json
from kafka import KafkaProducer
from kafka import KafkaConsumer


def main():
	file=open("config.json","r")
	data=json.load(file)

	URL = "http://13.68.206.239:5052/actionmanager"

	req = {
	'username' : 'dhamo',
	'applicationname' : 'testapplication1',
	'servicename' : 'emergencyfirealaram',
	'serviceid' : 'dhamo_testapplication1_emergencyfirealaram',
	'config_file' : data,
	'sensor_host' : ['127.0.0.1:9092 temperature1_in', '127.0.0.1:9092 temperature2_in']
	}

	res = requests.post(url = URL, json = req)

	print(res)
	res = {
	"status" : 200
	}

	return res

if __name__ == '__main__':
	main()
