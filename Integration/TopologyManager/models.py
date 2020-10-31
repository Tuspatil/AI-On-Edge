from sqlalchemy import Column, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Service(Base):
    __tablename__ = 'topology'
    serviceId = Column(String, primary_key=True)
    serviceName = Column(String)
    applicationName = Column(String)
    dependencyCount = Column(BigInteger)
    username = Column(String)
    status = Column(String)
    port = Column(String)
    ip = Column(String)
    containerId = Column(String)
    redeployRequest = Column(String)

    def __repr__(self):
        return f"<Service(userid='{self.username}', serviceid='{self.serviceId}')>"

class RedeployRequest:
    def __init__(self, serviceId, serviceName, username, applicationName):
        self.serviceId = serviceId
        self.servicename = serviceName
        self.username = username
        self.applicationname = applicationName
