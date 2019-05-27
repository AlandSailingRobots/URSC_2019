package fi.robosailboat.webservice.boatCommunication.dto;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
public class WaypointData {
    private double latitude;
    private double longitude;
    private double radius;

    public WaypointData(double latitude, double longitude, double radius){
        this.latitude = latitude;
        this.longitude = longitude;
        this.radius = radius;
    }
}
