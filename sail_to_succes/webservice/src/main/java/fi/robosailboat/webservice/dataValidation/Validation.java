package fi.robosailboat.webservice.dataValidation;

import fi.robosailboat.webservice.boatCommunication.dto.SensorData;
import fi.robosailboat.webservice.boatCommunication.dto.WaypointData;
import fi.robosailboat.webservice.weatherStationCommunication.SimpleMqttCallback;
import fi.robosailboat.webservice.calculation.Calculations;

public class Validation {

    private SensorData latestData;
    private SensorData expectedData;
    int maxDistanceDiff; // Max distance difference between latest and expected in meters
    double maxDirectionDiff; // Max difference in direction


    public Validation(SensorData latestData, SensorData expectedData, int maxDistanceDiff, double maxDirectionDiff) {
        this.latestData = latestData;
        this.expectedData = expectedData;
        this.maxDistanceDiff = maxDistanceDiff;
        this.maxDirectionDiff = maxDirectionDiff;
    }

    public void validate(){

        Calculations calculations = new Calculations();
        calculations.setData(latestData, SimpleMqttCallback.getLatestWeather());
        double distanceDiff = calculations.distanceBetween(latestData.getLatitude(), latestData.getLongitude(),
                expectedData.getLatitude(), expectedData.getLongitude());

        if(distanceDiff > maxDistanceDiff){
            //Distance is bigger than max value
            System.out.println("Notify boat communication component to send route modifications!");
        }

        /*To do:
         * Check if direction difference is too big
         * */

    }
}
