#include <cstring>
#include <stdio.h>
#include <stdlib.h>
#include <fstream>
#include <string>
#include <sys/time.h>
#include "csv_log.h"
#include <string>
#include <iostream>
#include <iomanip>

using namespace std;

ofstream outputFile;
static bool title_flag = true;
std::string LogFilename;

int fileopened=0;
double logging(double longitude, double latitude, float boyen_distance, int counter_boyen) {

if(!fileopened){
 timeval curTime;
        gettimeofday(&curTime, NULL);
        int milli = curTime.tv_usec / 1000;

        char buffer [80];
        strftime(buffer, 80, "%Y-%m-%d %H:%M:%S", localtime(&curTime.tv_sec));

        char currentTime[84] = "";
        sprintf(currentTime, "%s:%d", buffer, milli);
std::string currenttimestring(currentTime);

LogFilename= "LOG_RasPirates_"+currenttimestring;
fileopened = 1;
}

	outputFile.open(LogFilename, ios::out | ios::app);

	if(title_flag == true) {

		// write the file headers
		outputFile <<"Timestamp"<<"," << "GPS_Lat"<< "," << "GPS_Long" << "," <<"Boyen Distanz" << "," << "Counter_Boyen" << endl;
	}

	// get current date/time
	timeval curTime;
	gettimeofday(&curTime, NULL);
	int milli = curTime.tv_usec / 1000;
	int deci = (milli - milli % 100) /100;

	char buffer [80];
	strftime(buffer, 80, "%Y-%m-%dT%H:%M:%S", localtime(&curTime.tv_sec));

	char currentTime[84] = "";
	sprintf(currentTime, "%s.%dZ", buffer, deci); //, milli

	// write the data to the output file
	outputFile << setprecision(9) << currentTime << "," <<latitude << "," << longitude << "," << boyen_distance << "," << counter_boyen << endl;

	// close the output file
	outputFile.close();
	title_flag = false;

	return 0;
}


