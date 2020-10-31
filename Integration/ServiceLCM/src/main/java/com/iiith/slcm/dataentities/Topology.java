package com.iiith.slcm.dataentities;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "\"topology\"")
public class Topology {
    @Id
    @Column(name = "\"serviceId\"")
    private String serviceId;
    @Column(name = "\"serviceName\"")
    private String serviceName;
    @Column(name = "\"username\"")
    private String username;
    @Column(name = "\"status\"")
    private String status;
    @Column(name = "\"ip\"")
    private String ip;
    @Column(name = "\"port\"")
    private String port;
    @Column(name = "\"containerId\"")
    private String containerId;
    @Column(name = "\"redeployRequest\"")
    private String redeployRequest;
    @Column(name = "\"applicationName\"")
    private String applicationName;
    @Column(name = "\"dependencyCount\"")
    private long dependencyCount;


    public Topology() {
    }

    public long getDependencyCount() {
        return dependencyCount;
    }

    public void setDependencyCount(long dependencyCount) {
        this.dependencyCount = dependencyCount;
    }

    public String getServiceId() {
        return serviceId;
    }

    public void setServiceId(String serviceId) {
        this.serviceId = serviceId;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getIp() {
        return ip;
    }

    public void setIp(String ip) {
        this.ip = ip;
    }

    public String getPort() {
        return port;
    }

    public void setPort(String port) {
        this.port = port;
    }

    public String getContainerId() {
        return containerId;
    }

    public void setContainerId(String containerId) {
        this.containerId = containerId;
    }

    public String getRedeployRequest() {
        return redeployRequest;
    }

    public void setRedeployRequest(String redeployRequest) {
        this.redeployRequest = redeployRequest;
    }

    public String getApplicationName() {
        return applicationName;
    }

    public void setApplicationName(String applicationName) {
        this.applicationName = applicationName;
    }


    public String getServiceName() {
        return serviceName;
    }

    public void setServiceName(String serviceName) {
        this.serviceName = serviceName;
    }
}


