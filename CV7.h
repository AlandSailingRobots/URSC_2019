#ifndef __CV7_H__
#define __CV7_H__

#include <string>
#include <vector>

using namespace std;

class CV7 {

	public:

		CV7();
		~CV7();

		/*
			Loads the CV7 windsensor.
		*/
		void loadConfig(string portName, int baudRate);

		/*
			Sets vector sizes. Must be greater than 0 and default value is 30.
		*/
		void setBufferSize(unsigned int bufferSize);

		/*
			Returns current bufferSize value set.
		*/
		unsigned int getBufferSize();

		/*
			Gets a new reading from the sensor and adds them to the buffer vectors.
		*/
		void refreshData();

		/*
			Returns an average wind direction value, depending on how many values that is in vector.
		*/
		float getWindDirection();

		/*
			Returns an average wind speed value, depending on how many values that is in vector.
		*/
		float getWindSpeed();

		/*
			Returns an average wind temperature value, depending on how many values that is in vector.
		*/
		float getWindTemperature();

	private:

		int m_fd;

		unsigned int m_bufferSize;

		vector<float> m_windDirection;
		vector<float> m_windSpeed;
		vector<float> m_windTemperature;

		/*
			This is called from the public getWind...() methods.
			Returns an average windData value of all values in the vector.
		*/
		float getAverageValue(vector<float> v);

};

#endif
