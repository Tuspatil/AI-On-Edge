from kafka import KafkaProducer
from kafka.errors import KafkaError
from kafka import KafkaConsumer
import time
import random
import threading 


def sensor():
	producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])
	l = [0,0,0,0,0,1,0,0,0,0]
	while True:
		n = random.choice(l)
		msg = 'nilgiri_roomno:101' + " " + str(n)
		producer.send(str('doorstep2_out'), bytes(str(msg),"utf-8"))
		producer.flush() 
		time.sleep(5)

def main():
	t1 = threading.Thread(target=sensor, args=())
	t1.start()
	consumer = KafkaConsumer('doorstep2_in',group_id='doorstep2',bootstrap_servers=['127.0.0.1:9092'])
	for message in consumer:
		msg = message.value.decode('utf-8')
		print("Message recv ",msg)

main()
