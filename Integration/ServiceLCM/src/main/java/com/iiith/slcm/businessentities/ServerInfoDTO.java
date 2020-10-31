package com.iiith.slcm.businessentities;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ServerInfoDTO {
    @JsonProperty("result")
    String result;
    @JsonProperty("serviceid")
    String serviceId;
    @JsonProperty("serverip")
    String serverIp;
    @JsonProperty("sshPort")
    String sshPort;
    @JsonProperty("machineusername")
    String sshUsername;
    @JsonProperty("password")
    String sshPassword;


    public ServerInfoDTO() {
    }

    public String getResult() {
        return result;
    }

    public void setResult(String result) {
        this.result = result;
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

    @Override
    public String toString() {
        return "ServerInfo{" +
                "result='" + result + '\'' +
                ", serviceid='" + serviceId + '\'' +
                ", serverip='" + serverIp + '\'' +
                ", sshPort='" + sshPort + '\'' +
                ", machineusername='" + sshUsername + '\'' +
                ", password='" + sshPassword + '\'' +
                '}';
    }
}
