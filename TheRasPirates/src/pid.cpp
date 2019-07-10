#ifndef _PID_SOURCE_
#define _PID_SOURCE_

#include <iostream>
#include <cmath>
#include "pid.h"

using namespace std;

class PIDImpl
{
    public:
        PIDImpl(double dt, double max, double min, double Kp, double Kd, double Ki);
        ~PIDImpl();
        double calculate(double setpoint, double pv);

    private:
        double dt;
        double max;
        double min;
        double Kp;
        double Kd;
        double Ki;
        double pre_error;
        double integral;

};


PID::PID(double dt, double max, double min, double Kp, double Kd, double Ki)
{
    pimpl = new PIDImpl(dt,max,min,Kp,Kd,Ki);
}


double PID::calculate(double setpoint, double pv)
{
    return pimpl->calculate(setpoint,pv);
}


double PID::normalize(double angle)
{
	//normalize
	if(angle > 180) {
		angle -= 360;
	}
	else if(angle <= -180) {
		angle += 360;
	}

	return angle;
}

PID::~PID() 
{
    delete pimpl;
}



/***	Implementation	***/

PIDImpl::PIDImpl(double dt, double max, double min, double Kp, double Kd, double Ki) :
    dt(dt),
    max(max),
    min(min),
    Kp(Kp),
    Kd(Kd),
    Ki(Ki),
    pre_error(0),
    integral(0)
{
}

double PIDImpl::calculate(double setpoint, double pv)
{

    // Calculate error
    double error = setpoint - pv;
    cout << "error: " << error << endl;

    // Proportional term
    double Pout = Kp * error;

    // Integral term
    integral += error * dt;
    double Iout = Ki * integral;

    // Derivative term
    double derivative = (error - pre_error) / dt;
    double Dout = Kd * derivative;

    // Calculate total output
    double output = Pout + Iout + Dout;

    // Restrict to max/min
    if(output > max)
        output = max;
    else if(output < min)
        output = min;

    // Save error to previous error
    pre_error = error;

    return output;
}

PIDImpl::~PIDImpl()
{
}

#endif
