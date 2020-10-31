import requests
import json
import time
import random
from kafka import KafkaProducer
from kafka import KafkaConsumer

def get_sensor_data(topic,out_topic):
	consumer = KafkaConsumer(topic,bootstrap_servers=['localhost:9092'],auto_offset_reset = "latest")
	producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
	print("out_topic is ",out_topic)
	for message in consumer:
		s = message.value.decode('utf-8')
		print(s)
		s = s.split('>')
		msg = str(random.randrange(10,20))
		msg = msg + ">" + s[1]  
		print(msg)
		producer.send(str(out_topic), bytes(str(msg),"utf-8"))
		producer.flush() 
		time.sleep(2)


def main(): 

	# Make Request To Sensor Manager To Get Sensor Topics  
	file=open("config.json","r")
	data=json.load(file)

	d = {"username":"pratik","applicationname":"testapplication1","servicename":"algo1","serviceid":"pratik_testapplication1_algo1","config_file":data}
	r=requests.post(url="http://127.0.0.1:5040/sensormanager",json=d)

	data = r.json()
	print(data)
	get_sensor_data(data['temporary_topic'],'pratik_testapplication1_algo1')
	# if(topic == 'False' or topic == 'None'):
	# 	print("Not Autho")
	# else:
	# 	print('Sensor topic : ' + topic)
	# 	get_sensor_data(topic)

if __name__ == '__main__':
	main()