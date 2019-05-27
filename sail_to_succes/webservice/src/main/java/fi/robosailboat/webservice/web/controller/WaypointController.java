package fi.robosailboat.webservice.web.controller;

import fi.robosailboat.webservice.boatCommunication.WayPointService;
import fi.robosailboat.webservice.boatCommunication.dto.WaypointData;
import fi.robosailboat.webservice.boatCommunication.dto.SensorData;
import fi.robosailboat.webservice.boatCommunication.dto.Command;
import fi.robosailboat.webservice.calculation.Calculations;
import fi.robosailboat.webservice.weatherStationCommunication.WeatherDTO;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.servlet.ModelAndView;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

@Controller
@RequestMapping("/")
public class WaypointController {

    Calculations calculations = new Calculations();

    @RequestMapping("/waypoint")
    public String waypoint(Model model) {
        model.addAttribute("waypoints", WayPointService.getWaypointList());
        model.addAttribute("command", calculations.getNextCommand());

        return "waypoint";
    }

    @RequestMapping(value = "/addWaypoint", method = RequestMethod.POST)
    public void addWaypoint(@RequestParam(value = "index", required = true) int index,
                            @RequestParam(value = "latitude", required = true) double latitude,
                            @RequestParam(value = "longitude", required = true) double longitude,
                            @RequestParam(value = "radius", required = true) double radius) {
        WayPointService.addWaypoint(index, new WaypointData(latitude, longitude, radius));
    }

    @RequestMapping(value = "/addWaypointLastInList", method = RequestMethod.GET)
    public ModelAndView addWaypointLastInList(@RequestParam(value = "latitude", required = true) double latitude,
                                      @RequestParam(value = "longitude", required = true) double longitude,
                                      @RequestParam(value = "radius", required = true) double radius) {
        try {
            WayPointService.addWaypointLastInList(new WaypointData(latitude, longitude, radius));
        } catch(Exception e) {
            System.out.println("Error inserting: " + e.getMessage());
        }
        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("redirect:/waypoint");
        return modelAndView;
    }

    @RequestMapping(value = "/removeWaypoint", method = RequestMethod.GET)
    public ModelAndView removeWaypoint(@RequestParam(value = "index", required = true) int index) {
        try {
            WayPointService.removeWaypoint(index);
        } catch(Exception e) {
            System.out.println("Error removing: " + e.getMessage());
        }
        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("redirect:/waypoint");
        return modelAndView;
    }

    @RequestMapping(value = "/updateWaypoint", method = RequestMethod.GET)
    public ModelAndView update(@RequestParam(value = "index", required = true) int index,
                       @RequestParam(value = "action", required = true) int action,
                       @RequestParam(value = "value", required = true) double value) {
        try {
            WayPointService.updateWaypoint(index, action, value);
        } catch(Exception e) {
            System.out.println("Error updating: " + e.getMessage());
        }
        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("redirect:/waypoint");
        return modelAndView;
    }

    @RequestMapping(value = "/clearWaypoints", method = RequestMethod.GET)
    public ModelAndView clearWaypoints() {
        WayPointService.clearWaypoints();
        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("redirect:/waypoint");
        return modelAndView;
    }

    @RequestMapping(value ="/getWaypointList", method = RequestMethod.GET)
    public void getWaypointList(Model model) {
        model.addAttribute("waypoints",WayPointService.getWaypointList());
    }

    @RequestMapping(value = "/testCalculations", method = RequestMethod.GET)
    public ModelAndView testCalculations(
            @RequestParam(value = "latitude", required = true) double latitude,
            @RequestParam(value = "longitude", required = true) double longitude,
            @RequestParam(value = "gpsSpeed", required = true) double gpsSpeed,
            @RequestParam(value = "heading", required = true) double heading,
            @RequestParam(value = "windDirection", required = true) int windDirection,
            @RequestParam(value = "windSpeed", required = true) int windSpeed
    ) {
        SensorData sensorData = new SensorData(latitude*10000000, longitude*10000000, 0, gpsSpeed, heading);
        WeatherDTO weather = new WeatherDTO();
        weather.setDirection(windDirection);
        weather.setSpeed(windSpeed);
        calculations.setData(sensorData, weather);

        ModelAndView modelAndView = new ModelAndView();
        modelAndView.setViewName("redirect:/waypoint");
        return modelAndView;
    }
}
