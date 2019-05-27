package fi.robosailboat.webservice.weatherStationCommunication;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.*;

@Slf4j
public class SimpleMqttCallback implements MqttCallback {

    private static final String CONNECTION_URI = "tcp://m24.cloudmqtt.com:14846";
    private static final String SUBSCRIPTION = "weather";
    private static final String USERNAME = "yirnfmrp";
    private static final String PASSWORD = "yhxQJ-e_JUMg";
    private MqttClient client;
    private static WeatherDTO latestWeather;

    public SimpleMqttCallback() {
        try {
            this.client = new MqttClient(CONNECTION_URI, MqttAsyncClient.generateClientId());
            this.client.setCallback(this);
            this.client.connect(initOptions());
            this.client.subscribe(SUBSCRIPTION);
        } catch (MqttException e) {
            log.error("Mqtt error: " + e);
        }

    }

    private MqttConnectOptions initOptions(){
        MqttConnectOptions options = new MqttConnectOptions();
        options.setAutomaticReconnect(true);
        options.setUserName(USERNAME);
        options.setPassword(PASSWORD.toCharArray());
        options.setCleanSession(true);
        options.setConnectionTimeout(10);
        return options;
    }
    @Override
    public void connectionLost(Throwable cause) {
        log.info("Connection lost because: " + cause);
    }

    @Override
    public void messageArrived(String topic, MqttMessage message) throws Exception {
        String stringParse =  new String(message.getPayload());
        log.info("Message received");

        latestWeather = new ObjectMapper().readValue(stringParse, WeatherDTO.class);
        log.info("object parsed. direction: " + latestWeather.getDirection() + " | speed: " + latestWeather.getSpeed()
         + " | timestamp: " + latestWeather.getTimestamp());
    }

    @Override
    public void deliveryComplete(IMqttDeliveryToken token) {
        log.info("Mqtt Delivery Complete");
    }

    public static WeatherDTO getLatestWeather() {
        return latestWeather;
    }
}
