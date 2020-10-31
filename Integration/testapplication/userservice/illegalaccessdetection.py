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

	consumer = KafkaConsumer(str(temp_topic),bootstrap_servers=['127.0.0.1:9092'],auto_offset_reset = "latest")
	producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])
	for message in consumer:
		s = message.value.decode('utf-8')
		temp = s.split(' ')
		status = int(temp[1])
		print(s)
		if status == 1:
			msg = str(temp[0]) + " " + str(1)
			producer.send(str(output_topic), bytes(str(msg),"utf-8"))
			producer.flush() 
			time.sleep(5)

		
			


if __name__ == '__main__':
	main()
