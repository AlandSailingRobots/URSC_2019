/*
 * position_logger.h
 *
 *  Created on: 06.05.2019
 *      Author: pi
 */

#ifndef POSITION_LOGGER_H_
#define POSITION_LOGGER_H_

#include <string>

using namespace std;

struct location {
    double latitude;
    double longitude;
    double speed;
    double altitude;
    double course;

};

typedef struct location loc_t;

loc_t position_log();

#endif /* POSITION_LOGGER_H_ */
