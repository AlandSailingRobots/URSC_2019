/*
 * serial.h
 *
 *  Created on: May 1, 2019
 *      Author: ubuntu
 */

#ifndef SERIAL_H_
#define SERIAL_H_

#ifndef _SERIAL_H_
#define _SERIAL_H_

#include <inttypes.h>

#ifndef PORTNAME
#define PORTNAME "/dev/ttyACM0" //ttyACM0
#endif

void serial_init(void);
void serial_config(void);
void serial_println(const char *, int);
void serial_readln(char *, int);
void serial_close(void);

#endif

#endif /* SERIAL_H_ */
