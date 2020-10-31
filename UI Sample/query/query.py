from flask import Flask ,jsonify,request,render_template
import webbrowser
import requests


app = Flask(__name__,template_folder='template')


def getsensordata(username):
    d = {'username': username}
    r=requests.post(url="http://13.68.206.239:5050/getsensordata",json=d)
    
    sensordetail=[]
    for i in r:
        l = i.keys()
        if('api' in l):
            sensordetail.append([i['sensor_name'],i['api']])

    return sensordetail


@app.route('/')
def index():
    return render_template('query.html')



@app.route('/', methods=['POST'])
def getdata():
    username = request.form['sensoruser']
    print(username)
    sensordata = getsensordata(username)


    return render_template('query.html')
    # return render_template('query.html',n1=sensordetail[0][0],n2=sensordetail[1][0])

if __name__ == '__main__':
    app.run(debug=True)