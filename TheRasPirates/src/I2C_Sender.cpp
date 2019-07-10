#define Rudder 0x04
#define Sail 0x05

#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <math.h>
#include <cmath>
#include <iostream>


#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>

#include <unistd.h>				//Needed for I2C port
#include <fcntl.h>				//Needed for I2C port

#define PI 3.14159265

int file_i2c;
int length;
signed int buffer[60] = {0};
float lc = 250.0f;
float lr = 17.5f;

void I2CSetup(){

			//----- OPEN THE I2C BUS -----
			char *filename = (char*)"/dev/i2c-1";
			if ((file_i2c = open(filename, O_RDWR)) < 0)
			{
				//ERROR HANDLING: you can check error to see what went wrong
				printf("Failed to open the i2c bus");
				//return 0;
			}
return;


}


int I2CSendAngle(int SlaveAddr, int Angle_SP){

	if (ioctl(file_i2c, I2C_SLAVE, SlaveAddr) < 0)
		{
			printf("Failed to acquire bus access and/or talk to slave");
			printf(SlaveAddr+"\n");

			//ERROR HANDLING; you can check error to see what went wrong
			return 1;
		}

	if(SlaveAddr==Sail){
	float Angle_SP_f = Angle_SP;
	float sum1 = pow((sin(Angle_SP_f*PI/180.0f)*lc),2);
	float sum2 = pow(310.0f-lc*(cos(Angle_SP_f*PI/180.0f)),2);
	float mul1 = 18.0f/(2*PI*lr);
	unsigned int Angle_out=sqrt(sum1+sum2)*mul1+50;

	buffer[0] = (unsigned char)Angle_out;

	}
	else{
	buffer[0] = (unsigned char)(Angle_SP+90);}
	length = 1;			//<<< Number of bytes to write
	if (write(file_i2c, buffer, length) != length)		//write() returns the number of bytes actually written, if it doesn't match then an error occurred (e.g. no response from the device)
	{
		/* ERROR HANDLING: i2c transaction failed */
		printf("Failed to write to the i2c bus.\n");
		return 1;
	}

	return 1;
}
