package com.iiith.slcm.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.iiith.slcm.businessentities.DeployRequest;
import com.iiith.slcm.businessentities.DeploymentInfoDTO;
import com.iiith.slcm.businessentities.ServerInfoDTO;
import com.iiith.slcm.businessentities.ServiceInfoDTO;
import com.iiith.slcm.dao.ServiceLCMDAO;
import com.iiith.slcm.dao.TopologyDAO;
import com.iiith.slcm.dataentities.PendingRequests;
import com.iiith.slcm.dataentities.Topology;
import com.iiith.slcm.util.Constants;
import com.iiith.slcm.util.PlatformProperties;
import org.springframework.beans.factory.annotation.Autowired;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.ByteBuffer;
import java.util.List;
import java.util.concurrent.Flow;

@org.springframework.stereotype.Service
public class ServiceLCM {
    PlatformProperties platformProperties = PlatformProperties.getInstance();

    private final HttpClient httpClient = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_2)
            .build();

    @Autowired
    private ServiceLCMDAO serviceLCMDAO;
    @Autowired
    private TopologyDAO topologyDAO;

    public void startService(ServiceInfoDTO serviceInfoDTO) {
        PendingRequests pendingRequests = new PendingRequests();
        pendingRequests.setUsername(serviceInfoDTO.getUsername());
        pendingRequests.setServiceId(serviceInfoDTO.getServiceId());
        pendingRequests.setServiceName(serviceInfoDTO.getServiceName());
        pendingRequests.setApplicationName(serviceInfoDTO.getApplicationName());

        // Get topology info to determine whether this service already has an entry
        // If this service has no entry means this is the first time the service is to be launched
        Topology topology = topologyDAO.getTopologyInfo(serviceInfoDTO.getServiceId());

        if (topology == null) {
            // Service to be started for the first time
            // Get a free server ip and port where the service will be deployed
            String URL_ALLOCATE_SERVER = String.format("http://%s:%s/serverlcm/allocate_server/%s", platformProperties.getServerLCMIp(), platformProperties.getServerLCMPort(), serviceInfoDTO.getServiceId());

            // Add service entry to pending requests table
            serviceLCMDAO.addServiceInfo(pendingRequests);

            // send request to SERVER LCM to get a server ip and port
            sendRequestToServerLCM(URL_ALLOCATE_SERVER);
            // Service will be started when ServerLCM gives us back a free server ip and port
            // So the actual start logic is there where
            // we update service info with server ip,port,sshUsername, sshPassword


        } else if (Constants.ServiceState.STOPPED.equalsIgnoreCase(topology.getStatus())) {
            // A stop request was received sometime back to stop this service
            // And the stopping was successful
            // Now we have received a request to start this service again
            boolean startSuccess = startServiceViaDockerEngine(topology.getIp(), topology.getPort(), topology.getContainerId());

            if (startSuccess) {
                topology.setStatus(Constants.ServiceState.ALIVE);
            } else {
                topology.setStatus(Constants.ServiceState.FAILED_TO_START);
            }
            topologyDAO.addTopologyInfo(topology);

        } else {
            // else service is already running
            // increment its dependency count
            topology.setDependencyCount(topology.getDependencyCount() + 1);
            topologyDAO.addTopologyInfo(topology);
        }
    }

    private boolean startServiceViaDockerEngine(String dockerEngineIp, String dockerEnginePort, String containerId) {
        String url = String.format("http://%s:%s/v1.24/containers/%s/start?t=1",
                dockerEngineIp, dockerEnginePort, containerId);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .POST(new HttpRequest.BodyPublisher() {
                    @Override
                    public long contentLength() {
                        return 0;
                    }

                    @Override
                    public void subscribe(Flow.Subscriber<? super ByteBuffer> subscriber) {

                    }
                })
                .build();

        HttpResponse<String> response = null;
        try {
            response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException | InterruptedException e) {
            return false;
        }

        if (response.statusCode() == 500 || response.statusCode() == 404)
            return false;

        return true;
    }

    public void stopService(ServiceInfoDTO serviceInfoDTO) {
        Topology topology = topologyDAO.getTopologyInfo(serviceInfoDTO.getServiceId());

        if (topology == null)
            // this service was never started so can't stop it
            return;

        if (topology.getDependencyCount() > 0) {
            // Others have requested to start this service
            // keep the service running
            topology.setDependencyCount(topology.getDependencyCount() - 1);
            topologyDAO.addTopologyInfo(topology);
            return;
        }

        if (topology.getDependencyCount() == 0) {
            // dependencyCount=0 means no one else depends on this service
            // so it is safe to stop this service
            boolean isStopped = stopServiceViaDockerEngine(
                    topology.getIp(),
                    topology.getPort(),
                    topology.getContainerId());

            if (isStopped) {
                topology.setStatus(Constants.ServiceState.STOPPED);
            } else {
                topology.setStatus(Constants.ServiceState.FAILED_TO_STOP);
            }
            topologyDAO.addTopologyInfo(topology);
        }
    }

    public void updateServiceWithIpPort(ServerInfoDTO serverInfoDTO) {
        PendingRequests pendingRequests = serviceLCMDAO.getServiceInfo(serverInfoDTO.getServiceId());
        pendingRequests.setServerIp(serverInfoDTO.getServerIp());
        pendingRequests.setSshPort(serverInfoDTO.getSshPort());
        pendingRequests.setSshPassword(serverInfoDTO.getSshPassword());
        pendingRequests.setSshUsername(serverInfoDTO.getSshUsername());

        serviceLCMDAO.updateServiceInfo(pendingRequests);

        DeployRequest deployRequest = new DeployRequest(
                pendingRequests.getUsername(),
                pendingRequests.getApplicationName(),
                pendingRequests.getServiceName(),
                pendingRequests.getServiceId(),
                pendingRequests.getServerIp(),
                pendingRequests.getSshPort(),
                pendingRequests.getSshUsername(),
                pendingRequests.getSshPassword());

        startServiceViaDeploymentManager(deployRequest);
    }

    public void updateServiceDeploymentStatus(DeploymentInfoDTO deploymentInfoDTO) {
        Topology topology = topologyDAO.getTopologyInfo(deploymentInfoDTO.getServiceId());
        if(topology==null && !"admin".equalsIgnoreCase(deploymentInfoDTO.getUsername())) {
        	topology = new Topology();
        	topology.setPort(deploymentInfoDTO.getPort());
        }
        topology.setServiceId(deploymentInfoDTO.getServiceId());
        topology.setServiceName(deploymentInfoDTO.getServiceName());
        topology.setUsername(deploymentInfoDTO.getUsername());
        topology.setContainerId(deploymentInfoDTO.getContainerId());
        topology.setIp(deploymentInfoDTO.getIp());
        // whenever a service is started we consider it has no other dependencies
        topology.setDependencyCount(0);
        // FIXME: Ask for json value coming from deployment manager
        topology.setStatus(Constants.ServiceState.ALIVE);
        topology.setRedeployRequest("false");
        topology.setApplicationName(deploymentInfoDTO.getApplicationName());

        topologyDAO.addTopologyInfo(topology);
    }

    public void deletePendingRequest(DeploymentInfoDTO deploymentInfoDTO) {
        serviceLCMDAO.deletePendingRequest(deploymentInfoDTO.getServiceId());
    }

    private void sendRequestToServerLCM(String url) {
        HttpRequest request = HttpRequest.newBuilder()
                .GET()
                .uri(URI.create(url))
                .build();

        System.out.println("Sending request to: " + url);

        httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    System.out.println("response.statusCode(): " + response.statusCode());
                    return response;
                })
                .thenApply(HttpResponse::body)
                .thenAccept(System.out::println);
    }

    private void startServiceViaDeploymentManager(DeployRequest deployRequest) {
        String url = String.format("http://%s:%s/deployment/dodeploy",
                platformProperties.getDeploymentManagerIp(),
                platformProperties.getDeploymentManagerPort());

        ObjectMapper objectMapper = new ObjectMapper();
        String jsonBody = "";
        try {
            jsonBody = objectMapper.writeValueAsString(deployRequest);
        } catch (JsonProcessingException e) {
            e.printStackTrace();
        }

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonBody))
                .build();

        System.out.println("jsonBody: " + jsonBody);
        System.out.println("url: " + url);

        httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    System.out.println(response.statusCode());
                    return response;
                })
                .thenApply(HttpResponse::body)
                .thenAccept(System.out::println);
    }

    private boolean stopServiceViaDockerEngine(String dockerEngineIp,
                                               String dockerEnginePort,
                                               String containerId) {

        String url = String.format("http://%s:%s/v1.24/containers/%s/stop?t=1",
                dockerEngineIp,
                dockerEnginePort,
                containerId);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .POST(new HttpRequest.BodyPublisher() {
                    @Override
                    public long contentLength() {
                        return 0;
                    }

                    @Override
                    public void subscribe(Flow.Subscriber<? super ByteBuffer> subscriber) {

                    }
                })
                .build();

        HttpResponse<String> response = null;
        try {
            response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException | InterruptedException e) {
            return false;
        }

        if (response.statusCode() == 500)
            return false;

        return true;
    }

    public void redeployService(ServiceInfoDTO serviceSchema) {
        PendingRequests pendingRequests = new PendingRequests();
        pendingRequests.setUsername(serviceSchema.getUsername());
        pendingRequests.setServiceId(serviceSchema.getServiceId());
        pendingRequests.setServiceName(serviceSchema.getServiceName());
        pendingRequests.setApplicationName(serviceSchema.getApplicationName());

        String URL_ALLOCATE_SERVER = String.format("http://%s:%s/serverlcm/allocate_server/%s",
                platformProperties.getServerLCMIp(),
                platformProperties.getServerLCMPort(),
                serviceSchema.getServiceId());

        sendRequestToServerLCM(URL_ALLOCATE_SERVER);
        serviceLCMDAO.addServiceInfo(pendingRequests);
    }

    public List<Topology> getTopologyForUser(String userId) {
        return topologyDAO.getTopologyForUser(userId);
    }

    public List<Topology> getTopologyForServiceName(String serviceName) {
        return topologyDAO.getTopologyForServiceName(serviceName);
    }
}
