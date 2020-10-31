from flask import Flask, request, render_template,jsonify
from flask_restful import Resource, Api
import json
import requests
import os
import requests


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

UPLOAD_FOLDER_SENSOR = "/home/pratik/"
ALLOWED_EXTENSIONS_JSON = {'json'}  
app.config['UPLOAD_FOLDER_SENSOR'] = UPLOAD_FOLDER_SENSOR

app = Flask(__name__)
api = Api(app)


URL="127.0.0.1"
PORT=5057
PROTO="http://"

def allowed_file_json(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_JSON


@app.route('/sensorUpload', methods=['GET', 'POST'])
def upload_file():  
    if request.method == 'POST':
        username = request.form['username']
        print(username)
        if 'file' not in request.files:
            return jsonify(status="failure",message="Unknown error")
        file = request.files['file']
        if file.filename == '':
            return jsonify(status="failure",message="No file selected")
        if file and allowed_file_json(file.filename):
            filename = str(file.filename)
            dest = UPLOAD_FOLDER_SENSOR
            file.save(os.path.join(dest, filename))  
            jsonpath = dest+"sensor_registration.json"
            f = open (jsonpath, "r")
            config_data=json.load(f)
            reply = dict()
            reply["username"] = username
            reply["config_file"] = config_data
            # params = json.dumps(reply)
            # print(params)
            #pratik
            req = requests.post(url="http://127.0.0.1:5051/sensorregistration",json=reply)
            return jsonify(upload="success")
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload the Service Here</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <br><br>Enter Username : 
      <input type=text name=username>
      <br><br>
      <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(host=URL,port=PORT,debug=True)

