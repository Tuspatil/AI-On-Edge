def redeploy_service(redeployRequest):
    # TODO: Send request to SLCM
    #  ??? How do I know SLCM's rest endpoint's IP and PORT
    import requests
    startRequestJson = {"serviceId": redeployRequest.serviceId,
                        "servicename": redeployRequest.servicename,
                        "username": redeployRequest.username,
                        "applicationname": redeployRequest.applicationname,
                        }

    print("Request sent to redeploy service:", redeployRequest)
    print("Request:", startRequestJson)
    r = requests.post(url="http://localhost:8080/servicelcm/service/redeploy",
                      headers={'Content-type': 'application/json'},
                      json=startRequestJson)

    print("Response:", r.status_code)

    if r.status_code == 200:
        return True

    return False


def getContainerStatus(service):
    containerId, ip, port = service.containerId, service.ip, service.port

    if containerId is None:
        print("Container id is missing for service:", service)
        return False

    import requests

    url = f"http://{ip}:{port}/v1.24/containers/{containerId}/json"
    print("URL:", url)
    response = requests.get(url)
    print(response)
    if response.status_code >= 400:
        return False

    dict = response.json()

    status = dict['State']['Running']

    return status
