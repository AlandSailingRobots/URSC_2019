/*
 * I2C_Sender.h
 *
 *  Created on: 13.05.2019
 *      Author: pi
 */

#ifndef I2C_SENDER_H_
#define I2C_SENDER_H_

#define Rudder 0x04
#define Sail 0x05

void I2CSetup();
int I2CSendAngle(int SlaveAddr, int Angle_SP);

#endif /* I2C_SENDER_H_ */
