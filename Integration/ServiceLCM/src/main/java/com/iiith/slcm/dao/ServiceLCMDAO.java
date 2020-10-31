package com.iiith.slcm.dao;

import com.iiith.slcm.dataentities.PendingRequests;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.persistence.EntityManagerFactory;

@Component
public class ServiceLCMDAO {

    @Autowired
    private EntityManagerFactory entityManagerFactory;

    public void addServiceInfo(PendingRequests pendingRequests) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Transaction tx = session.beginTransaction();
        session.save(pendingRequests);
        tx.commit();
        session.close();
    }

    public PendingRequests getServiceInfo(String serviceId) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        PendingRequests pendingRequests = session.get(PendingRequests.class, serviceId);
        session.close();
        return pendingRequests;
    }

    public void updateServiceInfo(PendingRequests pendingRequests) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Transaction tx = session.beginTransaction();
        session.update(pendingRequests);
        tx.commit();
        session.close();
    }

    public void deletePendingRequest(String serviceId) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Transaction tx = session.beginTransaction();
        PendingRequests pendingRequests = session.get(PendingRequests.class, serviceId);
        session.delete(pendingRequests);
        tx.commit();
        session.close();
    }
}
