#include <cstring>
#include <chrono>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <iostream>
#include <string>
#include <sys/time.h>
#include <fstream>

#include "gps.h"
#include "nmea.h"
#include "serial.h"
#include "position_logger.h"

extern void gps_init(void) {
   std::cout << "GPS INIT"<<endl;
 serial_init();
    serial_config();

    //Write commands
}

extern void gps_on(void) {
    //Write on
}

// Compute the GPS location using decimal scale
extern void gps_location(loc_t *coord) {

    uint8_t status = _EMPTY;

    while(!(status& NMEA_GPGGA) ) {
    		gpgga_t gpgga;
    		char buffer[256];
    		serial_readln(buffer, 256);

    		if(nmea_get_message_type(buffer)==NMEA_GPGGA){
    			nmea_parse_gpgga(buffer, &gpgga);
    			gps_convert_deg_to_dec(&(gpgga.latitude), gpgga.lat, &(gpgga.longitude), gpgga.lon);

    			coord->latitude = gpgga.latitude;
                coord->longitude = gpgga.longitude;
                coord->altitude = gpgga.altitude;
                status |= NMEA_GPGGA;

    		}
    }
}

extern void gps_off(void) {
    //Write off
    serial_close();
}

// Convert lat and lon to decimals (from deg)
void gps_convert_deg_to_dec(double *latitude, char ns,  double *longitude, char we)
{
    double lat = (ns == 'N') ? *latitude : -1 * (*latitude);
    double lon = (we == 'E') ? *longitude : -1 * (*longitude);

    *latitude = gps_deg_dec(lat);
    *longitude = gps_deg_dec(lon);
}

double gps_deg_dec(double deg_point)
{
    double ddeg;
    double sec = modf(deg_point, &ddeg)*60;
    int deg = (int)(ddeg/100);
    int min = (int)(deg_point-(deg*100));

    double absdlat = round(deg * 1000000.);
    double absmlat = round(min * 1000000.);
    double absslat = round(sec * 1000000.);

    return round(absdlat + (absmlat/60) + (absslat/3600)) /1000000;
}



