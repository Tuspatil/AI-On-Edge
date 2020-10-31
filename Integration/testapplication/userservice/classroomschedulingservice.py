from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import time
import random
import threading 
import sys

def main():
	temp_topic = sys.argv[1]
	output_topic = sys.argv[2]
	producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])
	consumer = KafkaConsumer(str(temp_topic),bootstrap_servers=['127.0.0.1:9092'],auto_offset_reset = "latest")
	
	for message in consumer:
		s = message.value.decode('utf-8')

		temp = s.split()
		room = temp[0]
		strength = int(temp[1)]
		seat = int(temp[2])
		empty = seat - strength
		print(f'{room} : Strength of class is {strength} ,Number of Seat is {seat} ,Empty Seat is {empty}')
		if(empty > 50):
			print('Msg Proff : ' + str(strength))
			print('Msg Acad Office : ' + str(seat))

if __name__ == '__main__':
	main()
