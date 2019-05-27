package fi.robosailboat.webservice.weatherStationCommunication;

import lombok.Data;


import java.text.SimpleDateFormat;
import java.util.TimeZone;

@Data
public class WeatherDTO {
    private int direction;
    private int speed;
    private String timestamp;

}
