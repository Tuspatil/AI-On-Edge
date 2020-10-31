import json
import requests
import time
def output(thestring):
    #expecting      username;appname;serviceid
    payload = dict()
    thestring = thestring.split(";")
    # username = "admin"
    # servicename = "gatemonitor"
    # appname = "Application-1"
    payload["username"] = thestring[0]
    payload["appname"] = thestring[1]
    payload["serviceid"] = thestring[2]
    
    payload = json.dumps(payload)
    req =  requests.post(url="http://13.68.206.239:5056/outputlist",data=payload)
    resultlist = json.loads(req.text)
    resultlist = resultlist["output"]
    return resultlist

def clearBuffer(thestring):
    #expecting      username;appname;serviceid
    payload = dict()
    payload["opinfo"] = thestring
    payload = json.dumps(payload)
    req =  requests.post(url="http://13.68.206.239:5056/clearoutput",data=payload)

# print(output("admin_Application-1_gatemonitor"))
# time.sleep(10)
# print("Clearing buffer")
# clearBuffer("Application-1:gatemonitor:stop:admin")
# print(output("admin_Application-1_gatemonitor"))