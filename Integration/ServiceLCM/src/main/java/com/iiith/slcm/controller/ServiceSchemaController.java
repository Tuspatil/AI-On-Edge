package com.iiith.slcm.controller;

import com.iiith.slcm.businessentities.DeploymentInfoDTO;
import com.iiith.slcm.businessentities.ServerInfoDTO;
import com.iiith.slcm.businessentities.ServiceInfoDTO;
import com.iiith.slcm.dataentities.Topology;
import com.iiith.slcm.service.ServiceLCM;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;


@RestController
public class ServiceSchemaController {

    @Autowired
    private ServiceLCM serviceLCM;

    @RequestMapping(value = "/service/start", method = RequestMethod.POST)
    public void startService(@RequestBody ServiceInfoDTO serviceInfoDTO) {
        System.out.println("Received Request: /service/start " + serviceInfoDTO);
        serviceLCM.startService(serviceInfoDTO);
    }

    @RequestMapping(value = "/service/stop", method = RequestMethod.POST)
    public void stopService(@RequestBody ServiceInfoDTO serviceInfoDTO) {
        System.out.println("Received Request: /service/redeploy " + serviceInfoDTO);
        serviceLCM.stopService(serviceInfoDTO);
    }

    @RequestMapping(value = "/service/redeploy", method = RequestMethod.POST)
    public void redeployService(@RequestBody ServiceInfoDTO serviceInfoDTO) {
        System.out.println("Received Request: /service/redeploy " + serviceInfoDTO);
        serviceLCM.redeployService(serviceInfoDTO);
    }


    @RequestMapping(value = "/service/update", method = RequestMethod.POST)
    public void allotedServer(@RequestBody ServerInfoDTO serverInfoDTO) {
        System.out.println("Received Request: /service/redeploy " + serverInfoDTO);
        serviceLCM.updateServiceWithIpPort(serverInfoDTO);
    }

    @RequestMapping(value = "/service/deploymentStatus", method = RequestMethod.POST)
    public void deploymentStatus(@RequestBody DeploymentInfoDTO deploymentInfoDTO) {
        System.out.println("Received Request: /service/redeploy " + deploymentInfoDTO);
        if ("success".equalsIgnoreCase(deploymentInfoDTO.getStatus())) {
            // DELETE service info
            serviceLCM.updateServiceDeploymentStatus(deploymentInfoDTO);
            serviceLCM.deletePendingRequest(deploymentInfoDTO);
        } else {
            // TODO:
        }
    }


    @RequestMapping(value = "/service/topology/{userId}", method = RequestMethod.GET)
    public List<Topology> getTopology(@PathVariable("userId") String userId) {
        //System.out.println("Received Request: /service/topology/{userId} " + userId);
        return serviceLCM.getTopologyForUser(userId);
    }

    @RequestMapping(value = "/service/topology/serviceName/{serviceName}", method = RequestMethod.GET)
    public List<Topology> getTopologyForServiceName(@PathVariable("serviceName") String serviceName) {
        //System.out.println("Received Request: /service/topology/serviceName/{serviceName} " + serviceName);
        return serviceLCM.getTopologyForServiceName(serviceName);
    }
}
