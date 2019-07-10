#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <linux/i2c-dev.h>
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>

int statecmps=1;
int fd;
unsigned int res=0;
int address = 0x60;
unsigned  char buf[10]={0};

void cmpsSetup(){
char *fileName=(char*)"/dev/i2c-1";
if((fd=open(fileName, O_RDWR))<0){
printf("Failed to open i2c port cmps \n");}
return;
}


int cmps()
{
if(statecmps==1){
		if (ioctl(fd, I2C_SLAVE, address) >= 0) {statecmps=2;}
		else{							// Set the port options and set the address of the device we wish to speak to
			printf("Unable to get bus access to talk to cmps\n");
			//continue;
			return res;
		}
		}
		
if(statecmps==2){buf[0] = 2;								// this is the register we wish to read from
		
		if ((write(fd, buf, 1)) == 1) {statecmps=3;}
			else{			// Send register to read from
			printf("Error writing to cmps\n");
			//continue;
			return res;
		}
}
if(statecmps==3){		
		if (read(fd, buf, 2) == 2) {statecmps=4;
			 if(buf[0] > 128){
                                buf[0] = buf[0] - 128;
                        }
                        unsigned char highByte = buf[0];
                        unsigned char lowByte = buf[1];
                        unsigned int result = (highByte <<8) + lowByte;                 // Calculate the bearing a$

                        res = result/10;
statecmps=1;
                        return res;


}
else{								// Read back data into buf[]
			printf("Unable to read from cmps\n");
			return res;
		}

		
	}
	return res;
}

