package com.iiith.slcm.dao;

import com.iiith.slcm.dataentities.Topology;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.query.Query;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;

import javax.persistence.EntityManagerFactory;
import javax.persistence.criteria.CriteriaBuilder;
import javax.persistence.criteria.CriteriaQuery;
import javax.persistence.criteria.Root;
import java.util.List;

@Component
public class TopologyDAO {

    @Autowired
    private EntityManagerFactory entityManagerFactory;

    public void addTopologyInfo(Topology topology) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Transaction tx = session.beginTransaction();
        session.saveOrUpdate(topology);
        tx.commit();
        session.close();
    }

    public Topology getTopologyInfo(String serviceId) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Topology topology = session.get(Topology.class, serviceId);
        session.close();
        return topology;
    }

    public List<Topology> getTopologyForUser(String userId) {

        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Transaction tx = session.beginTransaction();

        CriteriaBuilder builder = session.getCriteriaBuilder();
        CriteriaQuery<Topology> query = builder.createQuery(Topology.class);
        Root<Topology> root = query.from(Topology.class);
        query.select(root).where(builder.equal(root.get("username"), userId));
        Query<Topology> q = session.createQuery(query);
        List<Topology> topologies = q.getResultList();

        tx.commit();

        session.close();
        return topologies;
    }

    public List<Topology> getTopologyForServiceName(String serviceName) {
        Session session = entityManagerFactory.unwrap(SessionFactory.class).openSession();
        Transaction tx = session.beginTransaction();

        CriteriaBuilder builder = session.getCriteriaBuilder();
        CriteriaQuery<Topology> query = builder.createQuery(Topology.class);
        Root<Topology> root = query.from(Topology.class);
        query.select(root).where(builder.equal(root.get("serviceName"), serviceName));
        Query<Topology> q = session.createQuery(query);
        List<Topology> topologies = q.getResultList();

        tx.commit();
        session.close();
        return topologies;
    }
}
