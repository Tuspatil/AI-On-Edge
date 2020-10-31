import requests
import json
import time
import random
from kafka import KafkaProducer
from kafka import KafkaConsumer

# def get_sensor_data(topic,out_topic):
	# consumer = KafkaConsumer(topic,bootstrap_servers=['localhost:9092'],auto_offset_reset = "latest")
	# producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
	# print("out_topic is ",out_topic)
	# for message in consumer:
	# 	s = message.value.decode('utf-8')
	# 	print(s)
	# 	s = s.split('>')
	# 	msg = str(random.randrange(10,20))
	# 	msg = msg + ">" + s[1]  
	# 	print(msg)
	# 	producer.send(str(out_topic), bytes(str(msg),"utf-8"))
	# 	producer.flush() 
	# 	time.sleep(2)

def get_sensor_data(temp_topic,output_topic):
	# temp_topic = sys.argv[1]
	# output_topic = sys.argv[2]
	consumer = KafkaConsumer(str(temp_topic),bootstrap_servers=['127.0.0.1:9092'],auto_offset_reset = "latest")
	producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])
	for message in consumer:
		s = message.value.decode('utf-8')
		temp = s.split(' ')
		temprature = int(temp[1])
		print("fire alaram algo getting ",s)
		if int(temprature) > 200:
			print('Fire Alarm temperature exceed 200')
			msg = str(temp[0]) + " " + str(temprature)
			producer.send(str(output_topic), bytes(str(msg),"utf-8"))
			producer.flush() 
			time.sleep(5)
		

def main(): 

	# Make Request To Sensor Manager To Get Sensor Topics  
	file=open("config.json","r")
	data=json.load(file)

	d = {"username":"dhamo","applicationname":"testapplication1","servicename":"emergencyfirealaram","serviceid":"dhamo_testapplication1_emergencyfirealaram","config_file":data}
	r=requests.post(url="http://127.0.0.1:5050/sensormanager",json=d)
	
	data = r.json()
	print(data)
	get_sensor_data(data['temporary_topic'],'dhamo_testapplication1_emergencyfirealaram')
	# if(topic == 'False' or topic == 'None'):
	# 	print("Not Autho")
	# else:
	# 	print('Sensor topic : ' + topic)
	# 	get_sensor_data(topic)

if __name__ == '__main__':
	main()