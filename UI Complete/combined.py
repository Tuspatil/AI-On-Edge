from flask import Flask, request, render_template,jsonify
from flask_restful import Resource, Api
import mysql.connector
import json
import requests
import base64
import os
import zipfile
import re
import shutil
import requests
import time
import threading
from json import loads
from kafka import KafkaConsumer



'''
Sensor manager - 5050
Sensor Registration - 5051
Action Manager - 5052
Scheduler - 5053
Server LCM - 5054
Service LCM - 8080
Monitoring - 5055
Request Manager- 5056, 5057
Deployment - 5058
'''

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER_APP = '/home/'
ALLOWED_EXTENSIONS_ZIP = {'zip'}
app.config['UPLOAD_FOLDER_APP'] = UPLOAD_FOLDER_APP
UPLOAD_FOLDER_SENSOR = '/home/'
ALLOWED_EXTENSIONS_JSON = {'json'}  
app.config['UPLOAD_FOLDER_SENSOR'] = UPLOAD_FOLDER_SENSOR




kafkaDict = dict()
URL="0.0.0.0"
PORT=5056
PROTO="http://"

USER_TABLE_NAME = "user"
UPLOADS_TABLE_NAME = "useruploadss"
DB_NAME = "iot"
mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
cursor = mydb.cursor(buffered=True)

#This is the first process. It needs to create database and tables
query = "create database if not exists "+DB_NAME
cursor.execute(query)
query = "use "+DB_NAME
cursor.execute(query)
query = "create table if not exists "+USER_TABLE_NAME+"(username varchar(30), password varchar(30), token varchar(1000))"
cursor.execute(query)
query = "create table if not exists "+UPLOADS_TABLE_NAME+"(username varchar(30), appname varchar(30), serviceid varchar(30),servicename varchar(50), status varchar(20), scheduled varchar(20))"
cursor.execute(query)
#checks end here

mydb.commit()
cursor.close()
mydb.close()

class login(Resource):
    def get(self):
        return jsonify(token=-2)

    def post(self):
        authparams = request.get_json(force=True)
        print("Login request from ",authparams["username"],"pass = ",authparams["password"])
        global PROTO
        URL_loc = PROTO + URL + ":" + str(PORT) + "/auth"
        authparams["type"] = "generate"
        authparams = json.dumps(authparams)
        req = requests.post(url=URL_loc,data=authparams)
        # the req has the token. The token is returned to the request
        return json.loads(req.text)


class signup(Resource):
    def get(self):
        return jsonify(status="failure",message="no Parameters received. Expecting username and password")
    def post(self):
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        authparams = request.get_json(force=True)
        username = authparams["username"]
        password = authparams["password"]
        print("Signup request from "+authparams["username"],"pass = ",authparams["password"])
        query = "select * from "+USER_TABLE_NAME+" where username = \""+username+"\""
        cursor.execute(query)
        #print(cursor.rowcount," <- cursor row count")
        if cursor.rowcount <= 0:
            #not an existing user
            query = "insert into "+USER_TABLE_NAME+" values(\""+username+"\",\""+password+"\",\"\")"
            cursor.execute(query)
            mydb.commit()
            cursor.close()
            mydb.close()
            return jsonify(status="success")
        elif cursor.rowcount == 1:
            #there is a user with same username 
            print("User exists by name "+username)
            mydb.commit()
            cursor.close()
            mydb.close()
            #print("User exists")
            return jsonify(status="failure",message="User exists. Try login.")
        elif cursor.rowcount >1:
            #ultiple uses. how did this happen 
            mydb.commit()
            cursor.close()
            mydb.close()
            return jsonify(status="failure",message="Unknown Error")
        return jsonify(status="failure",message="Unknown Error")



class authorize(Resource):
    def get(self,num):
        return jsonify(result="failure",message="Get is not a valid request. Please create POST request.")

    def post(self):
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        recvd_params = request.get_json(force=True)
        if recvd_params["type"] == "generate":
            username = recvd_params["username"]
            password = recvd_params["password"]
            message = username + ":" + password
            query1 = "select * from "+USER_TABLE_NAME+" where username = \"" + username + "\""
            cursor.execute(query1)
            if cursor.rowcount <= 0:
                #print("Got params "+username+","+password+" but did not find user in database")
                mydb.commit()
                cursor.close()
                mydb.close()
                return jsonify(status="failure",message="User not registered")
            if cursor.rowcount > 1:
                #print("Found multiple accounts with username "+username)
                mydb.commit()
                cursor.close()
                mydb.close()
                return jsonify(status="failure",message="Multiple Users")
            message_bytes = message.encode('ascii')
            base_64_bytes = base64.b64encode(message_bytes)
            base_64 = base_64_bytes.decode('ascii')
            cursor.close()
            cursor = mydb.cursor(buffered=True)
            query2 = "update user set token=\""+base_64+"\" where username=\""+username+"\";"
            cursor.execute(query2)
            #print(cursor.rowcount)
            if cursor.rowcount == 1:
                #print("Row updated for username "+username+" token set to "+base_64)
                mydb.commit()
                cursor.close()
                mydb.close()
                return jsonify(token=base_64,status="success")
            if cursor.rowcount == 0:
                #print("There were no updations. Token was already there ")
                mydb.commit()
                cursor.close()
                mydb.close()
                return jsonify(token=base_64,status="success")
            #print("Error while updating token for user "+username)
        elif recvd_params["type"] == "validate":
            base64_message = recvd_params["token"]
            base64_bytes = base64_message.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes)
            message = message_bytes.decode('ascii')
            if ":" not in message:
                #failure
                mydb.commit()
                cursor.close()
                mydb.close()
                #print("Failed as : is not present in the string")
                return jsonify(result="failure")
            message = message.split(":")
            username = message[0]
            query = "select * from "+USER_TABLE_NAME+" where username = \""+username + "\""
            #print("validating. Username is ",username)
            cursor.execute(query)
            if cursor.rowcount <= 0:
                #failure
                mydb.commit()
                cursor.close()
                mydb.close()
                #print("Failed as username ",username," returned 0 rows")
                return jsonify(result="failure")
            if cursor.rowcount == 1:
                #sucess
                mydb.commit()
                cursor.close()
                mydb.close()
                return jsonify(result="success",username=username)
            #other issue
            if cursor.rowcount >1:
                #multiple users
                mydb.commit()    
                cursor.close()
                mydb.close()
                print("Multiple users")
                return jsonify(result="failure")
        

class request_manager_backend(Resource):
    def get(self):
        return jsonify(status="failure",message="GET request not valid. Please POST token")
    
    def post(self):
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        params = request.get_json(force=True)
        username = params["username"]
        # print("Req manager sending dashboard update for user "+username)
        #print("################## REQ MANAGER SENDING AN UPDATE  for "+username+" ####")
        query = "select appname,serviceid,servicename,status,scheduled from "+UPLOADS_TABLE_NAME+" where username=\""+username+"\""
        cursor.execute(query)
        counter = 0
        mainlist = list()
        for x in cursor:
            appname = x[0]
            serviceid = x[1]
            servicename = x[2]
            status = x[3]
            scheduled = x[4]
            innerdict = dict()
            innerdict["serviceid"]= serviceid
            innerdict["servicename"]=servicename
            innerdict["status"]=status
            innerdict["scheduled"] = scheduled
            maindict = dict()
            found = False
            for i in mainlist:
                if i["appname"]==appname:
                    found = True
                    maindict = i
            if found == True:
                maindict["data"].append(innerdict)
            else:
                maindict["data"] = list()
                maindict["data"].append(innerdict)
                maindict["appname"] = appname
                mainlist.append(maindict)
        response = json.dumps(mainlist)
        cursor.close()
        mydb.commit()
        mydb.close()
        #print("################## REQ MANAGER SENDING AN UPDATE for "+username+" ENDS HERE ########")
        return response



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_ZIP

def kafkaThread(topic):
    #print("############ STARTING KAFKA CONSUMER THREAD HERE for topic "+topic)
    print("Launching kafka thread for topic :",topic)
    consumer = KafkaConsumer(topic,group_id='request_manager1',
    bootstrap_servers=['127.0.0.1:9092'],auto_offset_reset = "latest")
    #print("request "+topic)
    # consumer3 = KafkaConsumer(topic,
    #                          bootstrap_servers=['localhost:9092'],
    #                          auto_offset_reset='earliest',
    #                          enable_auto_commit=True,
    #                          group_id='request_manager1',
    #                          value_deserializer=lambda x: loads(x.decode('utf-8')))
    global kafkaDict
    for message in consumer:
        #temp = kafkaDict[topic]
        msg = message.value.decode('utf-8')
        #print("###### GOT A KAFKA MESSAGE ON "+topic)
        #print("Buuffer is "+temp)
        # print("Topic "+topic+" msg "+msg)
        #temp = temp + "\n" + msg
        kafkaDict[topic].append(msg)

def validate(path,username,appname):
    global DB_NAME
    mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
    cursor = mydb.cursor(buffered=True)
    query = "use "+DB_NAME
    cursor.execute(query)
    files = os.listdir(path)
    directorynames = []
    foldernames = list()
    for name in files:
        # print(name)
        if name != "config.json":
            directorynames.append(path+"/"+name)
            foldernames.append(name)
    jsondata = None
    jsonpath = path+"/"+"config.json"
    filef = open(jsonpath)
    json_data_text = filef.read()
    jsondata = json.loads(json_data_text)
    
    for name in directorynames:
        foldername = name.split("/")
        foldername = foldername[-1]
        # print(foldername)
        files = os.listdir(name)
        # print(files)
        #for filenames in files:
            # print(filenames)
    kafka_topics = []
    '''
    for serviceid in foldernames:
        a_topic = username+"_"+appname+"_"+jsondata["Application"]["services"][serviceid]["servicename"]
        kafka_topics.append(a_topic)
        isscheduled = jsondata["Application"]["services"][serviceid]["scheduled"]
        if isscheduled == "True":
            query = "insert into "+UPLOADS_TABLE_NAME+" values(\""+username+"\",\""+appname+"\",\""+serviceid+"\",\""+ jsondata["Application"]["services"][serviceid]["servicename"] +"\",\"Scheduled to Run\",\""+jsondata["Application"]["services"][serviceid]["scheduled"]+"\")"
        else:
            query = "insert into "+UPLOADS_TABLE_NAME+" values(\""+username+"\",\""+appname+"\",\""+serviceid+"\",\""+ jsondata["Application"]["services"][serviceid]["servicename"] +"\",\"Not Running\",\""+jsondata["Application"]["services"][serviceid]["scheduled"]+"\")"
        print("Uploading, updating tables, query = "+query)
        cursor.execute(query)
    '''
    print("Updating tables")
    for obj in jsondata["Application"]["services"]:
        serviceid = obj
        servicename = jsondata["Application"]["services"][obj]["servicename"]
        scheduled = jsondata["Application"]["services"][obj]["scheduled"]
        a_topic = username+"_"+appname+"_"+servicename
        kafka_topics.append(a_topic)
        status = "Stopped"
        if scheduled == "True":
            status = "Processing"
        query = "insert into "+UPLOADS_TABLE_NAME+" values(\""+username+"\",\""+appname+"\",\""+serviceid+"\",\""+servicename+"\",\""+status+"\",\""+scheduled+"\")"
        cursor.execute(query)

    global kafkaDict
    for i in kafka_topics:
        kafkaDict[i] = []
        t1 = threading.Thread(target=kafkaThread,args=(i,))
        t1.start()
    cursor.close()
    mydb.commit()
    mydb.close()   
    #I need to send req to Jay here as None
    response = dict()
    response["servicename"] = ""
    response["config"] = jsondata
    response["action"] = "None"
    #response = json.dumps(response)
    # print("#######################   UPLOAD TIME REQUEST TO JAY #####################")
    # print(response)
    # print("#######################   UPLOAD TIME REQUEST TO JAY ENDS HERE ###########")
    req = requests.post(url="http://13.68.206.239:5053/schedule_service",json=response)
    print("Scheduler requested to schedule services which are scheduled")
    return True
'''
@app.route('/uploadService', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        global DB_NAME
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)
        message = username + ":" + password
        message_bytes = message.encode('ascii')
        base_64_bytes = base64.b64encode(message_bytes)
        token = base_64_bytes.decode('ascii')
        query = "select username from user where token=\""+token+"\""
        print(token, " <- token")
        cursor.execute(query)
        if cursor.rowcount != 1:
            cursor.close()
            mydb.commit()
            mydb.close() 
            return jsonify(status="failure",message="not logged in")
        if 'file' not in request.files:
            return jsonify(status="failure",message="Unknown error")
        file = request.files['file']
        if file.filename == '':
            return jsonify(status="failure",message="No file selected")
        if file and allowed_file(file.filename):
            filename = str(file.filename)
            dest = app.config['UPLOAD_FOLDER_APP']
            file.save(os.path.join(app.config['UPLOAD_FOLDER_APP'], filename))
            path = dest+filename
            print(path)
            filename = filename.split(".")
            extractdest = dest+"/"+username+"/"+filename[0]
            #before extracting . Delete if existing
            users_folders = os.listdir(dest)
            found = False
            for users_names in users_folders:
                if users_names == username:
                    found=True
            if found == False:
                os.mkdir(dest+"/"+username)
            files = os.listdir(dest+"/"+username+"/")
            print("filename[0] = ",filename[0])
            for name in files:
                    #its a folder name. We need to compare
                if name == filename[0]:
                    #we found a folder
                    print("Found match")
                    query = "delete from "+UPLOADS_TABLE_NAME+" where username=\""+username+"\" and appname=\""+name+"\""
                    cursor.execute(query)
                    shutil.rmtree(dest+username)
            cursor.close()
            mydb.commit()
            mydb.close() 
            with zipfile.ZipFile(path, 'r') as zip_ref:
                zip_ref.extractall(extractdest)
            val_result = validate(extractdest,username,filename[0])
            if val_result == False:
                return jsonify(upload="success",validation="failure")
            else:
                return jsonify(upload="success",validation="success")
    return 
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload the Service Here</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <br><br>Enter Username : 
      <input type=text name=username>
      <br><br>
      Enter Password :
      <input type=text name=password>
      <br><br>
      <input type=submit value=Upload>
    </form>
    
'''


class processUpload(Resource):
    def get(self):
        return
    def post(self):
        recvd_params = request.get_json(force=True)
        extractdest = recvd_params["extractdest"]
        username = recvd_params["username"]
        filename = recvd_params["filename"]
        # print("Process upload got called")
        print("Uploading")
        validate(extractdest,username,filename)
        return 

class output(Resource):
    def get(self,num):
        return {"result":num*10}

    def post(self):
        recvd_params = request.get_json(force=True)
        username = recvd_params["username"]
        serviceid = recvd_params["serviceid"]
        appname = recvd_params["appname"]
        
        '''
        we need to get data from kafka and send it in output
        '''
        #create topic username_applicationname_servicename
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        query = "select servicename from "+UPLOADS_TABLE_NAME+" where username=\""+username+"\" AND serviceid=\""+serviceid+"\" AND appname=\""+appname+"\""
        cursor.execute(query)
        servicename = None
        for x in cursor:
            servicename = x[0]
        cursor.close()
        mydb.commit()
        mydb.close()
        print("Output requested for username : "+username+" appname : "+appname+" servicename : "+servicename)
        topic = username+"_"+appname+"_"+servicename
        global kafkaDict
        msg = kafkaDict[topic]
        # print("############ FROM OUTPUT, msg = ")
        # for i in msg:
        #     print(i)
        # print(" and topicname is "+topic)
        #msg = json.dumps(msg)
        return jsonify(status="success",output=msg)    

class sendToScheduler(Resource):
    def get(self):
        return

    def post(self):
        recvd_params = request.get_json(force=True)
        appname = recvd_params["appname"]
        serviceid = recvd_params["serviceid"]
        username = recvd_params["username"]
        requesttype = recvd_params["request"]
        dest = app.config['UPLOAD_FOLDER_APP']
        json_path = dest+"/"+username+"/"+appname+"/"+"config.json"
        file_json = open(json_path,"r")
        config_data=json.load(file_json)
        #Send request to Jay here: 
        response = dict()
        response["servicename"] = serviceid
        response["config"] = config_data
        response["action"] = requesttype
        #response = json.dumps(response)
        # print("#######################   FORCED REQUEST TO JAY #####################")
        # print(response)
        # print("#######################   FORCED REQUEST TO JAY ENDS HERE ###########")
        req = requests.post(url="http://13.68.206.239:5053/schedule_service",json=response)
        print("Scheduler requested to schedule serviceid "+serviceid)
        #return json.loads(req.text)
        return

class clearoutput(Resource):
    def get(self):
        return
    def post(self):
        recvd_params = request.get_json(force=True)
        global kafkaDict
        opcode = recvd_params["opinfo"]
        params = opcode.split(";")
        username = params[0]
        appname = params[1]
        servicename = params[2]
        print("Clearing output for service "+servicename)
        #create topic username_applicationname_servicename
        topicname = username+"_"+appname+"_"+servicename
        kafkaDict[topicname] = list()

class configedit(Resource):
    def get(self):
        return
    def post(self):
        print("rec req for edit config")
        recvd_params = request.get_json(force=True)
        username = recvd_params["username"]
        concat = recvd_params["service"]
        concat = concat.split("_")
        appname = concat[0]
        servicename = concat[1]
        start = recvd_params["starttime"]
        end = recvd_params["endtime"]
        day = recvd_params["day"]
        rec_scheduled = recvd_params["schtype"] 
        sensortype = recvd_params["sensortype"]
        location = recvd_params["location"]
        datarate = recvd_params["datarate"]
        action = recvd_params["action"]

        #create config
        config_file_path = app.config['UPLOAD_FOLDER_APP'] + username+"/"+appname+"/"+"config.json"
        print("Config file path = "+config_file_path)
        file_json = open(config_file_path,"r")
        config_data=json.load(file_json)
        file_json.close()
        serviceids = []
        serviceid = None
        for obj in config_data["Application"]["services"]:
            serviceids.append(obj)
            if config_data["Application"]["services"][obj]["servicename"] == servicename:
                serviceid = obj
                print("Service id set "+obj)
        maximum = -1
        for i in serviceids:
            temp = i.split("-")
            numb = temp[1]
            numb = int(numb)
            if numb > maximum:
                maximum = numb
        newnumber = maximum+1
        newnumber = str(newnumber)
        print("Maximum number is "+newnumber)
        newservicename= "service-"+newnumber
        print("new servicename "+newservicename)
        src = app.config['UPLOAD_FOLDER_APP'] + username+"/"+appname+"/"+servicename+"/"
        dst = app.config['UPLOAD_FOLDER_APP'] + username+"/"+appname+"/"+newservicename+"/"
        shutil.copytree(src, dst)
        copyofconfig = config_data["Application"]["services"][serviceid].copy()
        copyofconfig["servicename"] = newservicename
        temp1 = []
        temp1.append(start)
        copyofconfig["time"]["start"] = temp1
        temp2 = []
        temp2.append(end)
        copyofconfig["time"]["end"] = temp2
        temp3 = []
        temp3.append(day)
        copyofconfig["days"] =temp3
        counter = 1
        maindict = dict()
        for i in location:
            add = i.split("_")
            area = add[0]
            building = add[1]
            room_no = add[2]
            sensorid = "sensor"+str(counter)
            counter = counter+1
            geoloc = dict()
            geoloc["lat"] = "None"
            geoloc["long"] = "None"
            address = dict()
            address["area"] = area
            address["building"] = building
            address["room_no"] = room_no
            proc = dict()
            proc["data_rate"] = datarate
            innerdict = dict()
            innerdict["sensor_name"] = sensortype
            innerdict["sensor_geolocation"] = geoloc
            innerdict["sensor_address"] = address
            innerdict["processing"] = proc
            maindict[sensorid]=innerdict
        copyofconfig["sensor"] = maindict
        act = dict()
        t1 = dict()
        t1["value"] = "None"
        act["Output_display_to_user"] = False
        t3 = dict()
        t3["message"] = "None"
        t3["number"] = "None"
        t4 = dict()
        t4["To"] = "None"
        t4["From"] = "iastiwari@gmail.com"
        t4["Subject"] = "None"
        t4["Text"] = "None"
        if action == "displaytoadmin":
            act["Output_display_to_user"] = True
        elif action == "controlsensor":
            t1["value"] = "None"
        elif action == "email":
            t4["To"] = recvd_params["email-to"]
            t4["From"] = "iastiwari@gmail.com"
            t4["Subject"] = recvd_params["email-subject"]
            t4["Text"] = "None"
        elif action=="sms":
            t3["message"] = recvd_params["sms-subject"]
            t3["number"] = recvd_params["sms-number"]
        act["send_output_to_sensor"] = t1
        act["Send_SMS"] = t3
        act["Send_Email"] = t4
        copyofconfig["action"] = act
        copyofconfig["scheduled"] = rec_scheduled
        #Handle the dependency part here 
        isdependency = recvd_params["dependent"]
        if isdependency == "Yes":
            number_of_dependencies = recvd_params["numdependency"]
            deplist = list()
            number_of_dependencies = number_of_dependencies + 1
            for i in range(1,number_of_dependencies):
                keyname = "dependcy"+str(i)
                tsername = recvd_params[keyname]
                tsername = tsername.split("_")
                tsername = tsername[1]
                deplist.append(tsername)
            copyofconfig["dependency"] = deplist
        print("$$$$$$$$$$$$$$$$$")
        print("new copy of config is ")
        print(copyofconfig)

        #writing the changes here
        config_data["Application"]["services"][newservicename] = copyofconfig

        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print("New config is ")
        print(config_data)
        file_json = open(config_file_path,"w")
        file_json.write(json.dumps(config_data,indent=4,sort_keys=True))
        file_json.close()
        #file written
        all_services_dict = config_data["Application"]["services"].copy()
        print("$$$$$$$$$$$$$$")
        print(all_services_dict)
        keysList = all_services_dict.keys()
        keysList = list(keysList)
        print("-----------------------------------------")
        print(keysList)
        for tserviceid in keysList:
            if tserviceid != newservicename:
                del all_services_dict[tserviceid]
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        scheduled = config_data["Application"]["services"][serviceid]["scheduled"]
        if scheduled == "True":
            config_data["Application"]["services"] = all_services_dict
            print("Sending to Jay")
            print(config_data)
            response = dict()
            response["servicename"] = ""
            response["config"] = config_data
            response["action"] = ""
            req = requests.post(url="http://13.68.206.239:5053/schedule_service",json=response)
            query = "insert into "+UPLOADS_TABLE_NAME+" values(\""+username+"\",\""+appname+"\",\""+newservicename+"\",\""+newservicename+"\",\"Processing\",\""+scheduled+"\")"
            print(query)
            cursor.execute(query)
        else:
            print("Not scheduled. Normal update")
            query = "insert into "+UPLOADS_TABLE_NAME+" values(\""+username+"\",\""+appname+"\",\""+newservicename+"\",\""+newservicename+"\",\"Stopped\",\""+scheduled+"\")"
            print(query)
            cursor.execute(query)
        print("Starting kafka thread")
        a_topic = username+"_"+appname+"_"+newservicename
        global kafkaDict
        kafkaDict[a_topic] = []
        t1 = threading.Thread(target=kafkaThread,args=(a_topic,))
        t1.start()
        cursor.close()
        mydb.commit()
        mydb.close()
        print("Config update Success")
        return


class config_edit_resp(Resource):
    def get(self):
        return
    def post(self):
        recvd_params = request.get_json(force=True)
        username = recvd_params["username"]
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        #(username varchar(30), appname varchar(30), serviceid varchar(30),servicename varchar(50), 
        # status varchar(20), scheduled varchar(20))
        appreqst = recvd_params["app"]
        if appreqst == True:
            appname = recvd_params["appname"]
            query = "select appname,servicename from "+UPLOADS_TABLE_NAME+" where username=\""+username+"\" AND appname=\""+appname+"\""
            cursor.execute(query)
            values = []
            for x in cursor:
                appname = x[0]
                servicename = x[1]
                concat = appname+"_"+servicename
                values.append(concat)
            values = sorted(values)
            cursor.close()
            mydb.commit()
            mydb.close()
            return jsonify(services=values)
        else:
            query = "select appname,servicename from "+UPLOADS_TABLE_NAME+" where username=\""+username+"\""
            cursor.execute(query)
            values = []
            for x in cursor:
                appname = x[0]
                servicename = x[1]
                concat = appname+"_"+servicename
                values.append(concat)
            values = sorted(values)
            cursor.close()
            mydb.commit()
            mydb.close()
            return jsonify(services=values)

api.add_resource(login,'/authlogin')
api.add_resource(signup,'/authsignup')
api.add_resource(authorize,'/auth')
api.add_resource(request_manager_backend,'/req')
api.add_resource(output,'/outputlist')
api.add_resource(sendToScheduler,'/sendToScheduler')
api.add_resource(clearoutput,'/clearoutput')
api.add_resource(processUpload,'/processUpload')
api.add_resource(configedit,'/configEditReq')
api.add_resource(config_edit_resp,'/getServiceList')

def Updater():
    print("Updater thread started")
    while 1:
        #UNCOMMENT THIS
        mydb = mysql.connector.connect(host="localhost",user="admindb",passwd="password")
        cursor = mydb.cursor(buffered=True)
        query = "use "+DB_NAME
        cursor.execute(query)
        query  = "select username from "+USER_TABLE_NAME
        cursor.execute(query)
        usernames = []
        for x in cursor:
            usernames.append(x[0])
        for name in usernames:
            # Neeraj
            # print("#######################   UPDATE REQUEST TO SERVICE LCM #####################")
            requrl = "http://13.68.206.239:8080/servicelcm/service/topology/"+name
            try:
                resp = requests.get(requrl)
            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                time.sleep(30)
                continue
            #resp = requests.get(requrl)       
            # print(resp.text)
            if resp.ok:         
                response = resp.json()
                # print(response)
                # print(type(response))
                for block in response:
                    status = block["status"]
                    servicename = block["serviceName"]
                    appname = block["applicationName"]
                    tstatus = ""
                    if status == "alive":
                        tstatus = "Running"
                    elif status == "stopped" or status=="not working":
                        tstatus = "Stopped"
                    query = "update "+UPLOADS_TABLE_NAME+" set status=\""+tstatus+"\" where username=\""+name+"\" and appname=\""+appname+"\" and servicename=\""+servicename+"\""  
                    # print("Updating for user "+name)
                    print(query)
                    cursor.execute(query)  
            # print("#######################   UPDATE REQUEST TO SERVICE LCM ENDS HERE ###########")
        cursor.close()
        mydb.commit()
        mydb.close()
        time.sleep(3)
    
if __name__ == '__main__':
    t1 = threading.Thread(target=Updater) 
    t1.start()
    app.run(host=URL,port=PORT,debug=True)
