package com.iiith.slcm.util;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

public class PlatformProperties {
    private static PlatformProperties instance;
    private static Properties properties = new Properties();

    static {
        try {
            InputStream resourceAsStream = PlatformProperties.class.getClassLoader().getResourceAsStream("platform.properties");
            properties.load(resourceAsStream);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private PlatformProperties() {
        try {
            InputStream resourceAsStream = PlatformProperties.class.getClassLoader().getResourceAsStream("platform.properties");
            properties.load(resourceAsStream);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static PlatformProperties getInstance() {
        if (instance == null) {
            instance = new PlatformProperties();
        }

        return instance;
    }

    public Properties getProperties() {
        return properties;
    }

    public String getServerLCMIp() {
        return properties.getProperty("server.lcm.ip");
    }

    public String getServerLCMPort() {
        return properties.getProperty("server.lcm.port");
    }

    public String getDeploymentManagerIp() {
        return properties.getProperty("deployment.manager.ip");
    }

    public String getDeploymentManagerPort() {
        return properties.getProperty("deployment.manager.port");
    }
}
