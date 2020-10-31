from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import time
import random
import threading 

def sensor_1():
	producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
	
	while True:
		n = random.randrange(0,250)
		n1 = random.randrange(100,500)
		msg = "nilgiri_roomno:101 " + str(n) + " " + str(n1)
		producer.send(str('attendance2_out'), bytes(msg,"utf-8"))
		producer.flush() 
		time.sleep(30)

def main():
	t1 = threading.Thread(target=sensor_1, args=())
	t1.start()
	consumer = KafkaConsumer('attendance2_in',group_id='attendance2',bootstrap_servers=['localhost:9092'])
	for message in consumer:
		print("Message recv from instance ",message.value.decode('utf-8'))

main()
