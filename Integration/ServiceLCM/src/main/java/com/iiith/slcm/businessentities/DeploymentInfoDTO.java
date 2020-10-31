package com.iiith.slcm.businessentities;

import com.fasterxml.jackson.annotation.JsonProperty;

public class DeploymentInfoDTO {
    @JsonProperty("serviceId")
    private String serviceId;
    @JsonProperty("serviceName")
    private String serviceName;
    @JsonProperty("username")
    private String username;
    @JsonProperty("status")
    private String status; // success or failure
    @JsonProperty("ip")
    private String ip;
    // Admin service => forwarded port
    // User service => Docker daemon port
    @JsonProperty("port")
    private String port;
    @JsonProperty("containerId")
    private String containerId;
    @JsonProperty("applicationName")
    private String applicationName;

    @Override
    public String toString() {
        return "DeploymentResponse{" +
                "serviceId='" + serviceId + '\'' +
                ", serviceName='" + serviceName + '\'' +
                ", username='" + username + '\'' +
                ", status='" + status + '\'' +
                ", ip='" + ip + '\'' +
                ", port='" + port + '\'' +
                ", containerId='" + containerId + '\'' +
                ", applicationName='" + applicationName + '\'' +
                '}';
    }

    public String getApplicationName() {
        return applicationName;
    }

    public void setApplicationName(String applicationName) {
        this.applicationName = applicationName;
    }

    public DeploymentInfoDTO() {
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

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setContainerId(String containerId) {
        this.containerId = containerId;
    }
}
