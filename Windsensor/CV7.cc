#include "CV7.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <wiringSerial.h>


CV7::CV7() {
		m_bufferSize = 30;
}

CV7::~CV7()
{
	if(m_fd < 0) {
		serialClose(m_fd);
	}
}

void CV7::loadConfig(string portName, int baudRate)
{
	if((m_fd = serialOpen(portName.c_str(), baudRate)) < 0) {
		throw "CV7::openPort: Unable to connect";
	}
}

void CV7::setBufferSize(unsigned int bufferSize)
{
	if(bufferSize < 0)
	{
		throw "CV7::setBufferSize: bufferSize must be 1 or higher";
	}
	m_bufferSize = bufferSize;
}

unsigned int CV7::getBufferSize()
{
	return m_bufferSize;
}

void CV7::refreshData()
{
	float windDirection;
	float windSpeed;
	float windTemperature;

	const int NON_BREAKING_SPACE = 255;
	const int BUFF_SIZE = 256;
	char buffer[BUFF_SIZE];

	int index = 0;
	while(index < BUFF_SIZE) {

		buffer[index] = serialGetchar(m_fd);
		fflush(stdout);

		if(NON_BREAKING_SPACE == ((int)buffer[index])) {
			throw "CV7::refreshData: Serial read timeout";
		}

		index++;
	}

	const int IIMWV = 0;
	const int WIXDR = 1;
	bool updated[] = {false,false};

	char* split = strtok(buffer,"$,");
	while(split != NULL) {
		if(strcmp(split, "IIMWV") == 0) {
			split = strtok(NULL, "$,");
			windDirection = atof(split);
			split = strtok(NULL, "$,");
			split = strtok(NULL, "$,");
			windSpeed = atof(split);
			updated[IIMWV] = true;
		} else if(strcmp(split, "WIXDR") == 0) {
			split = strtok(NULL, "$,");
			split = strtok(NULL, "$,");
			windTemperature = atof(split);
			updated[WIXDR] = true;
		}

		if(updated[IIMWV] && updated[WIXDR]) {
			break;
		}
		split = strtok(NULL, "$,");
	}

	m_windDirection.push_back(windDirection);
	m_windSpeed.push_back(windSpeed);
	m_windTemperature.push_back(windTemperature);

	while(m_windDirection.size() > m_bufferSize) {
		m_windDirection.erase(m_windDirection.begin());
		m_windSpeed.erase(m_windSpeed.begin());
		m_windTemperature.erase(m_windTemperature.begin());
	}
}

float CV7::getAverageValue(vector<float> v)
{
	if(v.empty()) {
		return 0;
	}

	float sum = 0;
	for(unsigned int i = 0; i < v.size(); i++) {
		sum += v.at(i);
	}
	float averageValue = sum/v.size();
	return averageValue;
}

float CV7::getWindDirection()
{
	return getAverageValue(m_windDirection);
}

float CV7::getWindSpeed()
{
	return getAverageValue(m_windSpeed);
}

float CV7::getWindTemperature()
{
	return getAverageValue(m_windTemperature);
}
