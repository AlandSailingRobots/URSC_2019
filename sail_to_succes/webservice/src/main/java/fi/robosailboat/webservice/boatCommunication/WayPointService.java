package fi.robosailboat.webservice.boatCommunication;

import fi.robosailboat.webservice.boatCommunication.dto.WaypointData;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class WayPointService {

    private static List<WaypointData> WAYPOINT_LIST = new ArrayList<>();

    public WayPointService() {
        initWaypoints();
    }

    public static List<WaypointData> getWaypointList(){
        return WAYPOINT_LIST;
    }

    public static void addWaypointLastInList(final WaypointData waypointDat){
        WAYPOINT_LIST.add(waypointDat);
    }

    public static void addWaypoint(final int index ,final WaypointData waypointData){
        WAYPOINT_LIST.add(index, waypointData);
    }

    public static void initWaypoints(){
        WAYPOINT_LIST.add(new WaypointData(60.105,19.95,5));
        WAYPOINT_LIST.add(new WaypointData(60.108,19.95,5));
        WAYPOINT_LIST.add(new WaypointData(60.108,19.956,5));
        WAYPOINT_LIST.add(new WaypointData(60.105,19.956,5));
    }



    public static void removeWaypoint(final int index){
        WAYPOINT_LIST.remove(index);
    }

    public static void updateWaypoint(final int index, final int action, final double value){

         switch (action){
             case 1:
                 WAYPOINT_LIST.get(index).setLatitude(value);
                 break;
             case 2:
                 WAYPOINT_LIST.get(index).setLongitude(value);
                 break;
             case 3:
                 WAYPOINT_LIST.get(index).setRadius(value);
                 break;
         }
    }

    public static void clearWaypoints() {
        WAYPOINT_LIST.clear();
    }
}
