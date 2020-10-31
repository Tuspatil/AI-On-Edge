from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import time
import random
import threading 

def main():
	consumer = KafkaConsumer('alarm1_in',group_id='attendance1',bootstrap_servers=['localhost:9092'])
	for message in consumer:
		print("Message recv from instance ",message.value.decode('utf-8'))

main()
