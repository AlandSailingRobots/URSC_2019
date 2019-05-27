package fi.robosailboat.webservice.boatCommunication.controller;

import fi.robosailboat.webservice.boatCommunication.dto.Command;
import fi.robosailboat.webservice.boatCommunication.dto.PostResponse;
import fi.robosailboat.webservice.boatCommunication.dto.SensorData;
import fi.robosailboat.webservice.boatCommunication.dto.WaypointData;
import fi.robosailboat.webservice.calculation.Calculations;
import fi.robosailboat.webservice.robosailboatLib.repository.LoggingRepository;
import fi.robosailboat.webservice.weatherStationCommunication.SimpleMqttCallback;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Random;

@RestController
@RequestMapping("/dataTransfer")
public class VesselDataTransferController {

    private static Logger LOG = LoggerFactory.getLogger(VesselDataTransferController.class);
    private static Calculations calculations = new Calculations();

    @Autowired
    private LoggingRepository loggingRepo;

    @PostMapping(value = "/sensorData", consumes = "application/json", produces = "application/json")
    @ResponseBody
    public PostResponse postData(@RequestBody SensorData values) {


       /* this is just for testing*/
        loggingRepo.insert(values);
        SensorData latestData = loggingRepo.findTopByOrderByCreatedDesc();

        LOG.info("Latest sensorData. Gps latitud: " + latestData.getLatitude() + " | Gps longitud: " + latestData.getLongitude()
                + " | Compass direction: " + latestData.getDirection());

        calculations.setData(latestData, SimpleMqttCallback.getLatestWeather());

        /*Random respons command with values between 60 and 120*/
        /*Random rnd = new Random();
        int rAngle = rnd.nextInt(61)+60;
        int sAngle = rnd.nextInt(61)+60;

        return  new Command((double)rAngle, (double)sAngle);*/
        Command next = calculations.getNextCommand();
        return new PostResponse(next.getR(), next.getS(), next.getD());
    }

    public static int getCurrentWaypointIndex() {
        return calculations.getCurrentWaypointIndex();
    }

    public static Command getCurrentCommand() {
        return calculations.getNextCommand();
    }
}
