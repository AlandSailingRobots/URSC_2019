/*
 * position_logger.cpp
 *
 *  Created on: May 1, 2019
 *      Author: ubuntu
 */
#include <stdio.h>
#include <stdlib.h>
#include "gps.h"
#include "rpi_cmps12.h"
#include "position_logger.h"
#include <iostream>

uint8_t gps_init_flag = 0;

loc_t position_log() {


    // Open
  if(gps_init_flag==0){ 
 gps_init();
gps_init_flag =1;
}
    loc_t data;
    while (1) {
        gps_location(&data);
        return data;
    }
    return data;
}
