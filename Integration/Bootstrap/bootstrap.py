import os
import time
from pymongo import MongoClient 
try: 
    conn = MongoClient() 
    print("Connected successfully!!!") 
except:   
    print("Could not connect to MongoDB") 
db = conn.portMapping #dbname
collection = db.portInfo #Collection name
#os.system("sudo sshfs ubuntu@ec2-3-19-234-9.us-east-2.compute.amazonaws.com:/home/ubuntu/shared_folder /mnt/droplet -o IdentityFile=/home/tushar/AWS.pem -o allow_other")
#os.system("cp -r /mnt/droplet .") #copying into current directory
fp = open("./codes/init/config")  #machine independent
homedir="/home/tushar"           #Change home directory here
os.system("mkdir "+homedir+"/IAS")
commands=fp.readlines()
portno=5000
portmapping={}
for cmd in commands:
    tokens=cmd.split(" ")
    hostname=tokens[0]
    IP=tokens[1]
    PORT=tokens[2]
    password=tokens[3]
    directory=tokens[4]
    os.system("mkdir "+homedir+"/IAS/"+directory) #creating a folder corresponding to a machine
    services=[]
    for i in range(5,len(tokens),2):
        services.append(tokens[i].strip("\n"))
        portmapping[tokens[i].strip("\n")]={"IP":"127.0.0.1","Port":tokens[i+1].strip("\n")}
    for service in services: #copy services, change permission of services, execute services
        os.system("sshpass -p "+password+" scp -r ./codes/init/"+service+" "+hostname+"@"+IP+":"+homedir+"/IAS/"+directory)
        time.sleep(1)
        os.system("sshpass -p "+password+" ssh "+hostname+"@"+IP+" nohup chmod 777 -R "+homedir+"/IAS/"+directory+"/"+service+"/")
        time.sleep(1)
        os.system("cd "+homedir+"/IAS/"+directory+"/"+service+" && sh "+service+".sh")
        #os.system("sshpass -p "+password+" ssh "+hostname+"@"+IP+" nohup sh /home/tushar/"+dir+"/"+service+"/"+service+".sh")
        time.sleep(1)   
collection.insert_one(portmapping)
cursor = collection.find() 
for record in cursor: 
    print(record) 
