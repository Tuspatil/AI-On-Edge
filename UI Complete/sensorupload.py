from flask import Flask, request, jsonify, redirect, url_for
from flask import render_template
import os
import requests
import json
import mysql.connector
import zipfile
import shutil

from codes import twowaysensor, dashboardupdate, validate, fetchoutput,configedit

sensorname = None
logged_username = None
# logged_username="pratik"
identifier = None
#change dest path
dest = "/home/"

USER_TABLE_NAME = "user"
UPLOADS_TABLE_NAME = "useruploadss"
DB_NAME = "iot"

app = Flask(__name__)


@app.route("/login", methods=['GET', 'POST'])
def login():
	if (request.method == 'POST'):
		status = False
		if ("username" in request.form.keys()
				and "password" in request.form.keys()):
			username = request.form["username"]
			password = request.form["password"]
			status = validate.auth(username, password)

		if (status):
			global logged_username
			logged_username = username
			return redirect('/dashboard')
		else:
			return render_template('/login/login.html', authcode="error")

	return render_template('/login/login.html', authcode=None)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
	if (request.method == 'POST'):
		status = False
		if ("username" in request.form.keys()
				and "password" in request.form.keys()):
			username = request.form["username"]
			password = request.form["password"]
			if(username=="admin" and password=="admin"):
				status=True

		if (status):
			global logged_username
			logged_username = username
			return redirect('/sensor')
		else:
			return render_template('/adminlogin/adminlogin.html', authcode="error")

	return render_template('/adminlogin/adminlogin.html', authcode=None)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
	if (request.method == 'POST'):
		print(request.form)
		if ("username" in request.form.keys()
				and "password" in request.form.keys()):
			username = request.form["username"]
			password = request.form["password"]
			if (len(username) > 0 and len(password) > 0):
				validate.signup(username, password)
				return redirect('/login')
			else:
				return render_template('/signup/signup.html', authcode="error")
		else:
			return render_template('/login/login.html', authcode=None)
	return render_template('/signup/signup.html', authcode=None)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
	global identifier
	global logged_username
	if (request.method == 'POST'):
		action = request.form["action"]
		identifier = request.form["value"]
		splitted = identifier.split(";")
		appname = splitted[0]
		serviceid = splitted[1]
		if (action == "start"):
			print("start service")
			params = dict()
			params["appname"] = appname
			params["serviceid"] = serviceid
			params["username"] = logged_username
			params["request"] = "Start"
			#params = json.dumps(params)
			req = requests.post(
				url="http://13.68.206.239:5056/sendToScheduler", json=params)
		elif (action == "stop"):
			print("stop service")
			params = dict()
			params["appname"] = appname
			params["serviceid"] = serviceid
			params["username"] = logged_username
			params["request"] = "Stop"
			#params = json.dumps(params)
			req = requests.post(
				url="http://13.68.206.239:5056/sendToScheduler", json=params)
		else:
			print("redirect")
			return jsonify(url_for('output'))

		return jsonify(["ok"])
	username = logged_username
	send_data = dashboardupdate.update(username)
	# print(send_data)
	return render_template(
		'/dashboard/dashboard.html', data=send_data, length=len(send_data))


@app.route("/output", methods=['GET', 'POST'])
def output():
	print("yes")
	if (request.method == 'POST'):
		global identifier
		global logged_username
		if (request.form["required"] == "send"):
			splitted = identifier.split(";")
			appname = splitted[0]
			serviceid = splitted[1]
			username = logged_username
			thestring = username + ";" + appname + ";" + serviceid
			outputlist = fetchoutput.output(thestring)
			fetchoutput.clearBuffer(thestring)
			return jsonify(outputlist)
		else:
			print(request.form["required"])
			return jsonify(url_for('dashboard'))
	print("here")
	return render_template('/output/output.html')


@app.route("/sensor", methods=['GET', 'POST'])
def sensor():
	if (request.method == 'POST'):
		username = request.form["sensorregistration"]
		f = request.files['file']
		f.save(os.path.join(dest, f.filename))

		jsonpath = dest + "sensor_registration.json"
		f = open(jsonpath, "r")

		config_data = json.load(f)

		reply = dict()
		reply["username"] = username
		reply["config_file"] = config_data
		req = requests.post(
			url="http://13.68.206.239:5051/sensorregistration", json=reply)
		data = req.json()
		if (data['msg'] == 'Sensor Registered'):
			text = "sensors registered"
		else:
			text = "Error"
		#os.system(f'rm {jsonpath}')
		os.remove(jsonpath)
		return render_template('/sensor/sensor.html', displaytext=text)

	return render_template('/sensor/sensor.html', displaytext=None)


UPLOAD_FOLDER_APP = '/home/'
ALLOWED_EXTENSIONS_ZIP = {'zip'}


def allowed_file(filename):
	return '.' in filename and filename.rsplit(
		'.', 1)[1].lower() in ALLOWED_EXTENSIONS_ZIP


@app.route("/application", methods=['GET', 'POST'])
def application():
	if request.method == 'POST':
		mydb = mysql.connector.connect(
			host="localhost", user="admindb", passwd="password")
		cursor = mydb.cursor(buffered=True)
		query = "use iot"
		cursor.execute(query)
		username = request.form['username']
		print(username)
		if 'file' not in request.files:
			return render_template(
				'/application/application.html', displaytext="Error")
			# return jsonify(status="failure",message="Unknown error")
		file = request.files['file']
		if file.filename == '':
			return render_template(
				'/application/application.html', displaytext="Error")

		if file and allowed_file(file.filename):
			filename = str(file.filename)
			dest = UPLOAD_FOLDER_APP
			file.save(os.path.join(UPLOAD_FOLDER_APP, filename))
			path = dest + filename
			print(path)
			filename = filename.split(".")
			extractdest = dest + "/" + username + "/" + filename[0]
			#before extracting . Delete if existing
			users_folders = os.listdir(dest)
			found = False
			for users_names in users_folders:
				if users_names == username:
					found = True
			if found == False:
				os.mkdir(dest + "/" + username)
			files = os.listdir(dest + "/" + username + "/")
			print("filename[0] = ", filename[0])
			for name in files:
				#its a folder name. We need to compare
				if name == filename[0]:
					#we found a folder
					print("Found match")
					query = "delete from " + UPLOADS_TABLE_NAME + " where username=\"" + username + "\" and appname=\"" + name + "\""
					cursor.execute(query)
					shutil.rmtree(dest + username)
			cursor.close()
			mydb.commit()
			mydb.close()
			with zipfile.ZipFile(path, 'r') as zip_ref:
				zip_ref.extractall(extractdest)
			somepayload = dict()
			somepayload["extractdest"] = extractdest
			somepayload["username"] = username
			somepayload["filename"] = filename[0]
			req = requests.post(
				url="http://13.68.206.239:5056/processUpload",
				json=somepayload)
			# req = json.loads(req.text)
			return render_template(
				'/application/application.html', displaytext="Successful")
	return render_template('/application/application.html', displaytext=None)


@app.route("/query", methods=['GET', 'POST'])
def query():
	global sensorname
	if (request.method == 'POST'):
		if ("username" in request.form.keys()):
			username = request.form["username"]
			sensorname = twowaysensor.getsensordata(username)
			return render_template(
				'/query/query.html',
				user=username,
				sensors=sensorname,
				displaytext=None,username=logged_username)
		else:
			selected_sensorname = request.form["sensorname"]
			querytype = request.form["querytype"]
			ans = twowaysensor.getoutput(selected_sensorname, querytype)
			text = "{} for {} is {}".format(querytype, selected_sensorname,
											ans)
			return render_template(
				'/query/query.html',
				user=None,
				sensors=sensorname,
				displaytext=text,username=logged_username)

	return render_template(
		'/query/query.html', user=None, sensors=None, displaytext=None,username=logged_username)

@app.route("/config",methods=['GET','POST'])
def config():
	if(request.method == 'POST'):
		if("action" in request.form.keys() and request.form["action"]=="givelocation"):
			locations=configedit.FetchSensorLocations(logged_username,request.form["value"])
			return jsonify({"data":locations})
		elif("action" in request.form.keys() and request.form["action"]=="givecount"):
			count=configedit.FetchServiceCount(logged_username,request.form["value"])
			return jsonify({"count":count})
		elif("action" in request.form.keys() and request.form["action"]=="givedependency"):
			dependencies=configedit.FetchServiceByApplication(logged_username,request.form["value"])
			return jsonify({"dependencies":dependencies})
		else:
			# print(type(request.form))
			# print(request.form)
			temp = request.form.to_dict(flat=False)
			converted = dict()
			for k in temp:
				if len(temp[k]) > 1:
					converted[k] = temp[k]
				else:
					thelist = temp[k]
					converted[k] = thelist[0]
			converted["username"] = logged_username
			print(converted)
			req = requests.post(
				url="http://13.68.206.239:5056/configEditReq",
				json=converted)
			names=configedit.FetchServices(logged_username)
			sensortypes=configedit.FetchSensorTypes(logged_username)
			return render_template("/configedit/configedit.html",services=names,sensortypes=sensortypes,locations=None,displaytext="Successful")

	names=configedit.FetchServices(logged_username)
	sensortypes=configedit.FetchSensorTypes(logged_username)
	return render_template("/configedit/configedit.html",services=names,sensortypes=sensortypes,locations=None)

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5057)
	# app.run(debug=True, port=5057)