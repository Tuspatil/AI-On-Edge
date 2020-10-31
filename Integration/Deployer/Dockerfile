from base_image
RUN pip3 install sshclient
RUN pip3 install Flask
RUN pip3 install paramiko
RUN pip3 install requests

ADD deployer.py .
ADD deployer_helper.py .
ADD sshclient.py .
ENTRYPOINT python3 -u deployer.py
