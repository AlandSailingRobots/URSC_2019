#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <cmath>
#include <iostream>
#include <cstdlib>
#include <string>
#include <cstring>
#include <cctype>
#include <thread>
#include <chrono>
#include "rpi_cmps12.h"
#include "position_logger.h"
#include "gps.h"
#include "pid.h"
#include "csv_log.h"
#include "mqtt/async_client.h"
#include "json.hpp"
#include "sail_lookup.h"
#include "I2C_Sender.h"

#define PI 3.14159265

using json = nlohmann::json;

// This application uses an MQTT subscriber using the C++ asynchronous client
// interface, employing callbacks to receive messages and status updates.

const std::string SERVER_ADDRESS("192.168.4.1");
const std::string CLIENT_ID("roboboatfinal_cpp");
const std::string TOPIC("weather");

const int	QOS = 1;

//	Enter desired buoy coordinates
int boyen = 1;
float ziel_latitude[4] = {60.1046976,60.1041240,60.1044711,60.1049135};
float ziel_longitude[4] = {19.9492564,19.9491522,19.9506844,19.9461270};

int alpha_boot;				// angle boat to north
float alpha_wind;
float alpha_wind_empfangen; // angle wind to north
int alpha_wind_boot;		// Delta alpha_wind to alpha_boot
double alpha_kursziel;		// angle boat to desired bearing
int alpha_wind_kursziel;	// Delta alpha_wind to alpha_kursziel
int alpha_boot_kursziel;

float latitude;
float longitude;
int latitude_vorkomma;
int longitude_vorkomma;
float latitude_nachkomma;
float longitude_nachkomma;
loc_t gps;
float delta_latitude;
float delta_longitude;
float cos_latitude;
float distance_boyen = 100;
int counter_boyen = 0;

int alpha_servo_ruder = 0;
int alpha_servo_segel = 0;

int sailangle;
float windspeed;

loc_t get_gps(){return gps;};

/////////////////////////////////////////////////////////////////////////////

// Callbacks for the success or failures of requested actions.
// This could be used to initiate further action, but here we just log the
// results to the console.

class action_listener : public virtual mqtt::iaction_listener
{
	std::string name_;

	void on_failure(const mqtt::token& tok) override {
		std::cout << name_ << " failure";
		if (tok.get_message_id() != 0)
			std::cout << " for token: [" << tok.get_message_id() << "]" << std::endl;
		std::cout << std::endl;
	}

	void on_success(const mqtt::token& tok) override  {
		std::cout << name_ << " success";
		if (tok.get_message_id() != 0)
			std::cout << " for token: [" << tok.get_message_id() << "]" << std::endl;
		auto top = tok.get_topics();
		if (top && !top->empty())
			std::cout << "\ttoken topic: '" << (*top)[0] << "', ..." << std::endl;
		std::cout << std::endl;
	}

public:
	action_listener(const std::string& name) : name_(name) {}
};

/////////////////////////////////////////////////////////////////////////////

/**
 * Local callback & listener class for use with the client connection.
 * This is primarily intended to receive messages, but it will also monitor
 * the connection to the broker. If the connection is lost, it will attempt
 * to restore the connection and re-subscribe to the topic.
 */

class callback : public virtual mqtt::callback,
					public virtual mqtt::iaction_listener

{
	// Counter for the number of connection retries
	int nretry_;
	// The MQTT client
	mqtt::async_client& cli_;
	// Options to use if we need to reconnect
	mqtt::connect_options& connOpts_;
	// An action listener to display the result of actions.
	action_listener subListener_;

	void reconnect() {
		std::this_thread::sleep_for(std::chrono::milliseconds(2500));
		try {
			cli_.connect(connOpts_, nullptr, *this);
		}
		catch (const mqtt::exception& exc) {
			std::cerr << "Error: " << exc.what() << std::endl;
			exit(1);
		}
	}

	// Re-connection failure
	void on_failure(const mqtt::token& tok) override {
		std::cout << "Connection attempt failed" << std::endl;
		reconnect();
	}

	// (Re)connection success
	// Either this or connected() can be used for callbacks.
	void on_success(const mqtt::token& tok) override {}

	// (Re)connection success
	void connected(const std::string& cause) override {
		std::cout << "\nConnection success" << std::endl;
		std::cout << "\nSubscribing to topic '" << TOPIC << "'\n"
			<< "\tfor client " << CLIENT_ID
			<< " using QoS" << QOS << "\n"
			<< "\nPress Q<Enter> to quit\n" << std::endl;

		cli_.subscribe(TOPIC, QOS, nullptr, subListener_);
	}

	// Callback for when the connection is lost.
	// This will initiate the attempt to manually reconnect.
	void connection_lost(const std::string& cause) override {
		std::cout << "\nConnection lost" << std::endl;
		if (!cause.empty())
			std::cout << "\tcause: " << cause << std::endl;

		std::cout << "Reconnecting..." << std::endl;
		nretry_ = 0;
		reconnect();
	}

	// Callback for when a message arrives.
	void message_arrived(mqtt::const_message_ptr msg) override {

		auto j = json::parse(msg->to_string());
		alpha_wind_empfangen = j["direction"];
		windspeed = j["speed"];

	}

	void delivery_complete(mqtt::delivery_token_ptr token) override {}

public:
	callback(mqtt::async_client& cli, mqtt::connect_options& connOpts)
				: nretry_(0), cli_(cli), connOpts_(connOpts), subListener_("Subscription") {}
};

/////////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[])
{
	mqtt::connect_options connOpts;
	connOpts.set_keep_alive_interval(20);
	connOpts.set_clean_session(true);

	mqtt::async_client client(SERVER_ADDRESS, CLIENT_ID);

	callback cb(client, connOpts);
	client.set_callback(cb);
	I2CSetup();
	cmpsSetup();

	// Start the connection.
	// When completed, the callback will subscribe to topic.

	client.connect(connOpts, nullptr, cb);

	while (1){

		alpha_boot = cmps();

		if(alpha_boot > 180){
			alpha_boot = alpha_boot - 360;
		}
		printf("w_boot: %d   ", alpha_boot);
		alpha_wind=-160.0;
		windspeed = 1.0F;

		if(alpha_wind >= 180.0f){
			alpha_wind -=360.0f;
		}

		gps = position_log();
		
		latitude = gps.latitude;
		longitude = gps.longitude;

		printf("lat: %2.6f   long: %2.6f   ", latitude, longitude);

		alpha_wind_boot = alpha_wind - alpha_boot;

		if(alpha_wind_boot > 180){
			alpha_wind_boot -= 360;
		}
		if(alpha_wind_boot < -180){
			alpha_wind_boot += 360;
		}

		cos_latitude = latitude * PI /180;
		delta_longitude = 111.3 * cos(cos_latitude) * (ziel_longitude[counter_boyen] - longitude);
		delta_latitude = 111.3 * (ziel_latitude[counter_boyen] - latitude);
		distance_boyen = sqrt(delta_longitude * delta_longitude + delta_latitude * delta_latitude);
		float distance_boyen_meter = distance_boyen*1000;

		printf("dis: %4.1f   ", distance_boyen_meter);
		//	Condition that boat is close enough to the aimed buoy
		if(distance_boyen < 0.005) {
			counter_boyen = counter_boyen + 1;
			distance_boyen = 100;
		}

		if(counter_boyen == boyen){
			counter_boyen = 0;

		}
		printf("ctr: %d   ", counter_boyen);

		alpha_kursziel = atan(delta_longitude/delta_latitude); //Quadrant 1
		alpha_kursziel =  alpha_kursziel * 180 / PI;	//rad to deg

		if(delta_latitude<0 && delta_longitude<0){
			alpha_kursziel = alpha_kursziel - 180; //Quadrant 3
		}else if(delta_latitude<0 && delta_longitude>=0) {
			alpha_kursziel = alpha_kursziel + 180;
		}

		alpha_wind_kursziel = alpha_wind - alpha_kursziel;
		if(alpha_wind_kursziel > 180){
			alpha_wind_kursziel -= 360;
		}
		if(alpha_wind_kursziel < -180){
			alpha_wind_kursziel += 360;
		}

		alpha_boot_kursziel = alpha_boot - alpha_kursziel;
		if(alpha_boot_kursziel > 180){
			alpha_boot_kursziel -= 360;
		}
		if(alpha_boot_kursziel < -180){
			alpha_boot_kursziel += 360;
		}

		//Rudder Control

		alpha_servo_ruder = pid_run(alpha_boot_kursziel);
		sailangle = get_sailangle(alpha_wind_kursziel, windspeed);

		I2CSendAngle(Rudder,alpha_servo_ruder);
		I2CSendAngle(Sail, sailangle);

		logging(longitude, latitude, distance_boyen, counter_boyen);
	}

 	return 0;
}


