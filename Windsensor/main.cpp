#include <iostream>
#include <cstdlib>
#include <string>
#include <map>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <ctime>
#include <locale>

#include "mqtt/client.h"
#include "json.hpp"
#include "CV7.h"

using namespace std;
using json = nlohmann::json;

//MQTT Connection
const string SERVER_ADDRESS{"http:addresses here and the port number"};
const string USERNAME = "the username to log in";
const string PASSWORD = "and password ";
const string CLIENT_ID = "The ID for broker to know who is publishing the message";
const string TOPIC = "Whatever topic you like to have";
const int QOS = 1;

//CV7 WindSensor
const string PortName = "/dev/ttyAMA0";
const int baudRate = 4800;


class sample_mem_persistence : virtual public mqtt::iclient_persistence
{
	// Whether the store is open
	bool open_;

	// Use an STL map to store shared persistence pointers
	// against string keys.
	std::map<std::string, std::string> store_;

public:
	sample_mem_persistence() : open_(false) {}

	// "Open" the store
	void open(const std::string& clientId, const std::string& serverURI) override {
		std::cout << "[Opening persistence store for '" << clientId
			<< "' at '" << serverURI << "']" << std::endl;
		open_ = true;
	}

	bool getValue_open(){
		return open_;
	}

	// Close the persistent store that was previously opened.
	void close() override {
		std::cout << "[Closing persistence store.]" << std::endl;
		open_ = false;
	}

	// Clears persistence, so that it no longer contains any persisted data.
	void clear() override {
		std::cout << "[Clearing persistence store.]" << std::endl;
		store_.clear();
	}

	// Returns whether or not data is persisted using the specified key.
	bool contains_key(const std::string &key) override {
		return store_.find(key) != store_.end();
	}

	// Returns the keys in this persistent data store.
	const mqtt::string_collection& keys() const override {
		static mqtt::string_collection ks;
		ks.clear();
		for (const auto& k : store_)
			ks.push_back(k.first);
		return ks;
	}

	// Puts the specified data into the persistent store.
	void put(const std::string& key, const std::vector<mqtt::string_view>& bufs) override {
		/*std::cout << "[Persisting data with key '"
			<< key << "']" << std::endl;*/
		std::string str;
		for (const auto& b : bufs)
			str += b.str();
		store_[key] = std::move(str);
	}

	// Gets the specified data out of the persistent store.
	mqtt::string_view get(const std::string& key) const override {
		std::cout << "[Searching persistence for key '"
			<< key << "']" << std::endl;
		auto p = store_.find(key);
		if (p == store_.end())
			throw mqtt::persistence_exception();
		std::cout << "[Found persistence data for key '"
			<< key << "']" << std::endl;

		return mqtt::string_view(p->second);
	}

	// Remove the data for the specified key.
	void remove(const std::string &key) override {
		//std::cout << "[Persistence removing key '" << key << "']" << std::endl;
		auto p = store_.find(key);
		if (p == store_.end())
			throw mqtt::persistence_exception();
		store_.erase(p);
		//std::cout << "[Persistence kclient.connect(connOpts);ey removed '" << key << "']" << std::endl;
	}
};

/////////////////////////////////////////////////////////////////////////////
// Class to receive callbacks

class user_callback : public virtual mqtt::callback
{
	void connection_lost(const std::string& cause) override {
		std::cout << "\nConnection lost" << std::endl;
		if (!cause.empty())
			std::cout << "\tcause: " << cause << std::endl;
	}

	void delivery_complete(mqtt::delivery_token_ptr tok) override {
		std::cout << "\n\t[Delivery complete for token: "
			<< (tok ? tok->get_message_id() : -1) << "]" << std::endl;
	}

public:
};


int main(){
    int a = 0;
    CV7 sensor;
    sample_mem_persistence persist;
		cout<< "open_ value: "<<persist.getValue_open()<<endl;
    mqtt::client client(SERVER_ADDRESS,CLIENT_ID,&persist);
    user_callback cb;
    client.set_callback(cb);
		cout<< "open_ value: "<<persist.getValue_open()<<endl;

    mqtt::connect_options connOpts(USERNAME, PASSWORD);
    connOpts.set_keep_alive_interval(20);
    connOpts.set_clean_session(true);
    client.connect(connOpts);
    try{
        sensor.loadConfig(PortName,baudRate);
    }catch(const char* exception){
        cout<< exception << endl;
    }

    int speed, direction;
		char mstr[100];
	  time_t t;
	  struct tm* tmp;
	 	const char* fmt ="%Y-%m-%d %H:%M:%SZ";

    while(1){
            usleep(1000000);
            sensor.refreshData();
            direction = sensor.getWindDirection();
            speed = sensor.getWindSpeed();
						t = time(NULL);
				    tmp = gmtime(&t);
						strftime(mstr,sizeof(mstr),fmt,tmp);
						json jPackage;
	          jPackage["speed"] = speed;
	          jPackage["direction"] = direction;
	          jPackage["timestamp"] = mstr;
						cout<< jPackage.dump(2)<<endl;
	          client.publish(mqtt::message(TOPIC,jPackage.dump(),QOS,false));
    }
		client.disconnect();

    return 0;
}
