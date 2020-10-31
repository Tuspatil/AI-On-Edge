package com.iiith.slcm.dataentities;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.Id;
import javax.persistence.Table;

@Entity
@Table(name = "\"PendingRequests\"")
public class PendingRequests {
    @Id
    @Column(name = "\"serviceId\"")
    private String serviceId;
    @Column(name = "\"serviceName\"")
    private String serviceName;
    @Column(name = "\"applicationName\"")
    private String applicationName;
    @Column(name = "\"username\"")
    private String username;
    @Column(name = "\"serverIp\"")
    private String serverIp;
    @Column(name = "\"sshPort\"")
    private String sshPort;
    @Column(name = "\"sshUsername\"")
    private String sshUsername;
    @Column(name = "\"sshPassword\"")
    private String sshPassword;

    public PendingRequests() {
    }

    public String getServiceId() {
        return serviceId;
    }

    public void setServiceId(String serviceId) {
        this.serviceId = serviceId;
    }

    public String getServiceName() {
        return serviceName;
    }

    public void setServiceName(String serviceName) {
        this.serviceName = serviceName;
    }

    public String getApplicationName() {
        return applicationName;
    }

    public void setApplicationName(String applicationName) {
        this.applicationName = applicationName;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getServerIp() {
        return serverIp;
    }

    public void setServerIp(String serverIp) {
        this.serverIp = serverIp;
    }

    public String getSshPort() {
        return sshPort;
    }

    public void setSshPort(String sshPort) {
        this.sshPort = sshPort;
    }

    public String getSshUsername() {
        return sshUsername;
    }

    public void setSshUsername(String sshUsername) {
        this.sshUsername = sshUsername;
    }

    public String getSshPassword() {
        return sshPassword;
    }

    public void setSshPassword(String sshPassword) {
        this.sshPassword = sshPassword;
    }
}
