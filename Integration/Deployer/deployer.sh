#!/bin/bash

sudo docker build -t deployer .
sudo docker run -d -v ${HOME}:/userservice --name="deployer" --network="host" deployer
