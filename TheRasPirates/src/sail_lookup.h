/*
 * sail_lookup.h
 *
 *  Created on: 10.05.2019
 *      Author: pi
 */

#ifndef SAIL_LOOKUP_H_
#define SAIL_LOOKUP_H_

//r is angle between current bearing and the given wind direction of the weather station
int get_sailangle(float r, float windspeed);

#endif /* SAIL_LOOKUP_H_ */
