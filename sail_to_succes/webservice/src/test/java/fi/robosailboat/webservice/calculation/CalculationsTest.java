package fi.robosailboat.webservice.calculation;

import fi.robosailboat.webservice.boatCommunication.WayPointService;
import fi.robosailboat.webservice.boatCommunication.dto.Command;
import fi.robosailboat.webservice.boatCommunication.dto.SensorData;
import fi.robosailboat.webservice.boatCommunication.dto.WaypointData;
import fi.robosailboat.webservice.calculation.Calculations;
import fi.robosailboat.webservice.weatherStationCommunication.WeatherDTO;
import org.junit.Before;
import org.junit.Ignore;
import org.junit.Test;

import static org.junit.Assert.*;

public class CalculationsTest {

    private Calculations calculations;

    @Before
    public void init() {
        calculations = new Calculations();
        SensorData sensorData = new SensorData(601053810, 199445030, 180, 4, 150);
        WaypointData waypointData = new WaypointData(60.052229, 19.907767, 15);
        WayPointService.clearWaypoints();
        WayPointService.addWaypointLastInList(waypointData);
        WeatherDTO weatherDTO = new WeatherDTO();
        weatherDTO.setDirection(100);
        weatherDTO.setSpeed(5);
        calculations.setData(sensorData, weatherDTO);
    }

    @Test
    public void getNextCommand() {
        Command next = calculations.getNextCommand();

        assertEquals("112", next.getR());
        assertEquals("086", next.getS());

        SensorData sensorData = new SensorData(601045680, 199456190, 0, 5, 30);
        WaypointData waypointData = new WaypointData(60.104718, 19.946027, 15);
        WayPointService.clearWaypoints();
        WayPointService.addWaypointLastInList(waypointData);
        WeatherDTO weatherDTO = new WeatherDTO();
        weatherDTO.setDirection(30);
        weatherDTO.setSpeed(5);
        calculations.setData(sensorData, weatherDTO);

        next = calculations.getNextCommand();

        assertEquals("120", next.getR());
        assertEquals("094", next.getS());
    }


    @Test
    public void calculateTrueWindDirection() {
        double result = calculations.calculateTrueWindDirection(180, 5, 5, 150);

        assertEquals(153, result, 0.5);
    }


    @Test
    public void calculateTrueWindSpeed() {
        double result = calculations.calculateTrueWindSpeed(180, 5, 5, 150);

        assertEquals(-0, result, 0.5);

        result = calculations.calculateTrueWindSpeed(0, 5, 5, 30);

        assertEquals(0.8, result, 0.5);
    }

    @Test
    public void calculateTargetCourse() {
        double result = calculations.calculateTargetCourse();

        assertEquals(197, result, 0.5);
    }

    @Test
    public void distanceBetween() {
        double result = calculations.distanceBetween(60.105381, 19.944503,
                60.098792, 19.947658);

        assertEquals( 753, result,0.5);
    }
}