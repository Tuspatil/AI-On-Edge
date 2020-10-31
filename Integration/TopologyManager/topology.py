from time import sleep

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import healthCheck
import rest_handler
from models import Service, RedeployRequest

DATABASE_URI = 'postgres+psycopg2://postgres:root@localhost:5432/ias-db'

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)


def poll():
    s = Session()

    s.execute('SET search_path TO "ias-schema"')
    services = s.query(Service).filter_by(status='alive') \
        .filter_by(redeployRequest='false') \
        .all()

    print("services list:", services)
    for service in services:
        alive = healthCheck.check_health(service)
        if not alive:

            if service.username != "admin":
                service.status = "stopped"
                s.add(service)
                s.commit()
            else:
                print("Service ", service.serviceId, "is down.")
                redeployRequest = RedeployRequest(service.serviceId,
                                                  service.serviceName,
                                                  service.username,
                                                  service.applicationName)

                request_sent = rest_handler.redeploy_service(redeployRequest)
                service.redeployRequest = 'true' if request_sent else 'false'
                s.add(service)
                s.commit()
        else:
            print("Service ", service.serviceId, "is alive.")

    s.close()


if __name__ == "__main__":
    # TODO Parse config file
    while True:
        try:
            poll()
            sleep(10)
        except Exception as e:
            print("Exception:", e)
