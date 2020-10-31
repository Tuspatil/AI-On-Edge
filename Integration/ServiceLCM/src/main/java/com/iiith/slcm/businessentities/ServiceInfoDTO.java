package com.iiith.slcm.businessentities;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ServiceInfoDTO {

    @JsonProperty("serviceId")
    private String serviceId;
    @JsonProperty("servicename")
    private String serviceName;
    @JsonProperty("applicationname")
    private String applicationName;
    @JsonProperty("username")
    private String username;

    @Override
    public String toString() {
        return "ServiceSchema{" +
                "serviceId='" + serviceId + '\'' +
                ", servicename='" + serviceName + '\'' +
                ", applicationname='" + applicationName + '\'' +
                ", username='" + username + '\'' +
                '}';
    }

    public ServiceInfoDTO() {
    }

    public String getApplicationName() {
        return applicationName;
    }

    public void setApplicationName(String applicationName) {
        this.applicationName = applicationName;
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

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }
}
