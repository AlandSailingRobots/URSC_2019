#include "pid.h"
#include <stdio.h>
#include <chrono>
#include <tgmath.h>
#include <iostream>

using namespace std;

bool delta_flag = false;
int pid_out = 0;
int setpoint = 0;
int delta_alpha_kursziel = 0;
int new_alpha_kursziel = 0;
int old_alpha_kursziel = 0;

int pid_run(int alpha_kursziel) {

	for(int i = 0; i < 100; i++){
		PID pid = PID(0.2, 45, -45, 0.5, 0.01, 0.05);										// dt, max, min, Kp, Kd, Ki
		alpha_kursziel = pid.normalize(alpha_kursziel);										// change value range from 0...360 to -179...180
		pid_out = pid.calculate(setpoint, alpha_kursziel);

		return pid_out;
	}
	return pid_out;
}
