from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import time
import random
import threading 

from flask import Flask,request,jsonify
import requests
import sys 
import json
import os
from pymongo import MongoClient

app = Flask(__name__)

temp_list=[]

@app.route('/temperature1' ,methods=['GET','POST'])
def fun():
	global temp_list
	value = request.get_json()
	value = value['value']

	if(value == 'avg'):
		ans = sum(temp_list)/len(temp_list)
	elif(value == 'min'):
		ans = min(temp_list)
	elif(value == 'max'):
		ans = max(temp_list)
	else:
		ans = 'Invalid Input'

	a = {'msg':ans}
	return a

def sensor():
	producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])
	l=[0,0,0,0,1,0,1,0,2,3]
	while True:
		c = random.choice(l)
		n=None
		if(c==0):
			n = random.randrange(60,100)
		elif(c==1):
			n =random.randrange(10,59)
		elif(c==2):
			n=random.randrange(101,120)
		else:
			n=random.randrange(200,500)

		msg = 'nilgiri_roomno:100' +  ' ' + str(n)
		print(msg)
		if(n!=None):
			temp_list.append(float(n))
		producer.send(str('temperature1_out'), bytes(str(msg),"utf-8"))
		producer.flush() 
		time.sleep(30)

def main():
	t1 = threading.Thread(target=sensor, args=())
	t1.start()
	app.run(port=9000)


main()
