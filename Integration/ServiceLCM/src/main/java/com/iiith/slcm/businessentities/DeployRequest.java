package com.iiith.slcm.businessentities;

import com.fasterxml.jackson.annotation.JsonProperty;

public class DeployRequest {
    @JsonProperty("serviceid")
    private String serviceId;
    @JsonProperty("servicename")
    private String serviceName;
    @JsonProperty("username")
    private String username;
    @JsonProperty("applicationname")
    private String applicationName;
    @JsonProperty("serverip")
    private String serverIp;
    @JsonProperty("sshPort")
    private String sshPort;
    @JsonProperty("machineusername")
    private String machineUsername;
    @JsonProperty("password")
    private String password;

    public DeployRequest() {
    }

    @Override
    public String toString() {
        return "DeployRequest{" +
                "username='" + username + '\'' +
                ", applicationname='" + applicationName + '\'' +
                ", servicename='" + serviceName + '\'' +
                ", serviceid='" + serviceId + '\'' +
                ", serverip='" + serverIp + '\'' +
                ", sshPort='" + sshPort + '\'' +
                ", machineusername='" + machineUsername + '\'' +
                ", password='" + password + '\'' +
                '}';
    }

    public DeployRequest(String username, String applicationName, String serviceName, String serviceId, String serverIp, String sshPort, String machineUsername, String password) {
        this.username = username;
        this.applicationName = applicationName;
        this.serviceName = serviceName;
        this.serviceId = serviceId;
        this.serverIp = serverIp;
        this.sshPort = sshPort;
        this.machineUsername = machineUsername;
        this.password = password;
    }


    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
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

    public String getServiceId() {
        return serviceId;
    }

    public void setServiceId(String serviceId) {
        this.serviceId = serviceId;
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

    public String getMachineUsername() {
        return machineUsername;
    }

    public void setMachineUsername(String machineUsername) {
        this.machineUsername = machineUsername;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }
}
