/*
 * sail_lookup.cpp
 *
 *  Created on: 10.05.2019
 *      Author: pi
 */

//r,a is angle between current bearing and the given wind direction of the weather station
//bi arrays are sail angles

#include "sail_lookup.h"

int c;

float a[42] = {34,37,40,43,46,49,52,55,58,61,64,67,70,73,76,79,82,85,88,91,94,97,100,103,106,109,112,115,118,121,124,127,130,133,136,139,142,145,148,151,154,157};
float b1[42] = {11,12,13,14,15,16,17,18,20,21,23,24,26,27,29,30,31,33,34,36,37,39,41,43,45,47,49,51,53,55,57,59,61,63,65,67,69,71,73,75,77,80};
float b2[42] = {13,15,16,18,19,21,22,23,25,26,27,29,31,33,35,37,39,40,42,43,45,46,48,49,51,53,55,57,59,61,62,64,65,67,68,70,71,73,74,76,78,80};;
float b3[42] = {15,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,45,47,48,50,51,53,54,56,58,59,61,62,64,65,67,59,61,67,69,71,73,75,77,78,79,80};

int i;

//return is sailangle in [°]
int get_sailangle(float r, float windspeed){

	if(r<0.0F) r=r*(-1);

	if(r<a[0]){return 10;}
	if(r>a[41]){return 85;}

	if(windspeed<2.0F){

		for(i=0 ; i<40 ; i++){
			if(r>=a[i] && r<a[i+1]) return b1[i];
		}

	}else if(windspeed>=2.0F && windspeed<=8.0F){

		for(i=0 ; i<40 ; i++){
			if(r>=a[i] && r<a[i+1]) return b2[i];
		}

	}else{

		for(i=0 ; i<40 ; i++){
			if(r>=a[i] && r<a[i+1]) return b3[i];
		}
	}

	return -1;
}
