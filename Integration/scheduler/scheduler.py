import schedule 
import time 
import threading 
from random import randrange
import json
from flask import Flask,request,jsonify
import random
import json
import requests
import argparse
from datetime import datetime
import pickle
app = Flask(__name__)

service_life_cycle_ip = "127.0.0.1"
service_life_cycle_port = 8080
Myport = 5053

DUMPING_DELAY_IN_3_SECS = 1
def time_add(time,minutes_to_add) :
     hr = int(str(time).split(":")[0])
     mn = int(str(time).split(":")[1])
     mn = (mn+minutes_to_add)
     hr = (hr + int(mn/60))%24
     mn=mn%60
     hr = str(hr)
     mn = str(mn)
     if(len(hr)==1):
         hr="0"+hr
     if(len(mn)==1):
         mn="0"+mn
     return hr+":"+mn


class Scheduler:
    def __init__(self):   
        self.job_dict = {}
        self.main_service_id_dict={}
        self.single_instances ={} #
        self.started = {} #done
        self.loop_schedules=[] #done
        self.main_id_sch_id={}
    def pending_jobs(self):
        while True: 
            schedule.run_pending() 
            time.sleep(10)

    def send_request_to_service_life_cyle(self,username,application_id,service_name,service_instance_id,type_):
        response = {"username":username,"applicationname":application_id,"servicename":service_name,"serviceId":self.main_service_id_dict[service_instance_id]}
        print(response)
        if type_=="start":
            res = requests.post('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/servicelcm/service/start', json=response)
        else:
            res = requests.post('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/servicelcm/service/stop', json=response)
        
    def run(self):
        t1 = threading.Thread(target=self.pending_jobs) 
        t1.start() 
    def exit_service(self,service_instance_id):
        service_instance_id,username,application_id,service_name = service_instance_id[0],service_instance_id[1],service_instance_id[2],service_instance_id[3]
        print("+MSG TO SLCM TO STOP \t\t",service_instance_id)
        #send request to service life cycle manager to cancel service 
        self.send_request_to_service_life_cyle(username,application_id,service_name,service_instance_id,"stop")
        del self.started[service_instance_id]
        schedule.cancel_job(self.job_dict[service_instance_id])
        # del self.job_dict[service_instance_id]
    def run_service(self,service_detail):
        username,application_id,service_name,end,service_instance_id = service_detail[0],service_detail[1],service_detail[2],service_detail[3],service_detail[4]
        print("+MSG TO SLCM TO START \t\t",service_instance_id)
        #send request to service life cycle manager to start service
        self.send_request_to_service_life_cyle(username,application_id,service_name,service_instance_id,"start")
        data = {
               "service_id": service_instance_id,
               "username":username,
               "application_id":application_id,
               "service_name":service_name,
               "end":end
        }
        self.started[service_instance_id]=data
        job_id = schedule.every().day.at(end).do(self.exit_service,((service_instance_id,username,application_id,service_name))) 
        self.job_dict[service_instance_id]=job_id
        
    def run_service_period(self,service_detail):
        username,application_id,service_name,end,service_instance_id = service_detail[0],service_detail[1],service_detail[2],service_detail[3],service_detail[4]
        print("+MSG TO SLCM TO START \t\t",service_instance_id)
        #send request to service life cycle manager to start service
        self.send_request_to_service_life_cyle(username,application_id,service_name,service_instance_id,"start")

        now = datetime.now()
        current_time = now.strftime("%H:%M")
        end_time = time_add(current_time,int(end))

        data = {
               "service_id": service_instance_id,
               "username":username,
               "application_id":application_id,
               "service_name":service_name,
               "end":end_time
        }
        self.started[service_instance_id]=data

        job_id = schedule.every().day.at(end_time).do(self.exit_service,((service_instance_id,username,application_id,service_name))) 
        self.job_dict[service_instance_id]=job_id
        
    def run_service_once(self,service_detail):
        username,application_id,service_name,end,service_instance_id = service_detail[0],service_detail[1],service_detail[2],service_detail[3],service_detail[4]
        print("+MSG TO SLCM TO START \t\t",service_instance_id)
        #send request to service life cycle manager to start service
        self.send_request_to_service_life_cyle(username,application_id,service_name,service_instance_id,"start")
        data = {
               "service_id": service_instance_id,
               "username":username,
               "application_id":application_id,
               "service_name":service_name,
               "end":end
        }
        self.started[service_instance_id]=data
        if(service_instance_id in self.single_instances.keys()):
            del self.single_instances[service_instance_id] 
        job_id = schedule.every().day.at(end).do(self.exit_service,((service_instance_id,username,application_id,service_name))) 
        try:
            if(self.job_dict[service_instance_id]):
                print("here")
                schedule.cancel_job(self.job_dict[service_instance_id])
        except:
            pass
        self.job_dict[service_instance_id]=job_id
    def stop_all_started_at_their_end_time(self):
        for key in self.started.keys():
            service_instance_id,username,application_id,service_name,end = self.started[key]["service_id"],self.started[key]["username"],self.started[key]["application_id"],self.started[key]["service_name"],self.started[key]["end"]
            job_id = schedule.every().day.at(end).do(self.exit_service,((service_instance_id,username,application_id,service_name))) 
            self.job_dict[service_instance_id]=job_id
            # del self.started[service_instance_id]
            self.main_service_id_dict[service_instance_id] = username+"_"+application_id+"_"+service_name
            self.main_id_sch_id[username+"_"+application_id+"_"+service_name]=service_instance_id
    def schedule(self,request_,s_id=None):
        username = request_["username"]
        application_id = request_["application_id"]
        service_name = request_["service_name"]
        single_instance = request_["singleinstance"]
        day = request_["day"]
        start_time = request_["start_time"]
        end = request_["end_time"]
        period = request_["period"]
        # service_instance_id=username+"_"+application_id+"_"+service_name+"_"+str(randrange(10000))
        main_service_id = username+"_"+application_id+"_"+service_name
        
        service_instance_id = s_id

        if service_instance_id is None:
            service_instance_id=username+"_"+application_id+"_"+service_name+"_"+str(randrange(10000))

        self.main_service_id_dict[service_instance_id]=main_service_id
        self.main_id_sch_id[main_service_id] = service_instance_id

        result = "OK"
        
        if(str(single_instance)=="True"):
            print("single instance ",bool(single_instance))
            if(start_time=="NOW" and day is None):
                self.run_service_once((username,application_id,service_name,end,service_instance_id))
            elif day is not None and start_time!="NOW":
                self.single_instances[service_instance_id]=request_
                job_id = None
                if(day=="monday"):
                    job_id = schedule.every().monday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="tuesday"):
                    job_id = schedule.every().tuesday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="wednesday"):
                    job_id = schedule.every().wednesday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="thursday"):
                    job_id = schedule.every().thursday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="friday"):
                    job_id = schedule.every().friday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="saturday"):
                    job_id = schedule.every().saturday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                else:
                    job_id = schedule.every().sunday.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                self.job_dict[service_instance_id]=job_id
            else:
                self.single_instances[service_instance_id]=request_
                job_id = schedule.every().day.at(start_time).do( self.run_service_once,((username,application_id,service_name,end,service_instance_id)))
                self.job_dict[service_instance_id]=job_id
        elif day is None and period is not None:
            self.loop_schedules.append({"service_id":service_instance_id,"request": request_})
            interval = period["interval"]
            end = period["length"]
        
            job_id = schedule.every(interval).minutes.do( self.run_service_period,((username,application_id,service_name,end,service_instance_id)))
            self.job_dict[service_instance_id]=job_id
        elif day is not None:
                self.loop_schedules.append({"service_id":service_instance_id,"request": request_})
                if(day=="monday"):
                    job_id = schedule.every().monday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="tuesday"):
                    job_id = schedule.every().tuesday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="wednesday"):
                    job_id = schedule.every().wednesday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="thursday"):
                    job_id = schedule.every().thursday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="friday"):
                    job_id = schedule.every().friday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
                elif(day=="saturday"):
                    job_id = schedule.every().saturday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
                else:
                    job_id = schedule.every().sunday.at(start_time).do( self.run_service,((username,application_id,service_name,end,service_instance_id)))
        else:
            result = "ERROR : wrong scheduling format"
        return result,service_instance_id

def GetDict(services):
    d={}

    for _ in services:
        d[_]=False

    return d
def ConstructDict(data):
    forward_dict={}
    backward_dict={}
    for _ in data.keys():
        forward_dict[_]=data[_]["servicename"]
    for key,values in forward_dict.items():
        backward_dict[values]=key

    return forward_dict,backward_dict

def Make_Data(username,application_id,service_name,start_time=None,end_time=None,singleinstance=False,day=None,period=None):
    data_dict={"username":username,"application_id":application_id,"service_name":service_name,"singleinstance":singleinstance,"day":day,"start_time":start_time,"end_time":end_time,"period":period}

    return data_dict

def GetServices(data,all_services):
    services=[]
    for _ in all_services:
        if(data[_]["scheduled"]=="True"):
            services.append(_)

    return services

def Convert(data):
    return_data=[]

    username=data["Application"]["username"]
    application_id=data["Application"]["applicationname"]
    all_services=list(data["Application"]["services"].keys())
    services=GetServices(data["Application"]["services"],all_services)
    forward_dict,backward_dict=ConstructDict(data["Application"]["services"])
    # print(forward_dict)
    # print(backward_dict)
    # print(services)
    
    for service in services:
        # if(service!="service-1"):
        #   continue
        bool_dict=GetDict(all_services)
        bool_dict[service]=True

        order_dependency=[]
        stack=[]
        stack.append(service)

        while(len(stack) > 0):
            # print(order_dependency)
            temp=stack.pop()
            if(temp!=service):
                order_dependency.append(temp)

            curr_dep=data["Application"]["services"][temp]["dependency"]
            for _ in curr_dep:
                if(not bool_dict[backward_dict[_]]):
                    stack.append(backward_dict[_])
                    bool_dict[backward_dict[_]]=True

        order_dependency=order_dependency[::-1]
        order_dependency.append(service)
        # print(order_dependency)

        if(data["Application"]["services"][service]["period"]!="None"):
            for service_dep in order_dependency:
                return_data.append(Make_Data(username=username,application_id=application_id,service_name=forward_dict[service_dep],singleinstance="False",period=data["Application"]["services"][service]["period"]))
        else:
            times=[]
            days=[]
            flags=[True,True]

            if "time" in data["Application"]["services"][service].keys():
                times=[(s,e) for s,e in zip(data["Application"]["services"][service]["time"]["start"],data["Application"]["services"][service]["time"]["end"])]
            else:
                times.append((None,None))
                flags[0]=False

            if "days" in data["Application"]["services"][service].keys():
                days=[_ for _ in data["Application"]["services"][service]["days"]]
            else:
                days.append(None)
                flags[1]=False
                
            if(data["Application"]["services"][service]["singleinstance"]) or flags[1]:
                for service_dep in order_dependency:
                    for day in days:
                        for time in times:
                            return_data.append(Make_Data(username=username,application_id=application_id,service_name=forward_dict[service_dep],singleinstance=data["Application"]["services"][service]["singleinstance"],start_time=time[0],end_time=time[1],day=day))
            else:
                for service_dep in order_dependency:
                    for time in times:
                        return_data.append(Make_Data(username=username,application_id=application_id,service_name=forward_dict[service_dep],singleinstance=data["Application"]["services"][service]["singleinstance"],start_time=time[0],end_time=time[1]))

    return return_data

def ChangeData(data,name):
    for _ in data["Application"]["services"].keys():
        if(_ != name):
            data["Application"]["services"][_]["scheduled"]="False"
        else:
            data["Application"]["services"][_]["scheduled"]="True"
            del data["Application"]["services"][_]["days"]
            data["Application"]["services"][_]["time"]["start"]=["NOW"]
            data["Application"]["services"][_]["time"]["end"]=["23:45"]

    return data
   

@app.route('/schedule_service', methods=['GET', 'POST'])
def schedule_service():
    content = request.get_json()
    
    res = "OK"
    print(content)
    print(type(content))
    if(content["action"]=="Stop"):
        id_ = content["config"]["Application"]["username"]+"_"+content["config"]["Application"]["applicationname"]+"_"+content["config"]["Application"]["services"][content["servicename"]]["servicename"]

        response = {"username":content["config"]["Application"]["username"],"applicationname":content["config"]["Application"]["applicationname"],"servicename":content["config"]["Application"]["services"][content["servicename"]]["servicename"],"serviceId":id_}

        print(response)
        print(type(response))
        service_instance_id = sch.main_id_sch_id[id_]

        del sch.started[service_instance_id]
        
        schedule.cancel_job(sch.job_dict[service_instance_id])
        
        res = requests.post('http://'+service_life_cycle_ip+':'+str(service_life_cycle_port)+'/servicelcm/service/stop', json=response)
        print("+MSG TO SLCM TO STOP ",id_)

    else:
        if(content["action"]=="Start"):
            print("start")
            content["config"]=ChangeData(content["config"],content["servicename"])
        # print(content["config"])
        extracted_requests = Convert(content["config"])
        # print(extracted_requests)
        for scheduling_request in extracted_requests:
            print("+ RECEIVED REQUEST")
            print("\t\t ",scheduling_request,"\n")
            result,service_id = sch.schedule(scheduling_request)
            if(result!="OK"):
                res="ERROR : wrong scheduling format"
    return {"result":res}
sch = None
def dumping_thread():
    global sch
    minutes=0
    while True: 
        time.sleep(3)
        minutes+=1
        if minutes%DUMPING_DELAY_IN_3_SECS==0:
            print("+ Started ",minutes/6," minutes ago")
            print("+ DUMPING DETAILS")
            print("\t- Single Instance Schedules")
            print("\n\t\t",sch.single_instances)
            print("\t- Started")
            print("\n\t\t",sch.started)
            print("\t- Schedules")
            print("\n\t\t",sch.loop_schedules)
            print("\n")
            print("+ DUMPING DETAILS END")
            
            data = {"single_instance":sch.single_instances,
                    "started":sch.started,
                    "schedules":sch.loop_schedules
                    # "main_service_id_dict":self.main_service_id_dict
                    }
           
            pickle_out = open("/home/sch_data.pickle","wb")
            pickle.dump(data, pickle_out)
            pickle_out.close() 
           

            
if __name__ == "__main__": 
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-p","--port",required=True)
    # ap.add_argument("-i","--service_life_cycle_ip",required=True)
    # ap.add_argument("-x","--service_life_cycle_port",required=True)
    # args = vars(ap.parse_args())          
    # service_life_cycle_ip = args["service_life_cycle_ip"]
    # service_life_cycle_port = int(args["service_life_cycle_port"])
    # Myport = args["port"]
    sch = Scheduler()
    sch.run()
    '''
        retrieve data from logging service
        sch.started = data["started"]    #dictionary
        sch.loop_schedules = data["schedules"] #list
        sch.single_instances = data["single_instance"] #dictionary
        sch.main_service_id_dict = data["main_service_id_dict"] #dictionary
        sch.stop_all_started_at_their_end_time()

        for key in sch.singleinstances.keys():
            sch.schedule(sch.single_instances[key])
        for request in sch.loop_schedules:
            sch.schedule(request) 
         #it covers both single instance and non single instances 
    '''

    try:

        dbfile = open("/home/sch_data.pickle","rb")
        db = pickle.load(dbfile)

        schedules_ = db["schedules"]
        started = db["started"]
        single_instances = db["single_instance"]

        sch.loop_schedules == schedules_
        sch.single_instances = single_instances
        sch.started = started
        for schedue in schedules_:
            single_instance_id = schedue["service_id"]
            request_ = schedue["request"]
            sch.schedule(request_,single_instance_id)

        for key in single_instances.keys():
            sch.schedule(single_instances[key],key)
        sch.stop_all_started_at_their_end_time()
    except:
        print("NO PREVIOUS DATA")


    t2 = threading.Thread(target=dumping_thread) 
    t2.start()
        
    app.run(debug=False,host="0.0.0.0",port=int(Myport)) 



