from flask import Flask ,jsonify,request
import json

@app.route("/service_registry/get_service_location/<service>")
def get_service_location(service):
	with open('/home/tirth/pratik/service_registry.json') as f:
		d = json.load(f)
	
	return {"location":d[service]}

if __name__ == '__main__':
   app.run(debug=True,port=5060)
